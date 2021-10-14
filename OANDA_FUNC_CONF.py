#!/usr/bin/env python
# coding: utf-8

# # Oanda FUNC 

from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.accounts as accounts
import requests
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import argrelmax, argrelmin
import pickle
import pandas as pd
import json


#get_ipython().run_line_magic('matplotlib', 'inline')


accountID = '101-011-15612193-001'
access_token = '2897d1ae787989d30996a8a9d0a2c03d-7304ab578b56ccb454d311ecbc90cfdb'
api = API(access_token=access_token, environment="practice")

#accountID = '001-011-4552395-001'
#access_token = 'd0d8f6874507f43902f7f30de35b7464-c5d19825c0a11a8e211d9b7f6fa0eb86'
#api = API(access_token=access_token, environment = "live")

class Data:

    def __init__(self, span, count, value="c"):
        params = {
          "count": count,
          "granularity": span
        }
        r = instruments.InstrumentsCandles(instrument="USD_JPY", params=params)
        res = api.request(r)
        self.y = []
        self.x = []
        self.t = []
        for n, can in enumerate(res['candles']):
            cvalue = float(res['candles'][n]['mid'][value])                        #CからLへ
            self.y.append(cvalue)
            self.x.append(n)
            self.t.append(res['candles'][n]['time'])
            
    def bband(self, window=25):
        
        # ボリンジャーバンド追加
        bb = pd.DataFrame({"raw" : self.y})
        bb['time'] = self.t
        bb['mean'] = bb['raw'].rolling(window).mean()         # S30 nara window120 S14 de 240 he
        bb['std'] = bb['raw'].rolling(window).std()
        bb['upper3'] = bb['mean'] + (bb['std'] * 3)
        bb['upper'] = bb['mean'] + (bb['std'] * 2)
        bb['upper1'] = bb['mean'] + (bb['std'] * 1)         # backtest 1.5でついか
        bb['lower1'] = bb['mean'] - (bb['std'] * 1)         # backtest 1.5でついか
        bb['lower'] = bb['mean'] - (bb['std'] * 2)              
        bb['lower3'] = bb['mean'] - (bb['std'] * 3)             #3から2.9へ
#         bb = bb.iloc[window:,:]
#         bb = bb.reset_index()
        return bb
    
    def macd(self):
    
        # MACDの計算を行う
        macd = pd.DataFrame({"raw" : self.y})
        macd['ema_12'] = macd['raw'].ewm(span=12).mean()
        macd['ema_26'] = macd['raw'].ewm(span=26).mean()
        macd['macd'] = macd['ema_12'] - macd['ema_26']
        macd['signal'] = macd['macd'].ewm(span=9).mean()
        return macd
    
    def rsi(self):
        rsi = pd.DataFrame({"raw" : self.y})
        ##差分を計算する
        diff = rsi.diff()
        ## 値上がり幅、値下がり幅をシリーズへ切り分け
        up, down = diff.copy(), diff.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        # 値上がり幅/値下がり幅の単純移動平均（14)を処理
        up_sma_14 = up.rolling(window=14, center=False).mean()
        down_sma_14 = down.abs().rolling(window=14, center=False).mean()
        # 値上がり幅/値下がり幅の単純移動平均（14)を処理
        up_sma_14 = up.rolling(window=14, center=False).mean()
        down_sma_14 = down.abs().rolling(window=14, center=False).mean()
        # RSIの計算
        RS = up_sma_14 / down_sma_14
        RSI = 100.0 - (100.0 / (1.0 + RS))
        ##最初の数値がNanで欠損してしまうので削除する
        #diff_data = diff[1:]
        rsi["rsi"] = RSI
        rsi["70"] = 70
        rsi["30"] = 30
        return rsi

