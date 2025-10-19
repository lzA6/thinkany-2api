import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )

    APP_NAME: str = "thinkany-2api"
    APP_VERSION: str = "1.0.1" # 版本号升级
    DESCRIPTION: str = "一个将 thinkany.ai 转换为兼容 OpenAI 格式 API 的高性能代理，支持多账号、有状态上下文、以及 search/chat 模式。"

    API_MASTER_KEY: Optional[str] = None
    
    THINKANY_COOKIES: List[str] = []

    API_REQUEST_TIMEOUT: int = 180
    NGINX_PORT: int = 8088
    SESSION_CACHE_TTL: int = 3600

    # [修改] 重新定义模型列表，用于区分 search 和 chat 模式
    # 用户通过选择不同的模型名称来决定使用哪种模式
    # 格式: "用户看到的模型名": ["thinkany后端接受的模型名", "模式"]
    MODEL_MAPPING: Dict[str, List[str]] = {
        "thinkany-search-gpt4o-mini": ["gpt-4o-mini", "search"],
        "thinkany-chat-gpt4o-mini": ["gpt-4o-mini", "chat"],
        "thinkany-search-gemini-flash": ["gemini-flash-1.5", "search"],
        "thinkany-chat-gemini-flash": ["gemini-flash-1.5", "chat"],
        "thinkany-search-haiku": ["claude-3-haiku", "search"],
        "thinkany-chat-haiku": ["claude-3-haiku", "chat"],
    }
    # 废弃旧的模型列表
    # KNOWN_MODELS: Dict[str, str] = {
    #     "gpt-4o-mini": "gpt-4o-mini",
    #     "claude-3-haiku": "claude-3-haiku",
    #     "gemini-flash-1.5": "gemini-flash-1.5"
    # }
    DEFAULT_MODEL: str = "thinkany-search-gpt4o-mini"

    def __init__(self, **values):
        super().__init__(**values)
        # 从环境变量 THINKANY_COOKIE_1, THINKANY_COOKIE_2, ... 加载 cookies
        i = 1
        while True:
            cookie_str = os.getenv(f"THINKANY_COOKIE_{i}")
            if cookie_str:
                self.THINKANY_COOKIES.append(cookie_str)
                i += 1
            else:
                break
        
        if not self.THINKANY_COOKIES:
            raise ValueError("必须在 .env 文件中至少配置一个有效的 THINKANY_COOKIE_1")

settings = Settings()
