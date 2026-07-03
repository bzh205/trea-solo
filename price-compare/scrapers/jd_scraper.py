"""京东爬虫"""
from typing import List

from models.product import Product
from .base import BaseScraper


class JDScraper(BaseScraper):
    platform = "jd"
    search_url = "https://search.jd.com/Search?keyword={}&enc=utf-8"

    async def _parse_page(self, keyword: str) -> List[Product]:
        from urllib.parse import quote

        url = self.search_url.format(quote(keyword))
        try:
            await self._navigate_and_wait(url, wait_selector=".gl-item, [class*='login']", timeout=8000)
        except Exception as e:
            print(f"[jd] 导航失败: {e}")
            return []

        # 检测登录墙
        if await self._is_blocked():
            print(f"[jd] 触发反爬（登录墙），跳过本平台")
            return []

        products = []
        try:
            items = await self.page.query_selector_all(".gl-item")
            if not items:
                return []
        except Exception:
            return []

        for item in items[: self.max_items]:
            try:
                title_el = await item.query_selector(".p-name em, .p-name")
                price_el = await item.query_selector(".p-price i")
                shop_el = await item.query_selector(".p-shop a")
                link_el = await item.query_selector(".p-name a")
                img_el = await item.query_selector(".p-img img")
                comment_el = await item.query_selector(".p-commit strong a")

                title = await title_el.inner_text() if title_el else ""
                price = self.parse_price(await price_el.inner_text() if price_el else "")
                if price <= 0:
                    continue
                shop_name = await shop_el.inner_text() if shop_el else "京东商家"
                sales_text = await comment_el.inner_text() if comment_el else "0"
                sales = self.parse_sales(sales_text)
                href = await link_el.get_attribute("href") if link_el else ""
                url = f"https:{href}" if href and href.startswith("//") else (href or "")
                img_src = ""
                if img_el:
                    img_src = await img_el.get_attribute("src") or await img_el.get_attribute("data-lazy-img") or ""

                products.append(Product(
                    platform=self.platform,
                    title=title.strip()[:80],
                    price=price,
                    sales=sales,
                    shop_name=shop_name.strip()[:30],
                    shop_score=4.7,
                    url=url,
                    image_url=img_src,
                ))
            except Exception:
                continue

        return products
