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

    async def _navigate_and_wait(self, url: str, wait_selector: str = None):
        """导航到页面并等待加载"""
        await self.page.goto(url, wait_until="domcontentloaded")
        if wait_selector:
            await self.page.wait_for_selector(wait_selector, timeout=10000)
        await asyncio.sleep(random_delay(1, 3))

    @abstractmethod
    async def _parse_page(self, keyword: str) -> List[Product]:
        """解析页面 - 子类必须实现"""
        ...

    async def search(self, keyword: str) -> List[Product]:
        """搜索采集主流程"""
        try:
            products = await self._parse_page(keyword)
            return products[: self.max_items]
        except Exception as e:
            print(f"[{self.platform}] 采集失败: {e}")
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
        # 处理 "万" 单位
        wan_match = re.search(r"(\d+\.?\d*)\s*万", text)
        if wan_match:
            return int(float(wan_match.group(1)) * 10000)
        # 处理 "万+"
        wan_plus = re.search(r"(\d+\.?\d*)万\+", text)
        if wan_plus:
            return int(float(wan_plus.group(1)) * 10000)
        # 普通数字
        match = re.search(r"(\d+)", text)
        return int(match.group(1)) if match else 0
