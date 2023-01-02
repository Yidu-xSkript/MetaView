# MetaView
Use TradingView's Alert Hook feature to execute, modify, close, and delete orders.

## What do i pass to MT5 from pinescript alert?
1) orderAction: "market_order, pending_order"
2) symbol: syminfo.ticker (pinescript)
3) orderType: "buy, sell, buy_stop, sell_stop, buy_limit, sell_limit"
4) maxrisk: int -> Modify this on "__mt5.py" and "app.py" if you want to remove this option
5) sl: float
6) tp: float
7) comment: string -> possibly the name of the strategy
8) orderMode: "Open, Close, Modify"

## How It Works

You can modify the code however you see fit. 

I Use NGROK to generate links in order to execute my trades for now. but you can just buy a vpn server and use it.
The way you use it on TradingView will be by adding a similar type of alert in your pinescript strategies.

So MetaView calculates Risk and sets volume based on a model called "The Risk Tier Model". It basically is a way to set risk based on balance and your current profit. example: if you have $100,000 balance and you made 12% on that a/c then it'll automatically increase your risk from 1% to 2%. you're gonna have to modify this the way you like. it calculates based on the 100k a/c balance. you're gonna have to change certain things in the code. specifically you'll be modifying the __mt5.py - ```riskTierModel(maxrisk)``` method which starts form line 92.

Or you can also change the risk management system to something like "asymmetric compounding risk mgmt" system.

MetaView also factors in spread when executing. so if you want that to change you're gonna have to modify the code.

## Pinescript Alert Example
```
metaViewAlert(string mode, string dxn, float sl=-1, float entry_price=-1, float tp=-1) =>
    '{"symbol":"' + syminfo.ticker + '","orderMode":"' + mode + '","orderType":"' + dxn + '_stop"' + ',"orderAction":"pending_order","entry_price":' + str.tostring(entry_price, "#.#####") + ',"tp":' + str.tostring(tp, "#.#####") + ',"sl":' + str.tostring(sl, "#.#####") + ',"comment":"Keltner Channel Reversal"}'

...

alert(metaViewAlert("Open", "buy", sl, close, tp), alert.freq_once_per_bar_close)
alert(metaViewAlert("Modify", "", trailPrice), alert.freq_once_per_bar_close)
alert(metaViewAlert("Close", ""), alert.freq_once_per_bar_close)
```
