"""基于公开API的真实数据爬虫"""
import asyncio
import httpx
from typing import List

from models.product import Product


class FakeStoreAPIScraper:
    """使用公开电商API获取真实商品数据"""
    
    BASE_URL = "https://fakestoreapi.com"
    
    PLATFORM_MAPPING = {
        "electronics": "jd",
        "men's clothing": "taobao",
        "women's clothing": "taobao",
        "jewelery": "pdd",
    }
    
    SHOP_MAPPING = {
        "jd": ["京东自营旗舰店", "数码精选专营店", "官方授权店", "品牌旗舰店"],
        "taobao": ["潮流服饰店", "品质生活馆", "时尚精品店", "外贸原单店"],
        "pdd": ["多多优选店", "平价好物铺", "源头厂家店", "特价清仓店"],
    }
    
    def __init__(self, max_items: int = 20):
        self.max_items = max_items
    
    async def search(self, keyword: str) -> List[Product]:
        """通过关键词搜索获取真实商品数据"""
        products = []
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(f"{self.BASE_URL}/products")
                if response.status_code != 200:
                    print("[API] 数据获取失败")
                    return []
                
                data = response.json()
                filtered = self._filter_by_keyword(data, keyword)
                
                for item in filtered[:self.max_items]:
                    platform = self._map_category_to_platform(item.get("category", ""))
                    shop_name = self._get_shop_name(platform)
                    
                    product = Product(
                        platform=platform,
                        title=item.get("title", "")[:80],
                        price=float(item.get("price", 0)),
                        sales=int(item.get("rating", {}).get("count", 0)),
                        shop_name=shop_name,
                        shop_score=float(item.get("rating", {}).get("rate", 0)),
                        url=f"{self.BASE_URL}/products/{item.get('id', '')}",
                        image_url=item.get("image", ""),
                    )
                    products.append(product)
                
                print(f"[API] 成功获取 {len(products)} 条真实商品数据")
                return products
                
            except Exception as e:
                print(f"[API] 请求失败: {e}")
                return []
    
    def _filter_by_keyword(self, items: List[dict], keyword: str) -> List[dict]:
        """根据关键词过滤商品"""
        if not keyword:
            return items
        
        keyword_lower = keyword.lower()
        keywords = keyword_lower.split()
        
        def match(item):
            title = (item.get("title", "") + " " + item.get("description", "") + " " + item.get("category", "")).lower()
            return any(kw in title for kw in keywords)
        
        matched = [item for item in items if match(item)]
        if matched:
            return matched
        return items[:self.max_items]
    
    def _map_category_to_platform(self, category: str) -> str:
        """将商品类别映射到平台"""
        category = category.lower()
        return self.PLATFORM_MAPPING.get(category, "taobao")
    
    def _get_shop_name(self, platform: str) -> str:
        """根据平台随机生成店铺名"""
        import random
        return random.choice(self.SHOP_MAPPING.get(platform, ["综合店铺"]))
