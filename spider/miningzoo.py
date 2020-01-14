import requests
from .util import logger, poolItem, generate_request
import time, json

from decimal import *

s = generate_request()

merchant = "miningzoo"


@logger.catch
def getdata():
    url = "https://www.miningzoo.com/api/v1/powers"
    logger.info(f"get page {url}")
    z1 = s.get(url, timeout=60)
    data = z1.json()
    if data["head"]["code"] == 1000:
        return data["body"]
    logger.debug(f"奇怪的错误:{z1.text}")


def parsedata():
    data = getdata()
    for i in data:
        contract = i

        category_id = contract["category_id"]
        _type = ""
        if category_id == 1:
            _type = "spot"
        else:
            _type = "futures"
        _id = merchant + "_" + str(contract["id"]) + f"_{_type}"
        coin = "BTC"
        duration = contract["days"]
        issuers = merchant
        contract_size = float(contract["mini_limit"])
        for electricitie in contract["electricities"]:
            electricity_fee = float(electricitie["price"])
        management_fee = 0.0
        buy_url = f'https://www.miningzoo.com/order/{contract["id"]}'

        upfront_fee = float(contract["price"]) * duration * contract_size
        messari = 0.04
        if contract["balance"] == "0.0":
            sold_percent = 100.0
        else:
            sold_percent = float(
                Decimal(
                    (Decimal(contract["amount"]) - Decimal(contract["balance"]))
                    / Decimal(contract["amount"])
                    * 100
                ).quantize(Decimal(".1"), rounding=ROUND_DOWN)
            )
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
