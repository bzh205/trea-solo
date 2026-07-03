"""数据清洗模块 - 处理异常值、缺失值"""
from typing import List
from models.product import Product
from utils.helpers import clean_text


class DataCleaner:
    """数据清洗器"""

    def clean(self, products: List[Product]) -> List[Product]:
        """执行完整清洗流程"""
        cleaned = []
        for p in products:
            if not self._is_valid(p):
                continue
            p = self._normalize(p)
            cleaned.append(p)
        return cleaned

    def _is_valid(self, p: Product) -> bool:
        """验证数据有效性"""
        # 标题非空
        if not p.title or len(p.title.strip()) < 2:
            return False
        # 价格必须大于0
        if p.price <= 0 or p.price > 999999:
            return False
        # URL 可选但若有则需以 http 开头
        if p.url and not p.url.startswith("http"):
            p.url = ""
        return True

    def _normalize(self, p: Product) -> Product:
        """标准化数据"""
        p.title = clean_text(p.title)
        p.shop_name = clean_text(p.shop_name)
        # 价格保留两位小数
        p.price = round(p.price, 2)
        # 销量非负
        p.sales = max(0, p.sales)
        # 评分范围 0-5
        p.shop_score = max(0.0, min(5.0, p.shop_score))
        return p
