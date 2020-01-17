import os
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
from requests.adapters import HTTPAdapter
import js2xml
from parsel import Selector

# cache
from redis import StrictRedis
from redis_cache import RedisCache

client = StrictRedis(
    host=os.environ.get("REDIS_HOST", "127.0.0.1"), decode_responses=True
)
cache = RedisCache(redis_client=client)

## db
from pymongo import MongoClient
import pymongo

db = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017"))["spider"][
    "pools"
]
db_snapshot = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017"))[
    "spider"
]["snapshot"]

## requests setting
def generate_request():
    s = requests.Session()
    s.headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    s.mount("http://", HTTPAdapter(max_retries=3))
    s.mount("https://", HTTPAdapter(max_retries=3))

    return s


@dataclass
class poolItem:
    id: str
    coin: str
    duration: int
    issuers: str
    contract_size: float
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
    honeyLemon_contract_name: str = field(init=False)  # BTC 240 Days

    def __post_init__(self):
        if self.coin.lower() == "btc":
            self.btc_price = getPrice()["BTC"]
            self.mining_payoff_btc = get_global_data_BTC()
        elif self.coin.lower() == "eth":
            self.btc_price = getPrice()["ETH"]
            self.mining_payoff_btc = get_global_data_ETH()
        elif self.coin.lower() == "bch":
            self.btc_price = getPrice()["BCH"]
            self.mining_payoff_btc = get_global_data_BCH()
        elif self.coin.lower() == "bsv":
            self.btc_price = getPrice()["BSV"]
            self.mining_payoff_btc = get_global_data_BSV()
        elif self.coin.lower() == "etc":
            self.btc_price = getPrice()["ETC"]
            self.mining_payoff_btc = get_global_data_ETC()
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
        self.honeyLemon_contract_name = f"{self.coin.upper()} {self.duration} Days"

        # btc的合约可以挖bch
        #能够同时挖BCH的平台：Genesis mining, bitdeer, Bitcoin.com, IQ Mining
        # if self.coin.lower() == "btc":
        #     if self.issuers in ["bitdeer", "btccom", "genesis_mining", "iqmining"]:
        #         p1 = poolItem(
        #             self.id + "_bch",
        #             "BCH",
        #             self.duration,
        #             self.issuers,
        #             self.contract_size,
        #             self.electricity_fee,
        #             self.management_fee,
        #             self.buy_url,
        #             self.upfront_fee,
        #             self.messari,
        #             self.sold_percent,
        #         )
        #         p1.save2db()
        # btc的合约可以挖bsv
        # if self.coin.lower() == "btc":
        #     p1 = poolItem(
        #         self.id + "_bsv",
        #         "BSV",
        #         self.duration,
        #         self.issuers,
        #         self.contract_size,
        #         self.electricity_fee,
        #         self.management_fee,
        #         self.buy_url,
        #         self.upfront_fee,
        #         self.messari,
        #         self.sold_percent,
        #     )
        #     p1.save2db()
        # eth的合约可以挖etc
        # if self.coin.lower() == "eth":
        #     p1 = poolItem(
        #         self.id + "_etc",
        #         "ETC",
        #         self.duration,
        #         self.issuers,
        #         self.contract_size,
        #         self.electricity_fee,
        #         self.management_fee,
        #         self.buy_url,
        #         self.upfront_fee,
        #         self.messari,
        #         self.sold_percent,
        #     )
        #     p1.save2db()

    def save2db(self):
        db.update_one({"id": self.id}, {"$set": self.__dict__}, upsert=True)
        self.snapshot()

    def snapshot(self):
        snapshot_data = {
            "contract_cost": self.contract_cost,
            "electricity_fee": self.electricity_fee,
            "management_fee": self.management_fee,
            "mining_payoff": self.mining_payoff,
            "mining_payoff_btc": self.mining_payoff_btc,
            "today_income": self.today_income,
            "sold_percent": self.sold_percent,
            "id": self.id,
            "update_time": self.update_time,
        }
        db_snapshot.insert_one(snapshot_data)
        db_snapshot.create_index(
            [("id", pymongo.ASCENDING), ("update_time", pymongo.ASCENDING)]
        )


