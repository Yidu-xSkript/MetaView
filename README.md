# mt5hook
I Use NGROK to generate link in order to execute my trades for now. but you can just buy a vpn server and use it.
The way you use it on TradingView will be by adding this type of alert
Execute Trades (Buy, Sell):
-> Alert()
metaViewAlert(string mode, string dxn, float sl=-1, float entry_price=-1, float tp=-1) =>
    '{"symbol":"' + syminfo.ticker + '","orderMode":"' + mode + '","orderType":"' + dxn + '_stop"' + ',"orderAction":"pending_order","entry_price":' + str.tostring(entry_price, "#.#####") + ',"tp":' + str.tostring(tp, "#.#####") + ',"sl":' + str.tostring(sl, "#.#####") + ',"comment":"Keltner Channel Reversal"}'
