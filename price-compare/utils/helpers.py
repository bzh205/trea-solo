"""辅助工具函数"""
import random
import re


# 常用 User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def random_user_agent() -> str:
    """返回随机 User-Agent"""
    return random.choice(USER_AGENTS)


def random_delay(min_sec: float = 1.0, max_sec: float = 3.0) -> float:
    """返回随机延迟秒数"""
    return random.uniform(min_sec, max_sec)


def clean_text(text: str) -> str:
    """清理文本：去除多余空白、换行等"""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", str(text))
    return text.strip()


def truncate(text: str, length: int = 50) -> str:
    """截断文本到指定长度"""
    if not text:
        return ""
    return text[:length] + "..." if len(text) > length else text
