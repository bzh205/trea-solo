"""性价比推荐模块"""
from typing import List, Dict, Tuple
from models.product import Product


class Recommender:
    """性价比推荐器"""

    def recommend(self, products: List[Product]) -> List[Dict]:
        """为商品标注推荐等级"""
        if not products:
            return []

        # 计算归一化分数
        scored = self._calculate_scores(products)

        # 分级标注
        for item in scored:
            item["recommend_label"] = self._get_label(item["total_score"])

        # 按综合分数排序
        scored.sort(key=lambda x: x["total_score"], reverse=True)
        return scored

    def _calculate_scores(self, products: List[Product]) -> List[Dict]:
        """计算归一化分数（价格越低分越高、销量越高分越高、评分越高分越高）"""
        prices = [p.price for p in products]
        sales = [p.sales for p in products]
        scores = [p.shop_score for p in products]

        max_price, min_price = max(prices), min(prices)
        max_sales, min_sales = max(sales), (min(sales) if min(sales) > 0 else 0)
        max_score, min_score = max(scores), min(scores)

        result = []
        for p in products:
            # 价格分数：越低越好（反向归一化）
            price_score = self._normalize_inverse(p.price, min_price, max_price)
            # 销量分数
            sales_score = self._normalize(p.sales, min_sales, max_sales)
            # 评分分数
            score_score = self._normalize(p.shop_score, min_score, max_score)

            # 综合分数：价格权重0.4, 销量0.3, 评分0.3
            total = round(price_score * 0.4 + sales_score * 0.3 + score_score * 0.3, 2)

            result.append({
                **p.to_dict(),
                "price_score": round(price_score, 2),
                "sales_score": round(sales_score, 2),
                "shop_score_normalized": round(score_score, 2),
                "total_score": total,
            })
        return result

    def _normalize(self, value: float, min_v: float, max_v: float) -> float:
        if max_v == min_v:
            return 1.0
        return (value - min_v) / (max_v - min_v)

    def _normalize_inverse(self, value: float, min_v: float, max_v: float) -> float:
        """反向归一化（值越小分越高）"""
        if max_v == min_v:
            return 1.0
        return (max_v - value) / (max_v - min_v)

    def _get_label(self, score: float) -> str:
        """根据分数获取推荐标签"""
        if score >= 0.8:
            return "强烈推荐"
        elif score >= 0.6:
            return "推荐"
        elif score >= 0.4:
            return "一般"
        else:
            return "不推荐"
