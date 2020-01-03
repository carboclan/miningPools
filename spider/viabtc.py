import requests
from .util import logger, poolItem, generate_request
import time, json

from decimal import *

s = generate_request()

merchant = "viabtc"


@logger.catch
def getdata():
    url = "https://pool.viabtc.com/res/cloud/mining/contract"
    logger.info(f"get page {url}")
    z1 = s.get(url, timeout=60)
    data = z1.json()
    if data["code"] == 0:
        return data["data"]


def parsedata():
    data = getdata()
    data = data[0]
    for i in data["package"]:
        contract = data
        _id = merchant + "_" + contract["coin"] + "_" + i["hashrate"]
        coin = data["coin"]
        duration = 360
        issuers = merchant
        contract_size = float(i["hashrate"])
        electricity_fee = float(contract["electricity_price"])
        management_fee = 0.0
        buy_url = f'http://pool.viabtc.com/contract/checkout?contract_id={data["id"]}&hashrate={int(contract_size)}'

        upfront_fee = float(i["price"])
        messari = 0.04
        sold_percent = 10.0
        p = poolItem(
            _id,
            coin,
            duration,
            issuers,
            contract_size,
            electricity_fee,
            management_fee,
            buy_url,
            upfront_fee,
            messari,
            sold_percent,
        )
        p.save2db()


if __name__ == "__main__":
    parsedata()
