# app.py

from math import floor
from flask import Flask, request
import MetaTrader5 as mt5

app = Flask(__name__)

@app.route('/webhook/order/open', methods=['POST'])
def openTradeWebhook():
    if request.method == 'POST':
        if login():
            order(request.json['symbol'], request.json['orderAction'], request.json['orderType'], request.json['entry_price'], request.json['tp'], request.json['sl'])
        return "Webhook recieved"

@app.route('/webhook/order/close', methods=['POST'])
def closeTradeWebhook():
    if request.method == 'POST':
        return "Close Trade Webhook recieved!"

@app.route('/webhook/order/modify', methods=['POST'])
def ModifyTradeWebhook():
    if request.method == 'POST':
        return "Modify Trade Webhook recieved!"

def login():
    username = 1051316876
    password = "X8LMASWEA1"
    server = "FTMO-Demo"
    
    if not mt5.initialize():
        print("initialize() failed, error code: ", mt5.last_error())
        return False

    auth = mt5.login(username, password, server)
    print("Logged into MT5")
    return auth

def shutdown():
    mt5.shutdown()

def order(symbol, orderAction, orderType, entry_price, tp, sl):
    mt5.initialize()
    # Add the option to account for spread.
    info = mt5.symbol_info(symbol)
    tick_info = mt5.symbol_info_tick(symbol)

    stopInPips = abs(round(entry_price - sl, info.digits)/info.point)/10
    lots = calculateLots(symbol, stopInPips)

    request = {
        "action": mt5.TRADE_ACTION_DEAL if orderAction == "market_order" else mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": float(lots),
        "type": mt5.ORDER_TYPE_BUY if orderType == "buy" else mt5.ORDER_TYPE_SELL if orderType == "sell" else mt5.ORDER_TYPE_BUY_LIMIT if orderType == "buy_limit" else mt5.ORDER_TYPE_SELL_LIMIT if orderType == "sell_limit" else mt5.ORDER_TYPE_BUY_STOP if orderType == "buy_stop" else mt5.ORDER_TYPE_SELL_STOP,
        "price": tick_info.ask if orderAction == "market_order" and orderType == "buy" else tick_info.bid if orderAction == "market_order" and orderType == "sell" else entry_price,
        "sl": sl,
        "tp": tp,
        "magic": 2033,
        "comment": "mt5Hook Open Buy Market Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }

    if orderAction == "market_order":
        request['deviation'] = 20

    result = mt5.order_send(request)
    return result

def calculateLots(symbol, sl):
    lots = 0.25
    riskPerTrade = riskTierModel()
    info = mt5.symbol_info(symbol)
    lotstep = info.volume_step

    if riskPerTrade > 0:
        riskAmt =  mt5.account_info().balance * (riskPerTrade / 100)
        lots = round((riskAmt / ((info.spread * 0.1) + sl) / pointVal(symbol)) * 0.1, 2)

    lots = floor(lots / lotstep) * lotstep
    if lots < info.volume_min:
        lots = 0
    if lots > info.volume_max:
        lots = 0

    return lots

def pointVal(symbol):
    info = mt5.symbol_info(symbol)

    tickSize = info.trade_tick_size
    tickValue = info .trade_tick_value
    point = info.point
    ticksPerPt = tickSize / point

    return tickValue / ticksPerPt

def riskTierModel():
    equity = mt5.account_info().balance
    riskPerTrade = 0
    
    if equity >= 112000:
       riskPerTrade = 2
    if (equity <= 100000 and equity >= 99000) or (equity > 100000 and equity < 112000):
       riskPerTrade = 1
    if(equity < 99000 and equity > 92000):
       riskPerTrade = 0.5
    if(equity <= 92000):
       riskPerTrade = 0.25    
   
    return riskPerTrade

def closeOrder(symbol, ticket):
    position = mt5.position_get(ticket=ticket)[0]
    tick = mt5.symbol_info_tick(symbol)
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": position.ticket,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
        "price": tick.ask if position.type == 1 else tick.bid,
        "deviation": 20,
        "magic": 7,
        "comment": "mt5Hook > Close Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }

    result = mt5.order_send(request)
    result

def modifyOrder(ticket, sl = None, tp = None):
    request = {
        "action": mt5.TRADE_ACTION_SLIP,
        "position": ticket,
    }
    if sl != None:
        request["sl"] = sl
    if tp != None:
        request["tp"] = tp 
    
    if sl != None or tp != None:
        result = mt5.order_send(request)

    result

def deleteOrder(ticket):
    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket
    }

    result = mt5.order_send(request)
    result