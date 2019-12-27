import requests
from util import logger, power_detail
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
    logger.debug(f"奇怪的错误:{z1.text}")


def parsedata():
    data = getdata()
    powers = []
    for i in data:
        contract = i["contract"]
        power_detail["id"] = merchant + "_" + str(contract["Id"])
        power_detail["created_time"] = contract["CreateTime"]
        power_detail[
            "buy_url"
        ] = 'https://'+quote(f'www.oxbtc.com/cloudhash/buy/hash_contractDetail/{contract["Symbol"]}')
        power_detail["merchant"] = merchant
        power_detail["updated_time"] = int(time.time())
        power_detail["delivery_time"] = i["delivery_date"]

        power_detail["hash_rate_price"] = contract["Price"]
        power_detail["hash_rate_price_discount"] = 1
        ## 管理费
        power_detail["mainteance_price"] = contract["ManageFee"]
        power_detail["mainteance_price_discount"] = 1

        ## 合约天数
        if contract["HashExpireDays"] == 0:
            power_detail["days"] = contract["HashExpireYears"] * 365
        else:
            power_detail["days"] = contract["HashExpireDays"]
        power_detail["amount"] = contract["UnionAmount"]

        power_detail["hash_rate"] = contract["MinAmount"]  # 这边选择的是允许购买的下限

        ## 算出电费价格 以及 合约天数的折扣
        power_detail["electric_price_discount"] = 1
        power_detail["electric_price"] = contract["MaintenanceFee"]

        power_detail["hash_rate_final_price"] = str(
            Decimal(power_detail["hash_rate_price"]).quantize(
                Decimal("0.0001"), rounding=ROUND_UP
            )
            * Decimal(power_detail["hash_rate_price_discount"])
            * Decimal(power_detail["days"])
            * Decimal(power_detail["hash_rate"])
        )
        power_detail["maintance_final_price"] = 0
        power_detail["electric_final_price"] = str(
            Decimal(power_detail["electric_price_discount"]).quantize(
                Decimal("0.0001"), rounding=ROUND_UP
            )
            * Decimal(power_detail["electric_price"]).quantize(
                Decimal("0.0001"), rounding=ROUND_UP
            )
            * Decimal(power_detail["days"])
            * Decimal(power_detail["hash_rate"]).quantize(
                Decimal("0.0001"), rounding=ROUND_UP
            )
        )

        power_detail["price"] = str(
            Decimal(power_detail["hash_rate_final_price"])
            + Decimal(power_detail["maintance_final_price"])
            + Decimal(power_detail["electric_final_price"])
        )
        if contract["TotalAmount"] == 0:
            power_detail["sold_percent"] = 100
        else:
            power_detail["sold_percent"] = str(
                Decimal(
                    Decimal(contract["SellAmount"])
                    / Decimal(contract["TotalAmount"])
                    * 100
                ).quantize(Decimal("1"), rounding=ROUND_DOWN)
            )
        power_detail["coin"] = contract["Item"]
        power_detail["pool"] = ""
        power_detail["algorithm"] = ""
        power_detail["mining_machine"] = contract['Name'].split('-')[-1]

        powers.append(power_detail.copy())
    with open('oxbtc.json','w') as f:
        f.write(json.dumps(powers))


if __name__ == "__main__":
    parsedata()
