import requests
from .util import logger, poolItem, generate_request
import time, json
from parsel import Selector
from decimal import *
import js2xml

s = generate_request()

merchant = "iqmining"


@logger.catch
def getdata():
    url = "https://iqmining.com/pricing"
    logger.info(f"get page {url}")
    z1 = s.get(url, timeout=60)
    response = Selector(text=z1.text)
    jscode = response.xpath(
        '//script[contains(.,"pricesConfig")]/text()'
    ).extract_first()
    parse_js = js2xml.parse(jscode)
    pricesConfig = js2xml.jsonlike.getall(parse_js)
    ret = []
    for k, v in pricesConfig[0].items():
        gold, silver, bronze = {}, {}, {}
        gold.update(v)
        silver.update(v)
        bronze.update(v)
        del gold["fee"]
        del gold["options"]
        del gold["new_price"]
        del bronze["fee"]
        del bronze["options"]
        del bronze["new_price"]
        del silver["fee"]
        del silver["options"]
        del silver["new_price"]
        gold["contract_size"] = v["mingold"] / 1000
        silver["contract_size"] = v["minsilver"] / 1000
        bronze["contract_size"] = v["mincalc"] / 1000

        coin = ""
        if k in ["sha256", "shapro"]:
            coin = "BTC"
        elif k == "shabch":
            coin = "BCH"
        elif k == "eth":
            coin = "ETH"
        else:
            continue
        gold["coin"] = coin
        silver["coin"] = coin
        bronze["coin"] = coin
        if v["fee"]:
            gold["electricity_fee"] = v["fee"]["gold"]
            silver["electricity_fee"] = v["fee"]["silver"]
            bronze["electricity_fee"] = v["fee"]["bronze"]
        else:
            gold["electricity_fee"] = 0
            silver["electricity_fee"] = 0
            bronze["electricity_fee"] = 0
        if v.get("new_price", ""):  ##打折
            price_info = v["new_price"]
        else:
            price_info = v["options"]
        for y, p in price_info.items():
            if y == "y0":
                continue
            elif y == "y1":
                gold["duration"] = 365
                silver["duration"] = 365
                bronze["duration"] = 365
            elif y == "y2":
                gold["duration"] = 365 * 2
                silver["duration"] = 365 * 2
                bronze["duration"] = 365 * 2
            elif y == "y5":
                gold["duration"] = 365 * 5
                silver["duration"] = 365 * 5
                bronze["duration"] = 365 * 5
            gold["upfront_fee"] = p["gold"]
            silver["upfront_fee"] = p["silver"]
            bronze["upfront_fee"] = p["bronze"]
            ret.append(gold.copy())
            ret.append(silver.copy())
            ret.append(bronze.copy())
    return ret


def parsedata():
    data = getdata()
    for contract in data:
        _id = merchant + "_" + contract["name"] + "_" + str(contract["duration"])
        coin = contract["coin"]
        duration = contract["duration"]
        issuers = merchant
        contract_size = float(contract["contract_size"])
        electricity_fee = float(contract["electricity_fee"]) * 100
        management_fee = 0.0
        buy_url = "https://iqmining.com/pricing#tobuy"

        upfront_fee = float(contract["upfront_fee"]) * 100
        messari = 0.04
        sold_percent = 10
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
