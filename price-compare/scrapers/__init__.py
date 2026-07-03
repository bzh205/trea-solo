from .base import BaseScraper
from .jd_scraper import JDScraper
from .taobao_scraper import TaobaoScraper
from .pdd_scraper import PDDScraper

SCRAPERS = {
    "jd": JDScraper,
    "taobao": TaobaoScraper,
    "pdd": PDDScraper,
}
