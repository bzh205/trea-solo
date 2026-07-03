"""淘宝爬虫"""
from typing import List

from models.product import Product
from .base import BaseScraper


class TaobaoScraper(BaseScraper):
    platform = "taobao"
    search_url = "https://s.taobao.com/search?q={}"

    async def _parse_page(self, keyword: str) -> List[Product]:
        from urllib.parse import quote

        url = self.search_url.format(quote(keyword))
        await self._navigate_and_wait(url)

        # 淘宝搜索结果需要等待商品卡片加载
        await self.page.wait_for_timeout(3000)

        products = []
        # 淘宝商品卡片选择器（可能需要根据实际页面调整）
        items = await self.page.query_selector_all('[class*="Card"]')
        if not items:
            items = await self.page.query_selector_all(".items .item")

        for item in items[: self.max_items]:
            try:
                title_el = await item.query_selector('[class*="title"], .title')
                price_el = await item.query_selector('[class*="price"], .price')
                shop_el = await item.query_selector('[class*="shop"], .shopName')
                link_el = await item.query_selector("a")
                img_el = await item.query_selector("img")
                sales_el = await item.query_selector('[class*="realSales"], [class*="sale"]')

                title = await title_el.inner_text() if title_el else ""
                price = self.parse_price(await price_el.inner_text() if price_el else "")
                shop_name = await shop_el.inner_text() if shop_el else ""
                sales = self.parse_sales(await sales_el.inner_text() if sales_el else "")
                href = await link_el.get_attribute("href") if link_el else ""
                url = href if href.startswith("http") else f"https:{href}" if href else ""
                img_src = await img_el.get_attribute("src") if img_el else ""

                products.append(Product(
                    platform=self.platform,
                    title=title.strip(),
                    price=price,
                    sales=sales,
                    shop_name=shop_name.strip(),
                    shop_score=4.6,  # 淘宝默认评分
                    url=url,
                    image_url=img_src,
                ))
            except Exception:
                continue

        return products
