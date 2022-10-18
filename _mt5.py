#_mt5.py

from math import floor
from winsound import PlaySound
import MetaTrader5 as mt5


def login():
    username = 1051332401
    password = "X32CMQ5SPH"
    server = "FTMO-Demo"
    
    if not mt5.initialize():
        print("initialize() failed, error code: ", mt5.last_error())
        return False

    auth = mt5.login(username, password, server)
    print("Logged into MT5")
    return auth

def shutdown():
    mt5.shutdown()

def order(symbol, orderAction, orderType, entry_price, tp, sl, comment, maxrisk):
    mt5.initialize()
    # Add the option to account for spread.
    info = mt5.symbol_info(symbol)
    tick_info = mt5.symbol_info_tick(symbol)

    stopInPips = abs(round(entry_price - sl, info.digits)/info.point)/10
    lots = calculateLots(symbol, stopInPips, maxrisk)
    spread = info.ask - info.bid
    
    sl_spread = sl + spread

    request = {
        "action": mt5.TRADE_ACTION_DEAL if orderAction == "market_order" else mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": float(lots),
        "type": mt5.ORDER_TYPE_BUY if orderType == "buy" else mt5.ORDER_TYPE_SELL if orderType == "sell" else mt5.ORDER_TYPE_BUY_LIMIT if orderType == "buy_limit" else mt5.ORDER_TYPE_SELL_LIMIT if orderType == "sell_limit" else mt5.ORDER_TYPE_BUY_STOP if orderType == "buy_stop" else mt5.ORDER_TYPE_SELL_STOP,
        "price": tick_info.ask if orderAction == "market_order" and orderType == "buy" else tick_info.bid if orderAction == "market_order" and orderType == "sell" else entry_price if orderAction == "pending_order" and orderType == "buy_stop" or orderAction == "pending_order" and orderType == "buy_limit" else entry_price,
        "sl": sl_spread if orderType == "sell" or orderType == "sell_stop" or orderType == "sell_limit" else sl,
        "tp": tp,
        "magic": 2033,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }

    if orderAction == "market_order":
        request['deviation'] = 20

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE: 
        print("4. order_send failed, retcode={}".format(result.retcode))
        PlaySound("400.wav", False)
        if result.retcode == mt5.TRADE_RETCODE_INVALID_PRICE and orderAction == "pending_order":
            order(symbol, orderAction, "buy_limit" if orderType == "buy_stop" else "sell_limit" if orderType == "sell_stop" else "buy_stop" if orderType == "buy_limit" else "sell_stop", entry_price, tp, sl, comment, maxrisk)
    else:
        PlaySound("200.wav", False)
    return result

def calculateLots(symbol, sl, maxrisk):
    lots = 0.25
    riskPerTrade = riskTierModel(maxrisk)
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

def riskTierModel(maxrisk):
    equity = mt5.account_info().balance
    riskPerTrade = 1
    
    riskTier_3 = (equity < 138000 and equity >= 122000)
    riskTier_2 = (equity < 122000 and equity >= 112000)
    riskTier_1 = (equity <= 100000 and equity >= 99000) or (equity > 100000 and equity < 112000)
    riskTier_0_5 = (equity < 99000 and equity > 92000)
    riskTier_0_25 = (equity <= 92000)
    
    # You're gonna have to fix this if your balance is different than 100k.
    if maxrisk == 4:
        if equity >= 138000:
            riskPerTrade = 4
        if riskTier_3:
            riskPerTrade = 3
        if riskTier_2:
            riskPerTrade = 2
        if riskTier_1:
            riskPerTrade = 1
        if riskTier_0_5:
            riskPerTrade = 0.5
        if riskTier_0_25:
            riskPerTrade = 0.25

    if maxrisk == 3:
        if equity >= 122000:
            riskPerTrade = 3
        if riskTier_2:
            riskPerTrade = 2
        if riskTier_1:
            riskPerTrade = 1
        if riskTier_0_5:
            riskPerTrade = 0.5
        if riskTier_0_25:
            riskPerTrade = 0.25

    if maxrisk == 2:
        if equity >= 112000:
            riskPerTrade = 2
        if riskTier_1:
            riskPerTrade = 1
        if riskTier_0_5:
            riskPerTrade = 0.5
        if riskTier_0_25:
            riskPerTrade = 0.25

    if maxrisk == 1:
        if (equity >= 99000):
            riskPerTrade = 1
        if riskTier_0_5:
            riskPerTrade = 0.5
        if riskTier_0_25:
            riskPerTrade = 0.25

    if maxrisk == 0.5:
        if (equity > 92000):
            riskPerTrade = 0.5
        if riskTier_0_25:
            riskPerTrade = 0.25
   
    return riskPerTrade

def closeOrder(symbol):
    # mt5.initialize()
    positions = mt5.positions_get(symbol=symbol)

    if len(positions) == 0:
        print("No Open positions on {}, error code = {}".format(symbol, mt5.last_error))
        return

    tick = mt5.symbol_info_tick(symbol)
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": positions[0].ticket,
        "symbol": positions[0].symbol,
        "volume": positions[0].volume,
        "type": mt5.ORDER_TYPE_BUY if positions[0].type == 1 else mt5.ORDER_TYPE_SELL,
        "price": tick.ask if positions[0].type == 1 else tick.bid,
        "deviation": 20,
        "magic": 7,
        "comment": "MetaView > Close Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    
    result = mt5.order_send(request)
    return result

def modifyOrder(symbol, sl = None, tp = None):
    # mt5.initialize()
    positions = mt5.positions_get(symbol=symbol)
    # One order per symbol

    if len(positions) == 0:
        print("No Open positions on {}, error code = {}".format(symbol, mt5.last_error))
        return

    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": positions[0].ticket,
    }

    if sl != -1:
        request["sl"] = sl
    if tp != -1:
        request["tp"] = tp 
    
    if sl != -1 and len(positions) > 0 or tp != -1 and len(positions) > 0:
        result = mt5.order_send(request)

    if result != None and result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Error Occured while modifying, error code:{} | Comment:{}".format(result.retcode, result.comment))

    return result

def deleteOrder(ticket):
    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket
    }

    result = mt5.order_send(request)
    result