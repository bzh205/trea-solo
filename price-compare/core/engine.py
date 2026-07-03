"""核心编排模块 - 整合爬虫、处理、分析流程"""
import asyncio
from typing import List, Dict, Any, Optional

from models.product import Product
from scrapers import SCRAPERS
from processors.cleaner import DataCleaner
from processors.deduplicator import Deduplicator
from analyzers.comparator import Comparator
from analyzers.recommender import Recommender
from analyzers.visualizer import Visualizer


class PriceCompareEngine:
    """价格采集对比引擎"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.cleaner = DataCleaner()
        self.deduplicator = Deduplicator()
        self.comparator = Comparator()
        self.recommender = Recommender()
        self.visualizer = Visualizer()

    async def run(
        self,
        keyword: str,
        platforms: Optional[List[str]] = None,
        max_items: int = 20,
    ) -> Dict[str, Any]:
        """执行完整采集对比流程"""
        if platforms is None:
            platforms = list(SCRAPERS.keys())

        # 1. 爬虫采集（并发）
        products = await self._crawl(keyword, platforms, max_items)

        # 2. 数据清洗
        products = self.cleaner.clean(products)

        # 3. 去重
        products = self.deduplicator.deduplicate(products)

        # 4. 按价格升序排序
        products.sort(key=lambda p: p.price)

        # 5. 分析
        comparison = self.comparator.compare(products)
        recommendations = self.recommender.recommend(products)
        charts = self.visualizer.generate_chart_data(products)

        return {
            "keyword": keyword,
            "total_count": len(products),
            "products": [p.to_dict() for p in products],
            "comparison": comparison,
            "recommendations": recommendations,
            "charts": charts,
        }

    async def _crawl(
        self, keyword: str, platforms: List[str], max_items: int
    ) -> List[Product]:
        """并发执行多平台爬虫"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise RuntimeError("Playwright 未安装，请运行: pip install playwright && playwright install chromium")

        all_products = []
        async with async_playwright() as p:
            # 检测浏览器是否可用
            try:
                browser = await p.chromium.launch(headless=True)
                await browser.close()
            except Exception as e:
                raise RuntimeError(
                    f"Chromium 浏览器未安装或无法启动。\n"
                    f"错误详情: {e}\n"
                    f"请运行以下命令安装浏览器:\n"
                    f"  playwright install chromium\n"
                    f"如果下载缓慢，可尝试:\n"
                    f"  PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright python -m playwright install chromium"
                )

            tasks = []
            for plat in platforms:
                if plat not in SCRAPERS:
                    continue
                scraper = SCRAPERS[plat](max_items=max_items, headless=self.headless)
                await scraper._setup_browser(p)
                tasks.append(self._safe_search(scraper, keyword))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    all_products.extend(result)
                elif isinstance(result, Exception):
                    print(f"[采集异常] {result}")

        return all_products

    async def _safe_search(self, scraper, keyword: str) -> List[Product]:
        """安全执行搜索，确保资源释放"""
        try:
            return await scraper.search(keyword)
        except Exception as e:
            print(f"[{scraper.platform}] 采集异常: {e}")
            return []
        finally:
            await scraper.close()
