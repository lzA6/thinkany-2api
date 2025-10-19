import threading
from cachetools import TTLCache
from typing import List, Dict, Any, Optional
from app.core.config import settings
from loguru import logger

class SessionManager:
    def __init__(self):
        self.cache = TTLCache(maxsize=1024, ttl=settings.SESSION_CACHE_TTL)
        self.lock = threading.Lock()
        logger.info(f"会话管理器已初始化，缓存 TTL: {settings.SESSION_CACHE_TTL} 秒。")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            return self.cache.get(session_id)

    def update_session(self, session_id: str, data: Dict[str, Any]):
        with self.lock:
            self.cache[session_id] = data
            logger.debug(f"会话 {session_id} 已更新。")

    def get_openai_compatible_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """将内部存储的消息格式转换为 OpenAI API 所需的格式。"""
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages if "role" in msg and "content" in msg]
