import requests
from util import logger, poolItem
import time, json

from decimal import *

s = requests.Session()
s.headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}

merchant = "viabtc"


@logger.catch
def getdata():
    url = "https://pool.viabtc.com/res/cloud/mining/contract"
    logger.info(f"get page {url}")
    z1 = s.get(url)
    data = z1.json()
    if data["code"] == 0:
        return data["data"]


def parsedata():
    data = getdata()
    powers = []
    data = data[0]
    for i in data["package"]:
        contract = data
        _id = merchant + "_" + contract["coin"] + "_" + i["hashrate"]
        coin = data["coin"]
        duration = 360
        issuers = merchant
        honeyLemon_contract_name = f"BTC {duration} Days"
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

    with open(f"{merchant}.json", "w") as f:
        f.write(json.dumps(powers))


if __name__ == "__main__":
    parsedata()
