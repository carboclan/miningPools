import requests
from .util import logger, poolItem
import time, json

from decimal import *

s = requests.Session()
s.headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}

merchant = "bitdeer"


@logger.catch
def getdata():
    url = f"https://www.bitdeer.com/api/product/alllist?algorithm=1&_t={int(time.time()*1000)}"
    logger.info(f"get page {url}")
    z1 = s.get(url)
    data = z1.json()
    if data["code"] == 0:
        return data["data"]


@logger.catch
def parsedata():
    data = getdata()
    powers = []
    for k, v in data.items():
        if not v["data"]:
            continue
        for contract in v["data"]:
            _id = merchant + "_" + str(contract["id"])
            coin = contract["coin_symbol"]
            duration = int(contract["days"])
            issuers = merchant
            honeyLemon_contract_name = f"BTC {duration} Days"
            contract_size = float(contract["cnt"])
            electricity_fee = float(contract["electric_price"])
            management_fee = float(contract["maintance_price"])
            buy_url = f'https://www.bitdeer.com/zh/buyContract?algorithmid=1&sku_id={contract["id"]}&src=recommend'
            upfront_fee = float(contract["hash_rate_final_price"])
            messari = 0.04
            sold_percent = float(contract["sold_percent"])
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
