import pyupbit
import pandas as pd
import numpy as np
import time

access = "FfmG5GNkmBWZMpn9iCxdGyTf1kjPvfhtXJa5lHEW"
secret = "Ntax3A0CLxRyIrMHaxwxI7jUlxyHwwofA8Fou6f3"

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

# login
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

#autotrade
buy_list = []
sell_list = []
buy_tf = 0

while True :
    try: 

        df = pyupbit.get_ohlcv("KRW-BTC", interval="minute30", count=20)
        df = df.reset_index()

        df["UD"]=[df.loc[i,"close"]-df.loc[i-1,"close"] if i>0 else 0 for i in range(len(df))] 
        df["RSI_U"]=df["UD"].apply(lambda x: x if x>0 else 0)
        df["RSI_D"]=df["UD"].apply(lambda x: x * (-1) if x<0 else 0)
        df["RSI_AU"]=df["RSI_U"].rolling(14).mean()
        df["RSI_AD"]=df["RSI_D"].rolling(14).mean()
        df["RSI"] = df.apply(lambda x:x["RSI_AU"]/(x["RSI_AU"]+ x["RSI_AD"]) * 100,1)
        df[["UD","RSI_U","RSI_D","RSI_AU","RSI_AD","RSI"]].fillna(0, inplace=True)

        df["RSI_algo"]=np.where( (df["RSI"]>30) & (df["RSI"].shift(1)<30),"Buy", np.where((df["RSI"]<70) & (df["RSI"].shift(1)>70),"Sell","Wait"))

        current_price = pyupbit.get_current_price("KRW-BTC")
            
        if df.loc[19,"RSI_algo"] == "Buy" and buy_tf == 0: 
            krw = get_balance("KRW")
            upbit.buy_market_order("KRW-BTC", krw*0.9995)
            print('Buy')
            buy_list.append([df.loc[19,"index"], df.loc[19,"close"], current_price])
            buy_tf = 1

        elif df.loc[19,"RSI_algo"] == "Sell" and buy_tf == 1:
            btc = get_balance("BTC")
            upbit.sell_market_order("KRW-BTC", btc*0.9995)
            print('Sell')
            sell_list.append([df.loc[19,"index"], df.loc[19,"close"], current_price])
            buy_tf = 0

        else: pass
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)