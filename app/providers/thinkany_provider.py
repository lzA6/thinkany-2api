import json
import time
import uuid
import threading
from typing import Dict, Any, AsyncGenerator, List, Optional

import cloudscraper
from fastapi import HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from loguru import logger

from app.core.config import settings
from app.providers.base_provider import BaseProvider
from app.services.session_manager import SessionManager
from app.utils.sse_utils import create_sse_data, create_chat_completion_chunk, DONE_CHUNK

class ThinkanyProvider(BaseProvider):
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.session_manager = SessionManager()
        self.cookie_index = 0
        self.cookie_lock = threading.Lock()

    def _get_cookie(self) -> str:
        with self.cookie_lock:
            cookie = settings.THINKANY_COOKIES[self.cookie_index]
            self.cookie_index = (self.cookie_index + 1) % len(settings.THINKANY_COOKIES)
            return cookie

    async def chat_completion(self, request_data: Dict[str, Any]) -> StreamingResponse:
        session_id = request_data.get("user", f"session-{uuid.uuid4()}")
        messages = request_data.get("messages", [])
        
        # [修改] 根据用户请求的模型，从配置中获取真实模型名称和模式
        user_model = request_data.get("model", settings.DEFAULT_MODEL)
        model_info = settings.MODEL_MAPPING.get(user_model)
        if not model_info:
            raise HTTPException(status_code=400, detail=f"不支持的模型: {user_model}。请从 /v1/models 接口获取可用模型列表。")
        
        actual_model, mode = model_info

        session_data = self.session_manager.get_session(session_id)
        
        # [修改] 修正会话判断逻辑，确保能正确处理新旧会话
        conv_uuid = session_data.get("conv_uuid") if session_data else None
        is_new_conversation = not conv_uuid

        # [修复] 为新会话主动生成 conv_uuid
        if is_new_conversation:
            conv_uuid = f"m-{uuid.uuid4().hex[:12]}" # 模仿官网格式生成
            logger.info(f"新会话 {session_id}，已生成 conv_uuid: {conv_uuid}")


        async def stream_generator() -> AsyncGenerator[bytes, None]:
            request_id = f"chatcmpl-{uuid.uuid4()}"
            
            # [新增] 用于控制 Markdown 输出的几个状态变量
            sent_search_process = False
            sent_sources = False
            sent_answer_header = False
            
            try:
                payload = self._prepare_payload(messages, actual_model, conv_uuid, is_new_conversation, mode)
                headers = self._prepare_headers()
                
                logger.info(f"向 ThinkAny 发送请求, 会话: {session_id}, 模式: {mode}, 新对话: {is_new_conversation}")
                logger.debug(f"请求 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

                response = self.scraper.post(
                    "https://thinkany.ai/api/chat/completions",
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=settings.API_REQUEST_TIMEOUT
                )
                
                logger.info(f"ThinkAny 返回状态码: {response.status_code}")
                response.raise_for_status()

                full_response_content = ""
                
                logger.info("开始接收并处理来自 ThinkAny 的 SSE 数据流...")
                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    line_str = line.decode('utf-8', errors='ignore')
                    logger.debug(f"原始 SSE 数据行: {line_str}")

                    if not line_str.startswith("data:"):
                        # 有时错误信息不是以 'data:' 开头，直接就是 json
                        try:
                            error_data = json.loads(line_str)
                            if error_data.get("code") == -1:
                                logger.error(f"ThinkAny API 返回业务错误: {error_data.get('message')}")
                                break # 终止流
                        except json.JSONDecodeError:
                            continue # 忽略无法解析的非 data 行
                        
                    content_str = line_str[len("data:"):].strip()
                    if not content_str or content_str == "[DONE]":
                        continue
                        
                    try:
                        data = json.loads(content_str)
                        obj_type = data.get("object")

                        # --- 1. 处理 stream.event (用于搜索过程和来源) ---
                        if obj_type == "stream.event" and mode == "search":
                            msg = data.get("metadata", {}).get("msg", {})
                            
                            # 提取搜索过程
                            questions = msg.get("questions")
                            if questions and not sent_search_process:
                                md_content = "### 搜索过程\n" + "\n".join(f"- {q}" for q in questions) + "\n\n"
                                chunk = create_chat_completion_chunk(request_id, user_model, md_content)
                                yield create_sse_data(chunk)
                                sent_search_process = True

                            # 提取来源
                            rag_results = msg.get("rag_results")
                            if rag_results and not sent_sources:
                                md_content = "### 来源\n"
                                for i, res in enumerate(rag_results, 1):
                                    md_content += f"{i}. {res.get('title', '未知标题')} [<sup>1</sup>]({res.get('link', '#')}) - *{res.get('source', '未知来源')}*\n"
                                md_content += "\n"
                                chunk = create_chat_completion_chunk(request_id, user_model, md_content)
                                yield create_sse_data(chunk)
                                sent_sources = True
                            continue

                        # --- 2. 处理 chat.completion.chunk (用于最终答案) ---
                        elif obj_type == "chat.completion.chunk":
                            if not sent_answer_header:
                                header_content = "### 答案\n"
                                chunk = create_chat_completion_chunk(request_id, user_model, header_content)
                                yield create_sse_data(chunk)
                                sent_answer_header = True

                            delta_content = data.get("choices", [{}])[0].get("delta", {}).get("content")
                            if delta_content:
                                full_response_content += delta_content
                                chunk = create_chat_completion_chunk(request_id, user_model, delta_content)
                                yield create_sse_data(chunk)
                        else:
                            logger.debug(f"跳过其他类型的 SSE 对象: {obj_type}")

                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        logger.warning(f"解析或处理 SSE 数据块时跳过: {e}, 内容: {content_str}")
                        continue
                
                logger.info("ThinkAny 的 SSE 数据流处理完毕。")
                
                # 更新会话上下文
                updated_messages = self.session_manager.get_session(session_id).get("messages", []) if self.session_manager.get_session(session_id) else []
                updated_messages.extend(messages)
                updated_messages.append({"role": "assistant", "content": full_response_content})
                self.session_manager.update_session(session_id, {"conv_uuid": conv_uuid, "messages": updated_messages})
                logger.info(f"会话 {session_id} 已更新，包含新的上下文。")

                final_chunk = create_chat_completion_chunk(request_id, user_model, "", "stop")
                yield create_sse_data(final_chunk)
                yield DONE_CHUNK

            except Exception as e:
                logger.error(f"处理流时发生严重错误: {e}", exc_info=True)
                error_chunk = create_chat_completion_chunk(request_id, user_model, f"内部服务器错误: {str(e)}", "stop")
                yield create_sse_data(error_chunk)
                yield DONE_CHUNK

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    def _prepare_headers(self) -> Dict[str, str]:
        return {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "Cookie": self._get_cookie(),
            "Origin": "https://thinkany.ai",
            "Referer": "https://thinkany.ai/zh",
        }

    def _prepare_payload(self, messages: List[Dict[str, Any]], actual_model: str, conv_uuid: str, is_new: bool, mode: str) -> Dict[str, Any]:
        last_user_message = messages[-1]["content"]
        
        action = f"{'init' if is_new else 'append'}_{mode}"

        payload = {
            "conv_uuid": conv_uuid,
            "uuid": str(uuid.uuid4()),
            "role": "user",
            "content": last_user_message,
            "llm_model": actual_model,
            "locale": "zh",
            "mode": mode,
            "source": "all",
            "action": action
        }
        
        if is_new:
            payload["target_msg_uuid"] = ""
        else:
            # 获取除了最后一条用户消息之外的所有历史记录
            session_data = self.session_manager.get_session(conv_uuid) # 使用 conv_uuid 作为 session_id
            history = session_data.get("messages", []) if session_data else []
            payload["ctx_msgs"] = self.session_manager.get_openai_compatible_messages(history)

        return payload

    async def get_models(self) -> JSONResponse:
        # [修改] 返回新的模型列表
        return JSONResponse(content={
            "object": "list",
            "data": [{"id": name, "object": "model", "created": int(time.time()), "owned_by": "lzA6"} for name in settings.MODEL_MAPPING.keys()]
        })
