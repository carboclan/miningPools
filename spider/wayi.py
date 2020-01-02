import requests
from .util import logger, poolItem
import time, json

from decimal import *

s = requests.Session()
s.headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}

merchant = "wayi"


@logger.catch
def getdata():
    url = "https://api.wayi.cn/hash/getHashPlan/multi"
    logger.info(f"get url {url}")
    pageNO = 1
    ret_data = []
    while True:
        logger.info(f"get page {pageNO}")
        reqData = {
            "pageNO": pageNO,
            "pageSize": 10,
            "search": '{"coinType":"2","status":1,"productType":"110","hash_status":1}',
        }
        z1 = s.post(url, json=reqData)
        data = z1.json()["body"]
        if z1.json()["type"]:
            ret_data.extend(data["result"].copy())
            if data["pageTotal"] > data["pageNum"]:
                pageNO = data["pageNum"] + 1
                continue
        break
    return ret_data


@logger.catch
def parsedata():
    data = getdata()
    for i in data:
        contract = i
        _id = merchant + "_" + str(contract["id"])
        coin = contract["coinTypeName"]
        if not contract.get("incomeDays", 0):
            continue
        duration = int(contract["incomeDays"])
        issuers = merchant
        contract_size = float(contract["minAmount"])
        electricity_fee = float(contract["eleFeeUsdt"])
        management_fee = 0.0
        buy_url = f'https://wayi.cn/index/buyHash/{contract["id"]}'

        upfront_fee = float(contract["priceUsdt"]) * contract_size
        messari = 0.04
        if contract["unSellCopies"] == 0:
            sold_percent = 100.0
        else:
            sold_percent = float(
                Decimal(
                    (Decimal(contract["amount"]) - Decimal(contract["unSellCopies"]))
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