class History:

    def __init__(self, span, count, _from, value="c"):
        params = {
          "alignmentTimezone": "Japan",
          "from": _from,
          "count": count,
          "granularity": span
        }
        r = instruments.InstrumentsCandles(instrument="USD_JPY", params=params)
        res = api.request(r)
        self.y = []
        self.x = []
        self.t = []
        for n, can in enumerate(res['candles']):
            cvalue = float(res['candles'][n]['mid'][value])                        #CからLへ
            self.y.append(cvalue)
            self.x.append(n)
            self.t.append(res['candles'][n]['time'])
       
            
    def bband(self, window=25):
        
        # ボリンジャーバンド追加
        bb = pd.DataFrame({"raw" : self.y})
        bb['time'] = self.t
        bb['mean'] = bb['raw'].rolling(window).mean()         # S30 nara window120 S14 de 240 he
        bb['std'] = bb['raw'].rolling(window).std()
        bb['upper3'] = bb['mean'] + (bb['std'] * 3)
        bb['upper'] = bb['mean'] + (bb['std'] * 2)
        bb['upper1'] = bb['mean'] + (bb['std'] * 1)         # backtest 1.5でついか
        bb['lower1'] = bb['mean'] - (bb['std'] * 1)         # backtest 1.5でついか
        bb['lower'] = bb['mean'] - (bb['std'] * 2)              
        bb['lower3'] = bb['mean'] - (bb['std'] * 3)             #3から2.9へ
#         bb = bb.iloc[window:,:]
#         bb = bb.reset_index()
        return bb
    
    def macd(self):
    
        # MACDの計算を行う
        macd = pd.DataFrame({"raw" : self.y})
        macd['ema_12'] = macd['raw'].ewm(span=12).mean()
        macd['ema_26'] = macd['raw'].ewm(span=26).mean()
        macd['macd'] = macd['ema_12'] - macd['ema_26']
        macd['signal'] = macd['macd'].ewm(span=9).mean()
        return macd
    
    def rsi(self):
        rsi = pd.DataFrame({"raw" : self.y})
        ##差分を計算する
        diff = rsi.diff()
        ## 値上がり幅、値下がり幅をシリーズへ切り分け
        up, down = diff.copy(), diff.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        # 値上がり幅/値下がり幅の単純移動平均（14)を処理
        up_sma_14 = up.rolling(window=14, center=False).mean()
        down_sma_14 = down.abs().rolling(window=14, center=False).mean()
        # 値上がり幅/値下がり幅の単純移動平均（14)を処理
        up_sma_14 = up.rolling(window=14, center=False).mean()
        down_sma_14 = down.abs().rolling(window=14, center=False).mean()
        # RSIの計算
        RS = up_sma_14 / down_sma_14
        RSI = 100.0 - (100.0 / (1.0 + RS))
        ##最初の数値がNanで欠損してしまうので削除する
        #diff_data = diff[1:]
        rsi["rsi"] = RSI
        rsi["70"] = 70
        rsi["30"] = 30
        return rsi

        
        
def plotting(bdf_list, rdf_list, mdf_list):
    t = time.localtime()
    current_time = time.strftime("%b%d, %H:%M:%S", t)
    # fig initialize
    fig = plt.figure(figsize=(36, 24)) #figsize=(12, 8) inchi size
    fig.suptitle(current_time, fontsize=12)
    
    #add_subplot()でグラフを描画する領域を追加する．引数は行，列，場所
    ax1 = fig.add_subplot(3, 3, 1)
    ax2 = fig.add_subplot(3, 3, 4)
    ax3 = fig.add_subplot(3, 3, 7)
    ax4 = fig.add_subplot(3, 3, 2)
    ax5 = fig.add_subplot(3, 3, 5)
    ax6 = fig.add_subplot(3, 3, 8)
    ax7 = fig.add_subplot(3, 3, 3)    
    ax8 = fig.add_subplot(3, 3, 6)
    ax9 = fig.add_subplot(3, 3, 9)
    bax_list = [ax1,ax4,ax7 ]
    rax_list = [ax2, ax5, ax8]
    max_list = [ax3, ax6, ax9]
    
    
    # まずはbb
    for df, ax in zip(bdf_list,bax_list):
        
        ax.plot(df[['raw', 'mean', 'upper', 'lower', 'upper3', 'lower3']])
        ax.set_title('bb')
        # Show the major grid lines with dark grey lines
        ax.grid(b=True, which='major', color='#666666', linestyle='-')
        # Show the minor grid lines with very faint and almost transparent grey lines
        ax.minorticks_on()
        ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        
    # rsi
    for df, ax in zip(rdf_list, rax_list):
        ax.plot(df[['rsi', '30', '70']])
        ax.set_title('rsi')
        ax.minorticks_on()
        ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        
    # macd
    for df, ax in zip(mdf_list, max_list):
        ax.plot(df[[ 'ema_12', 'ema_26', ]]) # 'macd', 'signal'
        ax.set_title('macd')
        ax.minorticks_on()
        ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    
    # プロット表示(設定の反映)
    plt.tight_layout()
    #plt.show(block=False) # if want to show everytime
    fig.savefig("img.png")
    #debug memory error
    plt.close(fig)
    


