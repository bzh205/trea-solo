"""商品横向对比模块"""
from typing import List, Dict
from models.product import Product


class Comparator:
    """商品对比器 - 生成跨平台对比数据"""

    def compare(self, products: List[Product]) -> Dict:
        """生成对比分析结果"""
        if not products:
            return self._empty_result()

        return {
            "summary": self._summary(products),
            "platform_comparison": self._platform_stats(products),
            "price_distribution": self._price_distribution(products),
            "best_deals": self._best_deals(products),
        }

    def _empty_result(self) -> Dict:
        return {
            "summary": {},
            "platform_comparison": [],
            "price_distribution": [],
            "best_deals": [],
        }

    def _summary(self, products: List[Product]) -> Dict:
        prices = [p.price for p in products]
        return {
            "total_count": len(products),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": round(sum(prices) / len(prices), 2),
            "platforms": list(set(p.platform for p in products)),
        }

    def _platform_stats(self, products: List[Product]) -> List[Dict]:
        """各平台统计对比"""
        stats = {}
        for p in products:
            if p.platform not in stats:
                stats[p.platform] = {
                    "platform": p.platform,
                    "count": 0,
                    "prices": [],
                    "sales": [],
                    "scores": [],
                }
            s = stats[p.platform]
            s["count"] += 1
            s["prices"].append(p.price)
            s["sales"].append(p.sales)
            s["scores"].append(p.shop_score)

        result = []
        for s in stats.values():
            result.append({
                "platform": s["platform"],
                "count": s["count"],
                "min_price": min(s["prices"]),
                "max_price": max(s["prices"]),
                "avg_price": round(sum(s["prices"]) / len(s["prices"]), 2),
                "avg_sales": round(sum(s["sales"]) / len(s["sales"])),
                "avg_score": round(sum(s["scores"]) / len(s["scores"]), 2),
            })
        # 按平均价格升序
        result.sort(key=lambda x: x["avg_price"])
        return result

    def _price_distribution(self, products: List[Product]) -> List[Dict]:
        """价格区间分布"""
        if not products:
            return []
        prices = [p.price for p in products]
        min_p, max_p = min(prices), max(prices)
        # 分5个区间
        step = (max_p - min_p) / 5 if max_p > min_p else 1
        ranges = []
        for i in range(5):
            low = min_p + i * step
            high = min_p + (i + 1) * step if i < 4 else max_p
            count = sum(1 for p in products if low <= p.price <= high if i == 4 or p.price < high)
            ranges.append({
                "range": f"{round(low, 0)}-{round(high, 0)}",
                "count": count,
            })
        return ranges

    def _best_deals(self, products: List[Product]) -> List[Dict]:
        """最佳性价比商品（Top5）"""
        sorted_by_value = sorted(products, key=lambda p: p.price_performance, reverse=True)
        return [
            {
                "title": p.title,
                "platform": p.platform,
                "price": p.price,
                "sales": p.sales,
                "score": p.shop_score,
                "value_score": p.price_performance,
                "url": p.url,
            }
            for p in sorted_by_value[:5]
        ]
