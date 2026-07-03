"""商品数据模型"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """商品数据结构"""
    platform: str              # 平台 (jd/taobao/pdd)
    title: str                 # 商品名称
    price: float               # 价格
    sales: int = 0             # 销量
    shop_name: str = ""        # 店铺名称
    shop_score: float = 0.0    # 店铺评分
    url: str = ""              # 商品链接
    image_url: str = ""        # 商品图片
    crawl_time: str = field(   # 采集时间
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        return cls(
            platform=data.get("platform", ""),
            title=data.get("title", ""),
            price=float(data.get("price", 0)),
            sales=int(data.get("sales", 0) or 0),
            shop_name=data.get("shop_name", ""),
            shop_score=float(data.get("shop_score", 0) or 0),
            url=data.get("url", ""),
            image_url=data.get("image_url", ""),
            crawl_time=data.get("crawl_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

    @property
    def price_performance(self) -> float:
        """性价比分数 = 销量 * 评分 / 价格 (归一化指标)"""
        if self.price <= 0:
            return 0.0
        return round((self.sales * self.shop_score) / self.price, 2)
