import requests
from util import logger, poolItem
import time, json
from urllib.parse import quote
from decimal import *

s = requests.Session()
s.headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}

merchant = "btccom"


@logger.catch
def getdata():
    url = "https://console.pool.bitcoin.com/srv/getcontracts?coin=profit"
    logger.info(f"get contract list {url}")
    z1 = s.get(url)
    data = z1.json()
    return data


def parsedata():
    data = getdata()
    powers = []
    for i in data:
        contract = i
        _id = merchant + "_" + str(contract["contractId"])
        coin = contract["coin"]
        if "6 Month" in contract["name"]:
            duration = 6 * 30
        elif "1 Year" in contract["name"]:
            duration = 365
        else:
            continue
        issuers = merchant
        honeyLemon_contract_name = f"BTC {duration} Days"
        contract_size = float(contract["minPurchaseString"].split(" ")[0])
        electricity_fee = float(contract['dailyFee']) 
        management_fee = 0.0  
        buy_url = f'https://console.pool.bitcoin.com/confirmorderguest?contractid={contract["contractId"]}&hashrate={int(contract_size)}&language=en'
        upfront_fee = float(contract["initialCostString"].replace("$", ""))
        messari = 0.04
        sold_percent = 10
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