# # legend FUNCTION


    
def ma(data, n):
    # n 移動平均の点数
    data = np.array(data)
    # コンボリューション積分で移動平均の計算
    ave = np.convolve(data, np.ones(n)/float(n), mode='valid') #valid, same, full
    
    return ave

def short(price, tp, order_condition):
    if tp > 0.035:
        sl = 0.035
    else:
        sl = 0.025
    TP = price - tp
    TP = '{:.3f}'.format(TP)
    SL = price + sl # original 0.004
    SL = '{:.3f}'.format(SL)
    
    data = {
        "order": {
            "instrument": "USD_JPY",
            "units": "-200000",
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "takeProfitOnFill":{
                "timeInForce": "GTC",
                "price": TP    
            },
            "stopLossOnFill": {
                "timeInForce": "GTC",
                "price": SL
            },
        }
    }
    r = orders.OrderCreate(accountID, data=data)
    res = api.request(r)
    #end order original
    
    # after order process
    long_short = "short"
    ordered_price = res['orderFillTransaction']['price']
    order_id = res['orderFillTransaction']['id']
    
    return order_id, long_short, ordered_price, order_condition

def long(price, tp, order_condition):
    # order original 
    if tp > 0.035:
        sl = 0.033
    elif tp < 0.02:
        sl = 0.02
    else:
        sl = 0.024
    TP = price + tp
    TP = '{:.3f}'.format(TP)
    SL = price-sl # original 0.004
    SL = '{:.3f}'.format(SL)
    data = {
        "order": {
            "instrument": "USD_JPY",
            "units": "+200000",
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "takeProfitOnFill":{
                "timeInForce": "GTC",
                "price": TP
            },
            "stopLossOnFill": {
                "timeInForce": "GTC",
                "price": SL
            },
        }
    }
    r = orders.OrderCreate(accountID, data=data)
    res = api.request(r)
    #end order original
    
    # after order process
    long_short = "long"
    ordered_price = res['orderFillTransaction']['price']
    order_id = res['orderFillTransaction']['id']
    
    return order_id, long_short, ordered_price, order_condition



if __name__ == "__main__":
    def use_all():
        a = Data("M5",200)
        ab = a.bband()
        ar = a.rsi()
        am = a.macd()

        b = Data("M15",200)
        bb = b.bband()
        br = b.rsi()
        bm = b.macd()

        c = Data("D", 120)
        cb = c.bband(window=25)
        cr = c.rsi()
        cm = c.macd()

        b = [ab,bb,cb]
        r = [ar,br,cr]
        m = [am,bm,cm]

        plotting(b,r,m)

        
    def use_one():
        t = Data("M10",2000)
        tb = t.bband()
        tr = t.rsi()
        tm = t.macd()

        fig = plt.figure(figsize=(64, 16)) #figsize=(12, 8) inchi size
        #add_subplot()でグラフを描画する領域を追加する．引数は行，列，場所
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        ax1.plot(tb[['raw', 'mean', 'upper', 'lower', 'upper3', 'lower3']])
        ax1.set_title('bb')
        # Show the major grid lines with dark grey lines
        ax1.grid(b=True, which='major', color='#666666', linestyle='-')
        # Show the minor grid lines with very faint and almost transparent grey lines
        ax1.minorticks_on()
        ax1.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        ax2.plot(tr[['rsi', '30', '70']])
        ax2.set_title('rsi')
        ax2.minorticks_on()
        ax2.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.tight_layout()
        plt.show(block=False) # if want to show everytime
        #fig.savefig("img.png")
        #debug memory error
        plt.close(fig)


# In[ ]:


# use age
# use_one()


# In[ ]:





# In[ ]:




