#!/usr/bin/env python
# coding: utf-8

# In[1]:

# Variables
SYMBOL = "MATICUSDT"
INTERVAL = "5m"
RSI_ENTER = 26
D_DIFF = 0.045
K_ENTER = 0.25
RSI_EXIT = 74
RSI_WINDOW = 14
STOCH_SMA = 3
REWARD = 1.06
RISK = 0.98
LIMIT_ORDER = 0.98
MINUTES = 300
QUANTITY = 1000


import pandas as pd
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import time
import ta 
import warnings
warnings.simplefilter("ignore")


# In[2]:


load_dotenv()


# In[3]:


#Loading my Bybit's API keys from the dotenv file
api_key_pw = os.getenv('api_key_bot_IP')
api_secret_pw = os.getenv('api_secret_bot_IP')
sender_pass = os.getenv('mail_key')
receiver_address = os.getenv('mail')

# In[4]:


#Establishing Connection with the API (SPOT)
from pybit import spot
session_auth = spot.HTTP(
    endpoint='https://api.bybit.com',
    api_key = api_key_pw,
    api_secret= api_secret_pw
)

#Establishing Connection with the API (FUTURES)
from pybit import usdt_perpetual
session = usdt_perpetual.HTTP(
    endpoint='https://api.bybit.com',
    api_key = api_key_pw,
    api_secret= api_secret_pw
)


# In[5]:


#This function gets Real MATIC Price Data and creates a smooth dataframe that refreshes every 5 minutes
def get5minutedata():
    frame = pd.DataFrame(session_auth.query_kline(symbol=SYMBOL, interval=INTERVAL)["result"])
    frame = frame.iloc[:,: 6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index, unit="ms")
    frame = frame.astype(float)
    return frame


# In[6]:


#Function to apply some technical indicators from the ta library
def apply_technicals(df):
    df["K"] = ta.momentum.stochrsi(df.Close, window= RSI_WINDOW)
    df["D"] = df["K"].rolling(STOCH_SMA).mean()
    df["RSI"] = ta.momentum.rsi(df.Close, window = RSI_WINDOW)
    df.dropna(inplace=True)



# In[7]:


class Signals:
    def __init__(self, df, lags):
        self.df = df
        self.lags = lags
    
    #Checking if we have a trigger in the last n time steps
    def get_trigger(self):
        df_2 = pd.DataFrame()
        for i in range(self.lags + 1):
            mask = (self.df["RSI"].shift(i) < RSI_ENTER)
            df_2 = df_2.append(mask, ignore_index = True)
        return df_2.sum(axis= 0)
    
    # Is the trigger fulfilled and are all buying conditions fulfilled?
    def decide(self):
         self.df["trigger"] = np.where(self.get_trigger(), 1, 0)
         self.df["Buy"]= np.where((self.df.trigger) &
                                    (self.df["K"] < K_ENTER) &
                                    (self.df["K"] > self.df["D"] + D_DIFF), 1, 0)



# In[8]:


#The sender mail address and password
sender_address = 'pythontradingbot11@gmail.com'

#Function to automate mails
def send_email(subject, result = None, buy_price = None, exit_price = None, stop = None):
    content = ""
    if result is not None:
      content += f"Result: {result}\n"
    if buy_price is not None:
      content += f"Buy Price: {buy_price}\n"
    if exit_price is not None:
      content += f"TP Price: {exit_price}\n"
    if stop is not None:
      content += f"SL Price: {stop}\n"

    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject 
    message.attach(MIMEText(content, 'plain'))
    
    #Create SMTP session for sending the mail
    session_mail = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session_mail.starttls()  # enable security
    session_mail.login(sender_address, sender_pass)
    text = message.as_string()
    session_mail.sendmail(sender_address, receiver_address, text)
    session_mail.quit()


# In[9]:


