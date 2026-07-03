"""爬虫基类 - 提供反爬策略和通用采集流程"""
import asyncio
import random
from abc import ABC, abstractmethod
from typing import List

from models.product import Product
from utils.helpers import random_user_agent, random_delay


class BaseScraper(ABC):
    """爬虫基类：定义通用接口和反爬策略"""

    platform: str = "base"
    search_url: str = ""

    # 反爬标识
    BLOCKED_KEYWORDS = ["登录", "登录注册", "请输入", "Access Denied", "验证", "captcha", "滑动验证"]

    def __init__(self, max_items: int = 20, headless: bool = True):
        self.max_items = max_items
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

    async def _setup_browser(self, playwright):
        """配置浏览器上下文（反爬策略：随机UA + 指纹）"""
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent=random_user_agent(),
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
            java_script_enabled=True,
        )
        self.page = await self.context.new_page()

    async def _is_blocked(self) -> bool:
        """检测页面是否被反爬拦截（登录墙/验证等）"""
        try:
            title = await self.page.title()
            url = self.page.url
            # URL 包含登录
            if any(k in url.lower() for k in ["login", "passport", "verify"]):
                return True
            # 标题包含登录
            if any(k in title for k in self.BLOCKED_KEYWORDS):
                return True
            return False
        except Exception:
            return False

    async def _navigate_and_wait(self, url: str, wait_selector: str = None, timeout: int = 10000):
        """导航到页面并等待加载"""
        await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
        if wait_selector:
            try:
                await self.page.wait_for_selector(wait_selector, timeout=timeout)
            except Exception:
                pass  # 等待选择器超时不算错误
        await asyncio.sleep(random_delay(0.5, 1.5))

    @abstractmethod
    async def _parse_page(self, keyword: str) -> List[Product]:
        """解析页面 - 子类必须实现"""
        ...

    async def search(self, keyword: str) -> List[Product]:
        """搜索采集主流程"""
        try:
            products = await self._parse_page(keyword)
            if not products:
                return []
            return products[: self.max_items]
        except Exception as e:
            print(f"[{self.platform}] 采集失败: {str(e)[:80]}")
            return []

    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            self.browser = None

    @staticmethod
    def parse_price(text: str) -> float:
        """从文本中解析价格"""
        import re
        if not text:
            return 0.0
        match = re.search(r"(\d+\.?\d*)", str(text).replace(",", ""))
        return float(match.group(1)) if match else 0.0

    @staticmethod
    def parse_sales(text: str) -> int:
        """从文本中解析销量（支持 '万' '万+' 等中文单位）"""
        import re
        if not text:
            return 0
        text = str(text)
        wan_match = re.search(r"(\d+\.?\d*)\s*万", text)
        if wan_match:
            return int(float(wan_match.group(1)) * 10000)
        wan_plus = re.search(r"(\d+\.?\d*)万\+", text)
        if wan_plus:
            return int(float(wan_plus.group(1)) * 10000)
        match = re.search(r"(\d+)", text)
        return int(match.group(1)) if match else 0
