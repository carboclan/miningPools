import requests
from .util import logger, poolItem, generate_request
import time, json

from decimal import *

s = generate_request()

merchant = "bitdeer"


@logger.catch
def getdata():
    url = f"https://www.bitdeer.com/api/product/alllist?algorithm=1&_t={int(time.time()*1000)}"  ##btc
    logger.info(f"get page {url}")
    z1 = s.get(url, timeout=60)
    l = []
    data = z1.json()["data"]
    for k, v in data.items():
        if not v.get("data", ""):
            l.append(k)
    for dd in l:
        del data[dd]
    url2 = f"https://www.bitdeer.com/api/product/alllist?algorithm=3&_t={int(time.time()*1000)}"  ##ETH
    z2 = s.get(url2, timeout=60)
    data1 = z2.json()["data"]
    data1.update(data)
    return data1


@logger.catch
def parsedata():
    data = getdata()
    for k, v in data.items():
        if not v["data"]:
            continue
        for contract in v["data"]:
            _id = merchant + "_" + str(contract["id"])
            coin = contract["coin_symbol"]
            duration = int(contract["days"])
            issuers = merchant
            contract_size = float(contract["cnt"])
            electricity_fee = float(contract["electric_price"])
            management_fee = float(contract["maintance_price"])
            ##TODO: url 需要检查是否是根据coin变化的
            buy_url = f'https://www.bitdeer.com/en/buyContract?algorithmid=1&sku_id={contract["id"]}&src=recommend'
            upfront_fee = float(contract["hash_rate_final_price"])
            messari = 0.04
            ##TODO:api里面没有显示具体还有多少可以卖
            sold_percent = float(contract["sold_percent"])
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
