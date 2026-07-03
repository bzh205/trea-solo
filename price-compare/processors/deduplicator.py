"""数据去重模块 - 基于标题相似度和URL去重"""
from typing import List
from difflib import SequenceMatcher

from models.product import Product


class Deduplicator:
    """数据去重器"""

    def __init__(self, similarity_threshold: float = 0.85):
        self.threshold = similarity_threshold

    def deduplicate(self, products: List[Product]) -> List[Product]:
        """去重：优先保留价格更低的商品"""
        if not products:
            return []

        # 按价格升序排列，保留便宜的
        sorted_products = sorted(products, key=lambda p: p.price)
        unique = []

        for p in sorted_products:
            is_dup = False
            for existing in unique:
                if self._is_duplicate(p, existing):
                    is_dup = True
                    break
            if not is_dup:
                unique.append(p)

        return unique

    def _is_duplicate(self, a: Product, b: Product) -> bool:
        """判断是否重复"""
        # 同平台同URL视为重复
        if a.platform == b.platform and a.url and a.url == b.url:
            return True
        # 标题相似度高且价格接近(误差<10%)视为重复
        similarity = SequenceMatcher(None, a.title.lower(), b.title.lower()).ratio()
        if similarity >= self.threshold:
            avg_price = (a.price + b.price) / 2
            if avg_price > 0:
                price_diff = abs(a.price - b.price) / avg_price
                if price_diff < 0.1:
                    return True
        return False
