import requests
from .util import logger, poolItem, generate_request
import time, json
from urllib.parse import quote
from decimal import *

s = generate_request()

merchant = "btccom"


@logger.catch
def getdata():
    url = "https://console.pool.bitcoin.com/srv/getcontracts?coin=profit"
    logger.info(f"get contract list {url}")
    z1 = s.get(url, timeout=60)
    data = z1.json()
    return data


def parsedata():
    data = getdata()
    for i in data:
        contract = i
        _id = merchant + "_" + str(contract["contractId"])
        coin = contract["coin"]
        if coin.lower() not in ["btc", "eth"]:
            continue
        if "6 Month" in contract["name"]:
            duration = 6 * 30
        elif "1 Year" in contract["name"]:
            duration = 365
        else:
            continue
        issuers = merchant
        contract_size = float(contract["minPurchaseString"].split(" ")[0])
        electricity_fee = float(contract["dailyFee"])
        management_fee = 0.0
        buy_url = f'https://console.pool.bitcoin.com/confirmorderguest?contractid={contract["contractId"]}&hashrate={int(contract_size)}&language=en'
        upfront_fee = float(contract["initialCostString"].replace("$", ""))
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
