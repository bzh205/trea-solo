"""核心编排模块 - 整合爬虫、处理、分析流程"""
import asyncio
import random
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
        products, is_simulated = await self._crawl(keyword, platforms, max_items)

        # 2. 数据清洗
        products = self.cleaner.clean(products)

        # 3. 去重（模拟数据跳过去重，避免模板相似被误删）
        if not is_simulated:
            products = self.deduplicator.deduplicate(products)

        # 4. 按价格升序排序
        products.sort(key=lambda p: p.price)

        # 5. 分析
        comparison = self.comparator.compare(products)
        recommendations = self.recommender.recommend(products)
        charts = self.visualizer.generate_chart_data(products)

        result = {
            "keyword": keyword,
            "total_count": len(products),
            "products": [p.to_dict() for p in products],
            "comparison": comparison,
            "recommendations": recommendations,
            "charts": charts,
        }

        if is_simulated:
            result["note"] = "【模拟数据】当前环境因反爬限制无法获取真实数据，展示的是基于关键词生成的模拟数据。在本地或非反爬严格环境下，工具会自动从京东/淘宝/拼多多采集真实价格。"
            result["is_simulated"] = True

        return result

    async def _crawl(
        self, keyword: str, platforms: List[str], max_items: int
    ) -> tuple[List[Product], bool]:
        """并发执行多平台爬虫，浏览器不可用时回退到模拟数据"""
        # 检查 Playwright 是否可用
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("[Engine] Playwright 未安装，使用模拟数据")
            return self._generate_mock_data(keyword, platforms, max_items), True

        # 检查浏览器是否能启动
        browser_available = False
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                await browser.close()
                browser_available = True
        except Exception as e:
            print(f"[Engine] 浏览器无法启动: {e}")
            print("[Engine] 使用模拟数据")

        if not browser_available:
            return self._generate_mock_data(keyword, platforms, max_items), True

        # 浏览器可用，执行真实采集
        all_products = []
        async with async_playwright() as p:
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

        # 如果真实采集完全失败（被反爬），回退到模拟数据
        if not all_products:
            print("[Engine] 所有平台均被反爬拦截，使用模拟数据补充")
            return self._generate_mock_data(keyword, platforms, max_items), True

        # 真实采集到部分数据，补充模拟数据以保证有足够对比样本
        if len(all_products) < 6:
            print(f"[Engine] 真实采集仅获取 {len(all_products)} 条，补充模拟数据")
            mock_data = self._generate_mock_data(keyword, platforms, max_items)
            # 避免重复
            existing_titles = {p.title for p in all_products}
            for p in mock_data:
                if p.title not in existing_titles:
                    all_products.append(p)
            return all_products, True

        return all_products, False

    async def _safe_search(self, scraper, keyword: str) -> List[Product]:
        """安全执行搜索，确保资源释放"""
        try:
            return await scraper.search(keyword)
        except Exception as e:
            print(f"[{scraper.platform}] 采集异常: {e}")
            return []
        finally:
            await scraper.close()

    def _generate_mock_data(
        self, keyword: str, platforms: List[str], max_items: int
    ) -> List[Product]:
        """生成模拟数据（浏览器不可用时使用）"""
        templates = [
            "{brand}{keyword}{adj1}{adj2}",
            "{brand}{keyword}{adj1}{adj3}",
            "2024新款{brand}{keyword}{adj2}",
            "{brand}{keyword}{adj3}{adj4}",
            "{brand}{keyword}{adj1}{adj2}{adj3}",
            "正品{brand}{keyword}{adj4}",
            "{brand}{keyword}{adj2}{adj5}",
            "热销{brand}{keyword}{adj1}",
            "{brand}{keyword}{adj3}{adj5}{adj6}",
            "特价{brand}{keyword}{adj4}{adj6}",
        ]
        adjectives = ["真无线", "主动降噪", "入耳式", "运动防水", "高音质", "蓝牙5.3", "超长续航", "游戏低延迟", "迷你隐形", "商务旗舰", "HiFi音质", "Type-C快充", "触控操作", "IPX7防水"]
        brands = ["", "品牌", "知名品牌", "京东自营", "国际大牌", "国货", "旗舰款", "官方正品", "畅销款", "限量款"]
        shops = {
            "jd": ["京东自营", "品牌旗舰店", "数码专营店", "国际旗舰店", "京东超市", "京东家电"],
            "taobao": ["淘小宝数码", "声美专营店", "天籁之音", "尊享数码", "旗舰音响", "淘宝精选"],
            "pdd": ["数码专营店", "国货数码旗舰", "极客数码", "迷你数码馆", "全民数码", "百亿补贴店"],
        }
        urls = {
            "jd": "https://search.jd.com/Search?keyword=",
            "taobao": "https://s.taobao.com/search?q=",
            "pdd": "https://mobile.yangkeduo.com/search_result.html?search_key=",
        }

        products = []
        items_per_platform = max(6, min(max_items // len(platforms), 10))

        for plat in platforms:
            price_ranges = {"pdd": (19, 129), "taobao": (39, 199), "jd": (79, 599)}
            low, high = price_ranges.get(plat, (29, 299))
            plat_shops = shops.get(plat, ["商家"])
            plat_scores = {"jd": 4.9, "taobao": 4.7, "pdd": 4.5}
            base_score = plat_scores.get(plat, 4.5)

            for i in range(items_per_platform):
                # 使用模板生成多样化标题
                template = templates[i % len(templates)]
                adj_sample = random.sample(adjectives, 6)
                brand = random.choice(brands)
                title = template.format(
                    brand=brand,
                    keyword=keyword,
                    adj1=adj_sample[0],
                    adj2=adj_sample[1],
                    adj3=adj_sample[2],
                    adj4=adj_sample[3],
                    adj5=adj_sample[4],
                    adj6=adj_sample[5],
                ).strip()

                # 价格递增 + 随机波动
                price = low + (high - low) * (i / max(items_per_platform - 1, 1)) + random.randint(-8, 12)
                price = max(low, min(high, price))
                price = round(price, 2)

                # 销量与价格负相关
                sales_base = int((high - price) / max(high, 1) * 150000)
                sales = max(300, sales_base + random.randint(-8000, 15000))

                # 评分
                score = round(min(5.0, base_score + random.uniform(-0.15, 0.1)), 1)

                products.append(Product(
                    platform=plat,
                    title=title,
                    price=price,
                    sales=sales,
                    shop_name=random.choice(plat_shops),
                    shop_score=score,
                    url=urls.get(plat, "") + keyword,
                    image_url="",
                ))

        return products
