"""可视化数据生成模块 - 为前端ECharts准备数据"""
from typing import List, Dict, Any
from models.product import Product
from .comparator import Comparator


class Visualizer:
    """图表数据生成器"""

    def __init__(self):
        self.comparator = Comparator()

    def generate_chart_data(self, products: List[Product]) -> Dict[str, Any]:
        """生成所有图表所需的数据"""
        if not products:
            return self._empty_charts()

        return {
            "price_bar_chart": self._price_bar_chart(products),
            "price_trend_chart": self._price_trend_chart(products),
            "radar_chart": self._radar_chart(products),
            "platform_pie": self._platform_pie(products),
        }

    def _empty_charts(self) -> Dict:
        return {
            "price_bar_chart": {"categories": [], "series": []},
            "price_trend_chart": {"categories": [], "series": []},
            "radar_chart": {"indicator": [], "series": []},
            "platform_pie": {"data": []},
        }

    def _price_bar_chart(self, products: List[Product]) -> Dict:
        """价格对比柱状图 - Top10 最便宜商品"""
        sorted_products = sorted(products, key=lambda p: p.price)[:10]
        return {
            "categories": [self._short_title(p.title) for p in sorted_products],
            "series": [
                {
                    "name": "价格",
                    "data": [p.price for p in sorted_products],
                }
            ],
        }

    def _price_trend_chart(self, products: List[Product]) -> Dict:
        """价格区间分布统计（模拟趋势）"""
        prices = sorted([p.price for p in products])
        if not prices:
            return {"categories": [], "series": []}

        # 创建价格区间
        min_p, max_p = prices[0], prices[-1]
        step = (max_p - min_p) / 8 if max_p > min_p else 1
        categories = []
        counts = []
        for i in range(8):
            low = min_p + i * step
            high = min_p + (i + 1) * step
            count = sum(1 for p in prices if low <= p < high if i < 7 or p <= max_p)
            categories.append(f"{round(low, 0)}")
            counts.append(count)
        # 最后一个区间包含上界
        counts[-1] = sum(1 for p in prices if p >= min_p + 7 * step)

        return {
            "categories": categories,
            "series": [
                {
                    "name": "商品数量",
                    "data": counts,
                }
            ],
        }

    def _radar_chart(self, products: List[Product]) -> Dict:
        """性价比雷达图 - 各平台多维度对比"""
        platforms = {}
        for p in products:
            if p.platform not in platforms:
                platforms[p.platform] = {"prices": [], "sales": [], "scores": []}
            platforms[p.platform]["prices"].append(p.price)
            platforms[p.platform]["sales"].append(p.sales)
            platforms[p.platform]["scores"].append(p.shop_score)

        # 计算各平台归一化分数（0-100）
        all_avg_prices = [sum(v["prices"]) / len(v["prices"]) for v in platforms.values()]
        all_avg_sales = [sum(v["sales"]) / len(v["sales"]) for v in platforms.values()]
        max_price = max(all_avg_prices) if all_avg_prices else 1
        max_sales = max(all_avg_sales) if all_avg_sales else 1

        series = []
        for plat, data in platforms.items():
            avg_price = sum(data["prices"]) / len(data["prices"])
            avg_sales = sum(data["sales"]) / len(data["sales"])
            avg_score = sum(data["scores"]) / len(data["scores"])

            # 价格维度：越低越好（反向）
            price_dim = round((1 - avg_price / max_price) * 100) if max_price > 0 else 0
            sales_dim = round((avg_sales / max_sales) * 100) if max_sales > 0 else 0
            score_dim = round((avg_score / 5) * 100)

            series.append({
                "name": self._platform_name(plat),
                "value": [price_dim, sales_dim, score_dim],
            })

        return {
            "indicator": [
                {"name": "价格优势", "max": 100},
                {"name": "销量", "max": 100},
                {"name": "店铺评分", "max": 100},
            ],
            "series": series,
        }

    def _platform_pie(self, products: List[Product]) -> Dict:
        """平台商品数量占比"""
        counts = {}
        for p in products:
            counts[p.platform] = counts.get(p.platform, 0) + 1

        return {
            "data": [
                {"name": self._platform_name(k), "value": v}
                for k, v in counts.items()
            ]
        }

    @staticmethod
    def _short_title(title: str, length: int = 15) -> str:
        if len(title) <= length:
            return title
        return title[:length] + "..."

    @staticmethod
    def _platform_name(key: str) -> str:
        names = {"jd": "京东", "taobao": "淘宝", "pdd": "拼多多"}
        return names.get(key, key)
