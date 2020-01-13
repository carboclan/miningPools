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
        gold, silver, bronze = {"t": "gold"}, {"t": "silver"}, {"t": "bronze"}
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

        coin = ""
        if k in ["sha256", "shapro"]:
            coin = "BTC"
        elif k == "shabch":
            coin = "BCH"
        elif k == "eth":
            coin = "ETH"
        else:
            continue
        if coin == "ETH":
            gold["contract_size"] = v["mingold"]
            silver["contract_size"] = v["minsilver"]
            bronze["contract_size"] = v["mincalc"]
        else:
            # BTC BCH 这边拿到的是 GH/s 的值 基础单位是 1000GH=1TH
            gold["contract_size"] = v["mingold"] / 1000
            silver["contract_size"] = v["minsilver"] / 1000
            bronze["contract_size"] = v["mincalc"] / 1000
        gold["coin"] = coin
        silver["coin"] = coin
        bronze["coin"] = coin
        if v["fee"]:
            # BTC BCH 这边拿到的是 10GH/s 的值 基础单位是 1000GH
            gold["electricity_fee"] = float(v["fee"]["gold"]) * 100
            silver["electricity_fee"] = float(v["fee"]["silver"]) * 100
            bronze["electricity_fee"] = float(v["fee"]["bronze"]) * 100
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
            if coin == "ETH":
                ## ETH这边拿到的是 0.1 MH/s 的值,基础单位是1MH
                gold["upfront_fee"] = float(p["gold"]) * 10
                silver["upfront_fee"] = float(p["silver"]) * 10
                bronze["upfront_fee"] = float(p["bronze"]) * 10
            else:
                ## BTC BCH 这边拿到的是 10GH/s 的值 基础单位是 1000GH
                gold["upfront_fee"] = float(p["gold"]) * 100
                silver["upfront_fee"] = float(p["silver"]) * 100
                bronze["upfront_fee"] = float(p["bronze"]) * 100
            ret.append(gold.copy())
            ret.append(silver.copy())
            ret.append(bronze.copy())
    return ret


def parsedata():
    data = getdata()
    for contract in data:
        _id = (
            merchant
            + "_"
            + contract["name"]
            + "_"
            + str(contract["duration"])
            + "_"
            + contract["t"]
        )
        coin = contract["coin"]
        duration = contract["duration"]
        issuers = merchant
        contract_size = float(contract["contract_size"])
        electricity_fee = contract["electricity_fee"]
        management_fee = 0.0
        buy_url = "https://iqmining.com/pricing#tobuy"

        upfront_fee = contract["upfront_fee"]
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
