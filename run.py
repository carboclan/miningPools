from spider.bitdeer import parsedata as runbitdeer
from spider.btc_com import parsedata as runbtccom
from spider.genesis_mining import parsedata as rungenesis_mining
from spider.miningzoo import parsedata as runminingzoo
from spider.oxbtc import parsedata as runoxbtc
from spider.viabtc import parsedata as runviabtc

runlist = [runbitdeer, runbtccom, rungenesis_mining, runminingzoo, runoxbtc, runviabtc]

for app in runlist:
    app()
