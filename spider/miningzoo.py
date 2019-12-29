import requests
from util import logger, poolItem
import time, json

from decimal import *

s = requests.Session()
s.headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}

merchant = "miningzoo"


@logger.catch
def getdata():
    url = "https://www.miningzoo.com/api/v1/powers"
    logger.info(f"get page {url}")
    z1 = s.get(url)
    data = z1.json()
    if data["head"]["code"] == 1000:
        return data["body"]
    logger.debug(f"奇怪的错误:{z1.text}")


def parsedata():
    data = getdata()
    powers = []
    for i in data:
        contract = i
        _id = merchant + "_" + str(contract["id"])
        coin = "BTC"
        duration = contract["days"]
        issuers = merchant
        honeyLemon_contract_name = f"BTC {duration} Days"
        contract_size = float(contract["mini_limit"])
        for electricitie in contract["electricities"]:
            electricity_fee = float(electricitie["price"])
        management_fee = 0.0
        buy_url = f'https://www.miningzoo.com/order/{contract["id"]}'

        upfront_fee = float(contract["price"]) * duration
        messari = 0.04
        if contract["balance"] == "0.0":
            sold_percent = 100
        else:
            sold_percent = str(
                Decimal(
                    (Decimal(contract["amount"]) - Decimal(contract["balance"]))
                    / Decimal(contract["amount"])
                    * 100
                ).quantize(Decimal("1"), rounding=ROUND_DOWN)
            )
        p = poolItem(
            _id,
            coin,
            duration,
            issuers,
            honeyLemon_contract_name,
            contract_size,
            electricity_fee,
            management_fee,
            buy_url,
            upfront_fee,
            messari,
            sold_percent,
        )
        powers.append(p.__dict__)

    with open("miningzoo.json", "w") as f:
        f.write(json.dumps(powers))


if __name__ == "__main__":
    parsedata()
