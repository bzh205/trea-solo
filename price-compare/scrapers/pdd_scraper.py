"""拼多多爬虫"""
from typing import List

from models.product import Product
from .base import BaseScraper


class PDDScraper(BaseScraper):
    platform = "pdd"
    search_url = "https://mobile.yangkeduo.com/search_result.html?search_key={}"

    async def _parse_page(self, keyword: str) -> List[Product]:
        from urllib.parse import quote

        url = self.search_url.format(quote(keyword))
        await self._navigate_and_wait(url)

        # 拼多多是移动端页面，需要等待动态加载
        await self.page.wait_for_timeout(3000)
        # 尝试滚动触发懒加载
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await self.page.wait_for_timeout(2000)

        products = []
        # 拼多多商品卡片选择器（可能需要根据实际页面调整）
        items = await self.page.query_selector_all('[class*="goods"], [class*="item-card"]')

        for item in items[: self.max_items]:
            try:
                title_el = await item.query_selector('[class*="title"], [class*="goods-title"]')
                price_el = await item.query_selector('[class*="price"], [class*="cur-price"]')
                sales_el = await item.query_selector('[class*="sales"], [class*="sold"]')
                link_el = await item.query_selector("a")
                img_el = await item.query_selector("img")

                title = await title_el.inner_text() if title_el else ""
                price = self.parse_price(await price_el.inner_text() if price_el else "")
                sales = self.parse_sales(await sales_el.inner_text() if sales_el else "")
                href = await link_el.get_attribute("href") if link_el else ""
                url = href if href.startswith("http") else f"https://mobile.yangkeduo.com{href}" if href else ""
                img_src = await img_el.get_attribute("src") if img_el else ""

                products.append(Product(
                    platform=self.platform,
                    title=title.strip(),
                    price=price,
                    sales=sales,
                    shop_name="拼多多商家",  # 拼多多店铺名需要额外解析
                    shop_score=4.5,  # 拼多多默认评分
                    url=url,
                    image_url=img_src,
                ))
            except Exception:
                continue

        return products
