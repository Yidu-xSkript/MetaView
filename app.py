# app.py

from flask import Flask, request
from flask_ngrok import run_with_ngrok
from _mt5 import login, order, modifyOrder, closeOrder

app = Flask(__name__)
run_with_ngrok(app)

@app.route('/webhook/order', methods=['POST'])
def openTradeWebhook():
    print(request.data)
    if request.method == 'POST':
        if login():
            if request.json['orderMode'] == "Open":
                order(request.json['symbol'], request.json['orderAction'], request.json['orderType'], float(request.json['entry_price']), float(request.json['tp']), float(request.json['sl']), request.json['comment'])
            elif request.json['orderMode'] == "Close":
                closeOrder(request.json['symbol'])
            elif request.json['orderMode'] == "Modify":
                modifyOrder(request.json['symbol'], float(request.json['sl']), float(request.json['tp']))
        
        return "Webhook recieved"

if __name__ == "__main__":
    app.run(port=5000)