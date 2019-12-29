from loguru import logger

logger.add(
    "spider.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}",
    rotation="10 MB",
)

from dataclasses import dataclass, field
import time
from decimal import *
import requests
import js2xml
from parsel import Selector

# cache
from redis import StrictRedis
from redis_cache import RedisCache

client = StrictRedis(host="127.0.0.1", decode_responses=True)
cache = RedisCache(redis_client=client)


@dataclass
class poolItem:
    id: str
    coin: str
    duration: int
    issuers: str
    honeyLemon_contract_name: str  # BTC 240 Days
    contract_size: int
    electricity_fee: float
    management_fee: float
    buy_url: str
    upfront_fee: float
    messari: float  ## Messari.io
    sold_percent: float
    ##TODO: messari 需要从某个网站获取
    update_time: int = int(time.time())
    mining_payoff: float = field(init=False)
    today_income: float = field(init=False)
    contract_cost: float = field(init=False)
    expected_discount: float = field(init=False)
    expected_breakeven_days: float = field(init=False)
    present_value_of_total_cost: float = field(init=False)
    present_value_of_total_electricity_fee: float = field(init=False)
    daily_rate: float = field(init=False)
    btc_price: float = field(init=False)
    mining_payoff_btc: float = field(init=False)

    def __post_init__(self):
        self.btc_price, self.mining_payoff_btc = get_global_data()
        self.mining_payoff = self.btc_price * self.mining_payoff_btc
        self.today_income = self.mining_payoff * (1 - self.management_fee)
        self.daily_rate = pow(1 + self.messari, 1 / 365) - 1
        self.present_value_of_total_electricity_fee = (
            self.electricity_fee
            * ((1 - pow(1 + self.daily_rate, -self.duration)) / self.daily_rate)
            * self.contract_size
        )
        self.present_value_of_total_cost = (
            self.upfront_fee + self.present_value_of_total_electricity_fee
        )
        self.contract_cost = (
            self.present_value_of_total_cost / self.contract_size / self.duration
        )
        self.expected_discount = 1 - self.contract_cost / (
            self.mining_payoff * (1 - self.management_fee)
        )
        self.expected_breakeven_days = (
            self.upfront_fee
            / self.contract_size
            / (self.mining_payoff * (1 - self.management_fee) - self.electricity_fee)
        )


@logger.catch
@cache.cache(ttl=300)
def get_global_data():
    """
    拿到btc价格以及 每T/1天的收益
    """
    ##TODO:需要判断是否为btc...其他的币 需要别的获取方法...
    logger.info("爬取btc价格以及每T每天的收益")
    url = "https://explorer.viabtc.com/btc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    z = requests.get(url, headers=headers)
    sel = Selector(text=z.text)
    jscode = sel.xpath(
        '//script[contains(.,"coin_per_t_per_day")]/text()'
    ).extract_first()
    parse_js = js2xml.parse(jscode)
    btc_price = float(
        parse_js.xpath('//*[@name="usd_display_close"]/string/text()')[0].replace(
            "$", ""
        )
    )
    mining_payoff_btc = float(
        parse_js.xpath('//*[@name="coin_per_t_per_day"]/string/text()')[0].strip()
    )
    return btc_price, mining_payoff_btc


def test_poolItem():
    p = poolItem(
        "oxbtctest",
        "BTC",
        240,
        "oxbtc",
        "BTC 240 Days",
        10,
        0.1098,
        0.0,
        "hhh",
        77.0,
        0.04,
    )
    assert p.__dict__ == {
        "id": "oxbtctest",
        "btc_price": 7316.64,
        "mining_payoff_btc": 1.942e-05,
        "coin": "BTC",
        "duration": 240,
        "issuers": "oxbtc",
        "honeyLemon_contract_name": "BTC 240 Days",
        "contract_size": 10,
        "electricity_fee": 0.1098,
        "management_fee": 0.0,
        "buy_url": "hhh",
        "upfront_fee": 77.0,
        "messari": 0.04,
        "mining_payoff": 0.1420891488,
        "today_income": 0.1420891488,
        "daily_rate": 0.00010745978202786333,
        "present_value_of_total_electricity_fee": 260.13709201305954,
        "present_value_of_total_cost": 337.13709201305954,
        "contract_cost": 0.1404737883387748,
        "expected_discount": 0.011368640567331001,
        "expected_breakeven_days": 238.47020705606204,
    }
    print("公式没问题!")


if __name__ == "__main__":
    test_poolItem()
