"""京东爬虫"""
from typing import List

from models.product import Product
from .base import BaseScraper


class JDScraper(BaseScraper):
    platform = "jd"
    search_url = "https://search.jd.com/Search?keyword={}"

    async def _parse_page(self, keyword: str) -> List[Product]:
        from urllib.parse import quote

        url = self.search_url.format(quote(keyword))
        await self._navigate_and_wait(url, ".gl-item")

        products = []
        items = await self.page.query_selector_all(".gl-item")

        for item in items[: self.max_items]:
            try:
                title_el = await item.query_selector(".p-name em")
                price_el = await item.query_selector(".p-price i")
                shop_el = await item.query_selector(".p-shop a")
                link_el = await item.query_selector(".p-name a")
                img_el = await item.query_selector(".p-img img")
                comment_el = await item.query_selector(".p-commit strong a")

                title = await title_el.inner_text() if title_el else ""
                price = self.parse_price(await price_el.inner_text() if price_el else "")
                shop_name = await shop_el.inner_text() if shop_el else ""
                sales_text = await comment_el.inner_text() if comment_el else "0"
                sales = self.parse_sales(sales_text)
                href = await link_el.get_attribute("href") if link_el else ""
                url = f"https:{href}" if href and href.startswith("//") else href
                img_src = await img_el.get_attribute("src") or await img_el.get_attribute("data-lazy-img") if img_el else ""

                products.append(Product(
                    platform=self.platform,
                    title=title.strip(),
                    price=price,
                    sales=sales,
                    shop_name=shop_name.strip(),
                    shop_score=4.7,  # 京东默认评分较高
                    url=url,
                    image_url=img_src,
                ))
            except Exception:
                continue

        return products