def strategy_long(qty = QUANTITY, open_position = False):
    df= get5minutedata()
    apply_technicals(df)
    inst = Signals(df, 1)
    inst.decide()
    print(f'Current Time is ' + str(df.index[-1]))
    print(f'Current Close is '+str(df.Close.iloc[-1]))
    print(f"RSI: {round(df.RSI.iloc[-1], 2)}    K: {round(df.K.iloc[-1], 2)}    D: {round(df.D.iloc[-1], 2)}")
    print("-----------------------------------------")
    

    if df.Buy.iloc[-1]:
        price = round(df.Close.iloc[-1],4)
        buyprice_limit = round(price * LIMIT_ORDER,4)
        tp = round(buyprice_limit * REWARD,4)
        sl = round(buyprice_limit * RISK,4)
        send_email(subject = f"{SYMBOL} Open Long Limit Order", buy_price=buyprice_limit, exit_price=tp, stop=sl)
        
        print("-----------------------------------------")

        print(f"Buyprice: {buyprice_limit}")

        print("-----------------------------------------------------------------------------------------------------------------------------------------------")

        order = session.place_active_order(symbol=SYMBOL,
                                            side="Buy",
                                            order_type="Limit",
                                            qty= qty,
                                            price = buyprice_limit,
                                            time_in_force="GoodTillCancel",
                                            reduce_only=False,
                                            close_on_trigger=False,
                                            take_profit = tp,
                                            stop_loss = sl)
        print(order)

        matic_order_id = str(order['result']['order_id'])
        print("-----------------------------------------------------------------------------------------------------------------------------------------------")
        print(f"Order id: {matic_order_id}") 
        print("---------------------------------------------------")

        # Set the expiration time for the order (300 mins from now)
        expiration_time = int(time.time()) + (MINUTES*60)

        # Wait until the expiration time
        while int(time.time()) < expiration_time:
            # Sleep for 10 seconds before checking the order status again
            time.sleep(10)
            # Update time_runner
            time_runner = int((expiration_time - int(time.time()))/ 60)
            # Check the status of the order
            order_info = session.get_active_order(symbol= SYMBOL)
            order_status = str(order_info['result']["data"][0]['order_status'])
            print(f'Order Status: {order_status}')
            print(f'Time (mins) remaining for the order to be filled : {time_runner}')
            print("--------------------------------------------------------------------")

            # If the order has been filled or cancelled, exit the loop
            if order_status in ["Filled"]:
                open_position = True
                send_email(subject=f"{SYMBOL} Limit Order Activated")
                break
            elif order_status in ["Cancelled"]:
                open_position = False 
                send_email(subject=f"{SYMBOL} Order cancelled manually")
                break
            
        
        else:
            order_info = session.get_active_order(symbol= SYMBOL)
            order_status = str(order_info['result']["data"][0]['order_status'])
            print(order_status)
            print("----------------------------------------------------------------------")

            if order_status not in ["Filled"]: 
                try:
                    cancel_order = session.cancel_all_active_orders(symbol= SYMBOL)
                    print(cancel_order)
                    send_email(subject= f"{SYMBOL} Limit Order desactivated...")
                    open_position= False
                    
                except: 
                    print("No orders need to be cancelled")

    while open_position:
        time.sleep(10)
        df = get5minutedata()
        apply_technicals(df)
        current_price = round(df.Close.iloc[-1], 2)
        current_profit = round((current_price-buyprice_limit) * qty, 2)
        print(f"Buyprice: {buyprice_limit}" + '             Close: ' + str(df.Close.iloc[-1]))
        print(f'Target: ' + str(tp) + "                Stop: " + str(sl))
        print(f"RSI: {round(df.RSI.iloc[-1], 2)}       K: {round(df.K.iloc[-1], 2)}       D: {round(df.D.iloc[-1], 2)}")
        print(f'RSI Target: {RSI_EXIT}')
        print(f"K > D: {round(df.K.iloc[-1], 2) > round(df.D.iloc[-1], 2)}")
        print(f'Current Profit : {current_profit}')
        print("---------------------------------------------------")

        if current_price <= sl: 
            result = round((sl - buyprice_limit) * qty,2)
            print("Closed Position")
            send_email(subject=f"{SYMBOL} Long SL", result = result, buy_price=buyprice_limit, stop= sl)
            open_position = False
            exit()
        
        elif current_price >= tp:
            result= round((tp - buyprice_limit) * qty, 2)
            print("Closed Position")
            send_email(subject =f"{SYMBOL} Long TP", result = result, buy_price=buyprice_limit, exit_price= tp)
            open_position = False
            break

        elif df.RSI[-1] > RSI_EXIT:
            
            try:
                print(session.place_active_order(symbol=SYMBOL,
                                                side="Sell",
                                                order_type="Market",
                                                qty= qty,
                                                time_in_force="GoodTillCancel",
                                                reduce_only=True,
                                                close_on_trigger=False)) 
                print("--------------------")  
                rsi_exit_price = round(df.Close.iloc[-1],4)
                result= round((rsi_exit_price - buyprice_limit)*qty, 2)           
                print("Closed position")
                send_email(subject = f"{SYMBOL} Long Closed - RSI > {RSI_EXIT}", result=result, buy_price=buyprice_limit, exit_price= rsi_exit_price)
                open_position = False
                break
            
            except: 
                print("Position already closed")
                send_email(subject="Position already Closed")             
                break

# In[10]:


while True: 
    strategy_long(QUANTITY)
    time.sleep(120)