@logger.catch
@cache.cache(ttl=300)
def getPrice():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    logger.info("从coinmarketcap爬取价格信息")
    params = {"start": "1", "limit": "100", "convert": "USD"}
    z = requests.get(
        url,
        params=params,
        headers={"X-CMC_PRO_API_KEY": "fafa4240-a7ba-43ee-8954-88d8cc0eec1e"},
    )
    raw_data = z.json()
    prices = {}
    if raw_data["status"]["error_code"] == 0:
        for i in raw_data["data"]:
            symbol = i["symbol"]
            price = i["quote"]["USD"]["price"]
            prices[symbol] = price
        return prices


@logger.catch
@cache.cache(ttl=300)
def get_global_data_BTC():
    """
    拿到btc价格以及 每T/1天的收益
    """
    ##TODO:需要判断是否为btc...其他的币 需要别的获取方法...
    logger.info("爬取btc价格以及每T每天的收益")
    url = "https://explorer.viabtc.com/btc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    z = requests.get(url, headers=headers, timeout=60)
    sel = Selector(text=z.text)
    jscode = sel.xpath(
        '//script[contains(.,"coin_per_t_per_day")]/text()'
    ).extract_first()
    parse_js = js2xml.parse(jscode)
    btc_price = float(
        parse_js.xpath('//*[@name="usd_display_close"]/string/text()')[1].replace(
            "$", ""
        )
    )
    mining_payoff_btc = float(
        parse_js.xpath('//*[@name="coin_per_t_per_day"]/string/text()')[0].strip()
    )
    return mining_payoff_btc


@logger.catch
@cache.cache(ttl=300)
def get_global_data_ETC():
    """
    拿到etc价格以及 每T/1天的收益
    """
    ##TODO:需要判断是否为btc...其他的币 需要别的获取方法...
    logger.info("爬取etc价格以及每T每天的收益")
    url = "https://explorer.viabtc.com/etc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    z = requests.get(url, headers=headers, timeout=60)
    sel = Selector(text=z.text)
    jscode = sel.xpath(
        '//script[contains(.,"coin_per_t_per_day")]/text()'
    ).extract_first()
    parse_js = js2xml.parse(jscode)
    btc_price = float(
        parse_js.xpath('//*[@name="usd_display_close"]/string/text()')[1].replace(
            "$", ""
        )
    )
    mining_payoff_btc = float(
        parse_js.xpath('//*[@name="coin_per_t_per_day"]/string/text()')[0].strip()
    )
    return mining_payoff_btc


@logger.catch
@cache.cache(ttl=300)
def get_global_data_BCH():
    """
    拿到btc价格以及 每T/1天的收益
    """
    ##TODO:需要判断是否为btc...其他的币 需要别的获取方法...
    logger.info("爬取bch价格以及每T每天的收益")
    url = "https://explorer.viawallet.com/bch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    z = requests.get(url, headers=headers, timeout=60)
    sel = Selector(text=z.text)
    jscode = sel.xpath(
        '//script[contains(.,"coin_per_t_per_day")]/text()'
    ).extract_first()
    parse_js = js2xml.parse(jscode)
    btc_price = float(
        parse_js.xpath('//*[@name="usd_display_close"]/string/text()')[1].replace(
            "$", ""
        )
    )
    mining_payoff_btc = float(
        parse_js.xpath('//*[@name="coin_per_t_per_day"]/string/text()')[0].strip()
    )
    return mining_payoff_btc


@logger.catch
@cache.cache(ttl=300)
def get_global_data_BSV():
    """
    拿到bsv价格以及 每T/1天的收益
    """
    ##TODO:需要判断是否为btc...其他的币 需要别的获取方法...
    logger.info("爬取bsv每T每天的收益")
    url = "https://explorer.viawallet.com/bsv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    z = requests.get(url, headers=headers, timeout=60)
    sel = Selector(text=z.text)
    jscode = sel.xpath(
        '//script[contains(.,"coin_per_t_per_day")]/text()'
    ).extract_first()
    parse_js = js2xml.parse(jscode)
    mining_payoff_btc = float(
        parse_js.xpath('//*[@name="coin_per_t_per_day"]/string/text()')[0].strip()
    )
    return mining_payoff_btc


@logger.catch
@cache.cache(ttl=300)
def get_global_data_ETH():
    logger.info("爬取eth价格以及每M每天的收益")
    url = "https://www.sparkpool.com/v1/pool/stats?pool=SPARK_POOL_CN"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    z = requests.get(url, headers=headers, timeout=60)
    for i in z.json()["data"]:
        if i["currency"] == "ETH":
            return i["income"] / 100


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
