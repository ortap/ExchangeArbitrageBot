import json
import requests
import hmac
import hashlib
import time
import os
try:
    from urllib import urlencode
except ImportError:  # for compatibility with py3
    from urllib.parse import urlencode


class Exchange:

    def __init__(self):
        self.API_URL = 'https://www.binance.com/api/v1'
        self.API_URL_V3 = 'https://www.binance.com/api/v3'
        self.API_KEY = os.environ['BINANCE_API_KEY']  #
        self.API_SECRET = os.environ['BINANCE_API_SECRET']  #
        self.feeRatio = 0.001

    def unauthenticated_request(self, method, URL, body={}):
        query = urlencode(body)
        url = "%s?%s" % (URL, query)
        return requests.request(method, url, timeout=30, verify=True).json()

    def signOrder(self, body={}):
        data = body.copy()

        ts = str(int(1000 * time.time()))
        data.update({"timestamp": ts})

        h = urlencode(data)
        b = bytearray()
        b.extend(self.API_SECRET.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'),
                             digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data

    def authenticated_request(self, method, URL, body={}):
        body.update({"recvWindow": 120000})
        query = urlencode(self.signOrder(body))
        url = URL + "?" + query
        header = {"X-MBX-APIKEY": self.API_KEY}
        return requests.request(method, url, headers=header,
                                timeout=30, verify=True).json()

    def get_ticker_history(self, tokenpair):
        path = "%s/historicalTrades" % self.API_URL
        body = {"symbol": tokenpair, "limit": 50}
        return self.unauthenticated_request('GET', path, body)

    def get_trades(self, tokenpair):
        path = "%s/trades" % self.API_URL
        body = {"symbol": tokenpair, "limit": 50}
        return self.unauthenticated_request('GET', path, body)

    def get_candlesticks(self, tokenpair):
        path = "%s/klines" % self.API_URL
        body = {"symbol": tokenpair}
        return self.unauthenticated_request('GET', path, body)

    def get_ticker_lastPrice(self, tokenpair):
        path = "%s/ticker/allPrices" % self.API_URL
        body = {"symbol": tokenpair}
        return self.unauthenticated_request('GET', path, body)

    def get_ticker_order_book(self, tokenpair):
        path = "%s/depth" % self.API_URL
        body = {"symbol": tokenpair, "limit": 50}
        order_book = self.unauthenticated_request('GET', path, body)
        # order_book = json.loads(ob_request)
        return order_book

    def get_ticker_orderBook_innermost(self, tokenpair):
        orderBook = self.get_ticker_order_book(tokenpair)
        bestbid = [float(orderBook['bids'][0][0]),
                   float(orderBook['bids'][0][1])]
        bestask = [float(orderBook['asks'][0][0]),
                   float(orderBook['asks'][0][1])]
        return bestbid, bestask

    def get_user_history(self, tokenpair):
        path = "%s/allOrders" % self.API_URL_V3
        body = {"symbol": tokenpair}
        return self.authenticated_request('GET', path, body)

    def get_account(self):
        path = self.API_URL_V3 + "/account"
        return self.authenticated_request('GET', path, {})

    def get_balance(self, tokensymbol):
        balances = self.get_account()
        balances['balances'] = {item['asset']: item for item in balances['balances']}
        return balances['balances'][tokensymbol]['free']

    def place_order(self, tokenpair, side, amount, price=None):
        path = "%s/order" % self.API_URL_V3
        body = {}

        if price is not None:
            body["type"] = "LIMIT"
            price = "{:.8f}".format(price)
            body["price"] = price
            body["timeInForce"] = "GTC"
        else:
            body["type"] = "MARKET"

        body["tokenpair"] = tokenpair
        body["side"] = side
        body["amount"] = '%.8f' % amount
        return self.authenticated_request('POST', path, body)

    def cancel_order(self, tokenpair, orderId):
        path = "%s/order" % self.API_URL_V3
        body = {"symbol": tokenpair, "orderId": orderId}
        return self.authenticated_request('DELETE', path, body)

    def get_open_orders(self, tokenpair):
        path = "%s/openOrders" % self.API_URL_V3
        body = {'symbol': tokenpair}
        open_orders = self.authenticated_request('GET', path, body)
        openOrders = json.loads(open_orders.text)
        return openOrders

    def cancel_allOrders(self):
        tokenpairs = ['ZRXETH', 'REPETH', 'GNTETH']
        openOrders = self.get_open_orders()
        for i in range(len(tokenpairs)):
            tokenpair = tokenpairs[i]
            for j in range(len(openOrders)):
                orderId = openOrders[j]['orderId']
                cancelorder = self.cancel_order(tokenpair, orderId)
                return cancelorder
            return tokenpair
        print('All open orders successfully canceled for the defined tokenpairs')


if __name__ == "__main__":
    binance = Exchange()
    print(binance.get_ticker_orderBook_innermost('ZRXETH'))
    ###
