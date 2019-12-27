import requests
from util import logger, power_detail
import time, json

from decimal import *

s = requests.Session()
s.headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}

merchant = "hashnest"


@logger.catch
def getdata():
    url = "https://dcdn.hashnest.com/client/api/v2/hash_currencies/shop"
    logger.info(f"get page {url}")
    z1 = s.get(url)
    data = z1.json()
    return data


def parsedata():
    data = getdata()
    powers = []
    for i in data:
        power_detail["id"] = merchant + "_" + str(i["id"])
        power_detail["buy_url"] = f'https://www.hashnest.com/hash/shopitem?hc_id={i["hash_currency_id"]}'
        power_detail["merchant"] = merchant
        power_detail["updated_time"] = int(time.time())
        power_detail["delivery_time"] = 1

        power_detail["hash_rate_price"] = i["price"]
        power_detail["hash_rate_price_discount"] = 1
        ## 管理费
        power_detail["mainteance_price"] = 0
        power_detail["mainteance_price_discount"] = 1

        ## 合约天数
        power_detail["days"] = i["days"]
        power_detail["amount"] = i["amount"]

        power_detail["hash_rate"] = i["rated_speed"]  

        ## 算出电费价格 以及 合约天数的折扣
        power_detail["electric_price_discount"] = 1
        power_detail["electric_price"] = 1
        electricities = i["electricities"]
        for electricitie in electricities:
            if electricitie["days"] == power_detail["days"]:
                power_detail["electric_price_discount"] = electricitie["off"]
                power_detail["electric_price"] = electricitie["price"]

        power_detail["hash_rate_final_price"] = str(
            Decimal(power_detail["hash_rate_price"])
            * Decimal(power_detail["hash_rate_price_discount"])
            * Decimal(power_detail["days"])
            * Decimal(power_detail["hash_rate"])
        )
        power_detail["maintance_final_price"] = 0
        power_detail["electric_final_price"] = str(
            Decimal(power_detail["electric_price_discount"]).quantize(
                Decimal("0.0001"), rounding=ROUND_UP
            )
            * Decimal(power_detail["electric_price"])
            * Decimal(power_detail["days"])
            * Decimal(power_detail["hash_rate"])
        )

        power_detail["price"] = str(
            Decimal(power_detail["hash_rate_final_price"])
            + Decimal(power_detail["maintance_final_price"])
            + Decimal(power_detail["electric_final_price"])
        )
        if i["balance"] == "0.0":
            power_detail["sold_percent"] = 100
        else:
            power_detail["sold_percent"] = str(
                Decimal(
                    (Decimal(i["amount"]) - Decimal(i["balance"]))
                    / Decimal(i["amount"])
                    * 100
                ).quantize(Decimal("1"), rounding=ROUND_DOWN)
            )
        power_detail["coin"] = "BTC"
        power_detail["pool"] = ""
        power_detail["algorithm"] = ""
        power_detail["mining_machine"] = ""

        powers.append(power_detail.copy())


if __name__ == "__main__":
    parsedata()
