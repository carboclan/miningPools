import requests
from .util import logger, poolItem
import time, json
from urllib.parse import quote
from decimal import *

s = requests.Session()
s.headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}

merchant = "oxbtc"


@logger.catch
def getdata():
    url = "https://www.oxbtc.com/api/default/shop?buy_page=true"
    logger.info(f"get contract list {url}")
    z1 = s.get(url)
    data = z1.json()
    datas = []
    if data["Code"] == "0":
        contracts = data["Data"]["contracts"]["contracts"]
        for contract in contracts:
            datas.append(getcontract(contract))
        return datas
    logger.debug(f"奇怪的错误:{z1.text}")


def getcontract(contract):
    url = f"https://www.oxbtc.com/api/default/contract_detail?symbol={contract}"
    logger.info(f"get contract: {contract}")

    z1 = s.get(url)
    data = z1.json()
    if data["Code"] == "0":
        return data["Data"]


def parsedata():
    data = getdata()
    powers = []
    for i in data:
        contract = i["contract"]
        _id = merchant + "_" + str(contract["Id"])
        coin = contract["Item"]
        if contract["HashExpireDays"] != 0:
            duration = contract["HashExpireDays"]
        else:
            duration = contract["HashExpireYears"] * 365
        if duration == 0:
            continue
        issuers = merchant
        honeyLemon_contract_name = contract["Name"]
        contract_size = contract["MinAmount"]
        electricity_fee = contract["ElectricFeeUsd"]
        management_fee = contract["ManageFee"]
        buy_url = "https://" + quote(
            f'www.oxbtc.com/cloudhash/buy/hash_contractDetail/{contract["Symbol"]}'
        )
        upfront_fee = i["price"] * contract_size
        messari = 0.04
        if contract["TotalAmount"] == 0:
            sold_percent = 100.0
        else:
            sold_percent = float(
                Decimal(
                    Decimal(contract["SellAmount"])
                    / Decimal(contract["TotalAmount"])
                    * 100
                ).quantize(Decimal(".1"), rounding=ROUND_DOWN)
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

    with open(f"{merchant}.json", "w") as f:
        f.write(json.dumps(powers))


if __name__ == "__main__":
    parsedata()
