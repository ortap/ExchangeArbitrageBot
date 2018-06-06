# Explanation of Important Methods and Definitions in theocean.py

This module contains two classes: `TokenContracts` and `Exchange`. 

## TokenContracts class

Contains a dictionary of tokens, token pairs and their contract addresses for use by methods within the `Exchange` class.

## Exchange class

Contains methods and definitions for The Ocean exchange that are required for the exchange arbitrage bot.

### ____init____ method

 - `API_URL` may change overtime and should be altered accordingly.
 - User's `API_KEY`, `API_SECRET` and `ETHEREUM_ADDRESSES` should be stored as environment variables. User may also input these variables directly (less secure).
 - `feeRatio` is defined here as 0.1% for both makers and takers. This may be altered based on user preference to include Ocean tokens, discounts and user defined tolerances.
 - a http based `web3` provider (such as parity) is required for getting wallet balances and for signing requests. An alternative signer method/function may be implemented to bypass requirement of a web3 provider.

### Snippet of theocean.py
```python
from web3 import Web3, HTTPProvider
import json
import requests
import hmac
import hashlib
import base64
import time
import os


class TokenContracts:
    ZRX = '0x6ff6c0ff1d68b964901f986d4c9fa3ac68346570'
    ETH = '0xd0a1e359811322d97991e03f863a0c30c2cf029c'
    GNT = '0xef7fff64389b814a946f3e92105513705ca6b990'
    MKR = '0x1dad4783cf3fe3085c1426157ab175a6119a04ba'
    REP = '0xb18845c260f680d5b9d84649638813e342e4f8c9'

    def ZRXETH():
        baseTokenAddress = TokenContracts.ZRX
        quoteTokenAddress = TokenContracts.ETH
        return baseTokenAddress, quoteTokenAddress

    def GNTETH():
        baseTokenAddress = TokenContracts.GNT
        quoteTokenAddress = TokenContracts.ETH
        return baseTokenAddress, quoteTokenAddress

    def REPETH():
        baseTokenAddress = TokenContracts.REP
        quoteTokenAddress = TokenContracts.ETH
        return baseTokenAddress, quoteTokenAddress

    def MKRETH():
        baseTokenAddress = TokenContracts.MKR
        quoteTokenAddress = TokenContracts.ETH
        return baseTokenAddress, quoteTokenAddress

    def GNTZRX():
        baseTokenAddress = TokenContracts.GNT
        quoteTokenAddress = TokenContracts.ZRX
        return baseTokenAddress, quoteTokenAddress

    def MKRZRX():
        baseTokenAddress = TokenContracts.MKR
        quoteTokenAddress = TokenContracts.ZRX
        return baseTokenAddress, quoteTokenAddress

    def REPZRX():
        baseTokenAddress = TokenContracts.REP
        quoteTokenAddress = TokenContracts.ZRX
        return baseTokenAddress, quoteTokenAddress

    dictionary = {
        'ZRXETH': ZRXETH,
        'GNTETH': GNTETH,
        'REPETH': REPETH,
        'MKRETH': MKRETH,
        'GNTZRX': GNTZRX,
        'MKRZRX': MKRZRX,
        'REPZRX': REPZRX
    }
    checksum_dict = {
        'ZRX': Web3.toChecksumAddress(ZRX),
        'ETH': Web3.toChecksumAddress(ETH),
        'GNT': Web3.toChecksumAddress(GNT),
        'MKR': Web3.toChecksumAddress(MKR),
        'REP': Web3.toChecksumAddress(REP)
    }


class Exchange:
    def __init__(self):
        self.API_URL = 'https://api.staging.theocean.trade/api/v0'  # 'https://api.dev.theocean.trade/api/v0'  #
        self.WEB3_URL = 'http://localhost:8545'
        self.API_KEY = os.environ['OCEAN_API_KEY']  #
        self.API_SECRET = os.environ['OCEAN_API_SECRET']  #
        self.ETHEREUM_ADDRESS = os.environ['ETHEREUM_ADDRESS']  #
        self.feeRatio = 0.001
        self.async = True
        self.web3 = Web3(HTTPProvider(self.WEB3_URL))
        self.TokenContracts = TokenContracts

    # add send requests method that do not require authentication
    # def send_request(self, URL, method):

    def authenticated_request(self, URL, method, body):
        timestamp = str(int(round(time.time() * 1000)))
        prehash = self.API_KEY + timestamp + method + json.dumps(
            body, separators=(',', ':'))
        signature = base64.b64encode(
            hmac.new(
                self.API_SECRET.encode('utf-8'),
                msg=prehash.encode('utf-8'),
                digestmod=hashlib.sha256).digest())
        headers = {
            'TOX-ACCESS-KEY': self.API_KEY,
            'TOX-ACCESS-SIGN': signature,
            'TOX-ACCESS-TIMESTAMP': timestamp
        }
        request = requests.request(method, URL, headers=headers, json=body)

        return request

    def signOrder(self, order):
        signed_order = order
        signed_order['maker'] = self.ETHEREUM_ADDRESS
        values = [
            Web3.toChecksumAddress(signed_order['exchangeContractAddress']),
            Web3.toChecksumAddress(signed_order['maker']),
            Web3.toChecksumAddress(signed_order['taker']),
            Web3.toChecksumAddress(signed_order['makerTokenAddress']),
            Web3.toChecksumAddress(signed_order['takerTokenAddress']),
            Web3.toChecksumAddress(signed_order['feeRecipient']),
            int(signed_order['makerTokenAmount']),
            int(signed_order['takerTokenAmount']),
            int(signed_order['makerFee']),
            int(signed_order['takerFee']),
            int(signed_order['expirationUnixTimestampSec']),
            int(signed_order['salt'])
        ]
        types = [
            'address', 'address', 'address', 'address', 'address', 'address',
            'uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256'
        ]
        orderHash = Web3.soliditySha3(types, values).hex()
        # print(orderHash)
        signed_order['orderHash'] = orderHash
        sig = Web3.toChecksumAddress(self.ETHEREUM_ADDRESS.lower())
        # print(sig)
        hex_signature = self.web3.eth.sign(sig, hexstr=orderHash).hex()
        # print(hex_signature)
        sig = Web3.toBytes(hexstr=hex_signature)
        v, r, s = Web3.toInt(sig[-1]), Web3.toHex(sig[:32]), Web3.toHex(
            sig[32:64])
        ecSignature = {'v': v, 'r': r, 's': s}
        signed_order['ecSignature'] = ecSignature

        signed_order['exchangeContractAddress'] = signed_order[
            'exchangeContractAddress'].lower()
        signed_order['maker'] = signed_order['maker'].lower()
        signed_order['taker'] = signed_order['taker'].lower()
        signed_order['makerTokenAddress'] = signed_order[
            'makerTokenAddress'].lower()
        signed_order['takerTokenAddress'] = signed_order[
            'takerTokenAddress'].lower()
        signed_order['feeRecipient'] = signed_order['feeRecipient'].lower()

        return signed_order

    def new_market_order(self, baseTokenAddress, quoteTokenAddress, side,
                         orderAmount, feeOption='feeInNative'):
        RESERVE_MARKET_ORDER = self.API_URL + '/market_order/reserve'
        PLACE_MARKET_ORDER = self.API_URL + '/market_order/place'
        USER_HISTORY = self.API_URL + '/user_history'

        reserve_body = {
            'walletAddress': self.ETHEREUM_ADDRESS.lower(),
            'baseTokenAddress': baseTokenAddress,
            'quoteTokenAddress': quoteTokenAddress,
            'side': side,
            'orderAmount': orderAmount,
            'feeOption': feeOption
        }
        # print(reserve_body)
        reserve_request = self.authenticated_request(RESERVE_MARKET_ORDER,
                                                     'POST', reserve_body)
        print(reserve_request.text)
        signed_order = self.signOrder(
            json.loads(reserve_request.text)['unsignedOrder'])
        market_order_ID = json.loads(reserve_request.text)['marketOrderID']

        place_body = {
            'marketOrderID': market_order_ID,
            'signedOrder': signed_order
        }

        place_request = self.authenticated_request(PLACE_MARKET_ORDER, 'POST',
                                                   place_body)
        print(place_request.text)

        history_request = self.authenticated_request(USER_HISTORY, 'GET', {})
        # print(history_request.text)
    
    def place_order(self, tokenpair, side, amount, price=None):
        func = self.TokenContracts.dictionary.get(tokenpair)
        pairaddresses = func()
        baseTokenAddress = pairaddresses[0]
        quoteTokenAddress = pairaddresses[1]
        if price is not None:
            return self.new_limit_order(baseTokenAddress, quoteTokenAddress, side,
                                       amount, price)
        elif price is None:
            return self.new_market_order(baseTokenAddress, quoteTokenAddress, side,
                                        amount)
        else:
            print('Invalid type')

    def get_user_history(self):
        USER_HISTORY = self.API_URL + '/user_history'
        history_request = self.authenticated_request(USER_HISTORY, 'GET', {})
        history = json.loads(history_request.text)
        return history

    def cancel_order(self, orderHash):
        CANCEL_ORDER = self.API_URL + '/order/' + orderHash
        delete_request = self.authenticated_request(CANCEL_ORDER, 'DELETE', {})
        # print(delete_request.text)
        print('Order successfully canceled')

    def cancel_allOrders(self):
        history = self.get_user_history()
        for i in range(len(history)):
            if int(history[i]['openAmount']) != 0:
                orderHash = history[i]['orderHash']
                self.cancel_order(orderHash)
                i += 1
            else:
                i += 1
        print('All open orders successfully canceled')

    def get_balance(self, tokensymbol):
        token_t_abi = json.loads(
            '[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'
        )
        address_tokensymbol = TokenContracts.checksum_dict.get(tokensymbol)
        token = self.web3.eth.contract(
            address_tokensymbol,
            abi=token_t_abi,
        )
        balance = token.call().balanceOf(self.ETHEREUM_ADDRESS)/10**18
        return balance

    def get_ticker_history(self, tokenpair):
        pass

    def get_ticker_lastPrice(self, tokenpair):
        func = TokenContracts.dictionary.get(tokenpair)
        pairaddresses = func()
        TICKER = self.API_URL + '/ticker'

        ticker_request = requests.get(
            TICKER,
            params={
                'baseTokenAddress': pairaddresses[0],
                'quoteTokenAddress': pairaddresses[1]
            })
        last_price = json.loads(ticker_request.text)['last']
        return last_price

    def get_ticker_orderBook(self, tokenpair):
        func = TokenContracts.dictionary.get(tokenpair)
        pairaddresses = func()
        ORDERBOOK = self.API_URL + '/order_book'
        ob_request = requests.get(
            ORDERBOOK,
            params={
                'baseTokenAddress': pairaddresses[0],
                'quoteTokenAddress': pairaddresses[1]
            })
        order_book = json.loads(ob_request.text)
        return order_book

    def get_ticker_orderBook_innermost(self, tokenpair):
        orderBook = self.get_ticker_orderBook(tokenpair)
        bestbid = [float(orderBook['bids'][0]['price']),
                   float(orderBook['bids'][0]['availableAmount'])/float(10**18)]
        bestask = [float(orderBook['asks'][0]['price']),
                   float(orderBook['asks'][0]['availableAmount'])/float(10**18)]
        return bestbid, bestask


if __name__ == "__main__":
    ocean = Exchange()
    print(ocean.get_user_history())
    print(ocean.get_ticker_orderBook_innermost('ZRXETH'))
    ###

```