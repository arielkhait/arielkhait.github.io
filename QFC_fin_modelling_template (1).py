import pandas as pd
import numpy as np

class Market:
    transaction_fee = 0.005
    def __init__(self) -> None:
        self.stocks = {"HydroCorp": 100, "BrightFuture": 100}

    def updateMarket(self):
        #Will be implemented during grading. 
        #This function will update the stock values to their "real" values each day.
        pass
 
class Portfolio:
    def __init__(self) -> None:
        self.shares = {"HydroCorp": 0, "BrightFuture": 0}
        self.cash = 100000

    def evaluate(self, curMarket: Market) -> float:
        valueA = self.shares["HydroCorp"] * curMarket.stocks["HydroCorp"]
        valueB = self.shares["BrightFuture"] * curMarket.stocks["BrightFuture"]

        return valueA + valueB + self.cash

    def sell(self, stock_TSLA: str, sharesToSell: float, curMarket: Market) -> None:
        if sharesToSell <= 0:
            raise ValueError("Number of shares must be positive")

        if sharesToSell > self.shares[stock_TSLA]:
            raise ValueError("Attempted to sell more stock than is available")

        self.shares[stock_TSLA] -= sharesToSell
        self.cash += (1 - Market.transaction_fee) * sharesToSell * curMarket.stocks[stock_TSLA]

    def buy(self, stock_TSLA: str, sharesToBuy: float, curMarket: Market) -> None:
        if sharesToBuy <= 0:
            raise ValueError("Number of shares must be positive")
        
        cost = (1 + Market.transaction_fee) * sharesToBuy * curMarket.stocks[stock_TSLA]
        if cost - self.cash > 0.0000001:    #This is needed because the program makes a 16 bit integer division/ multiplication mistake
            raise ValueError("Attempted to spend more cash than available")

        self.shares[stock_TSLA] += sharesToBuy
        self.cash -= cost

class Context:
    def __init__(self) -> None:
        self.price_history = {"HydroCorp": [], "BrightFuture": []}
        self.rsi_window = 5
        self.long_run_avg = 10
        self.weighting_factor = 0.01
        self.macd_short = 12
        self.macd_long = 26
        self.macd_signal_period = 9
        self.boillinger_window = 20
        self.ewa_period = 5

    def calculate_bollinger_bands(self, returns, window=20):
      rolling_mean = pd.Series(returns).rolling(window, min_periods = 1).mean()
      rolling_std = pd.Series(returns).rolling(window, min_periods = 1).std()
      upper_band = rolling_mean + 2 * rolling_std
      lower_band = rolling_mean - 2 * rolling_std
      return rolling_mean, upper_band, lower_band   

    def calculate_macd(self, data, short_period=12, long_period=26, signal_period=9):
      short_ema = data.ewm(span=short_period, adjust=False).mean()
      long_ema = data.ewm(span=long_period, adjust=False).mean()
      macd = short_ema - long_ema
      signal = macd.ewm(span=signal_period, adjust=False).mean()
      histogram = macd - signal
      return macd, signal, histogram   

    def calculate_modified_rsi(self, prices, window = 5, weighting_factor = 0.05):
      delta = prices.diff()
      gain = np.where(delta > 0, delta * weighting_factor, 0) 
      loss = np.where(delta < 0, -delta * (1 - weighting_factor), 0)
      avg_gain = pd.Series(gain).rolling(window=window, min_periods=1).mean()
      avg_loss = pd.Series(loss).rolling(window=window, min_periods=1).mean()
      rs = avg_gain / (avg_loss + 1e-10)  
      rsi = 100 - (100 / (1 + rs))
      return rsi

    def calculate_moving_average(self, data, period=10, type='SMA'): 
      if type == 'SMA': 
        return data.rolling(window=period).mean() 
      elif type == 'EMA': 
        return data.ewm(span=period, adjust=False).mean()

    def volitility(self, returns, window = 20):
      return pd.Series(returns).rolling(window, min_periods = 1).std()

def update_portfolio(curMarket: Market, curPortfolio: Portfolio, context: Context):
    #Strategy Selection
    #To Del Later
    Strat1 = False
    Strat2 = False
    Strat3 = False
    Strat4 = False
    Strat5 = True
    
    # Buy and Sell Functions
    def buy_h(indicator = True):
      max_buy_h = curPortfolio.cash/((1+curMarket.transaction_fee) * curMarket.stocks['HydroCorp'])

      if indicator and can_buy(max_buy_h,'HydroCorp'):
        curPortfolio.buy('HydroCorp', max_buy_h, curMarket)
        print('You bought shares of HydroCorp, at a price of:', curMarket.stocks['HydroCorp'])

    def buy_bf(indicator = True):
      max_buy_bf = curPortfolio.cash/((1+curMarket.transaction_fee) * curMarket.stocks['BrightFuture'])

      if indicator and can_buy(max_buy_bf,'BrightFuture'):
        curPortfolio.buy('BrightFuture', max_buy_bf, curMarket)
        print("You bought shares of BrightFuture, at a price of:", curMarket.stocks['BrightFuture'])

    def sell_h(indicator = True):
      sell_all_shares_h = curPortfolio.shares['HydroCorp'] 

      if indicator and can_sell(sell_all_shares_h, 'HydroCorp'):
        curPortfolio.sell('HydroCorp', sell_all_shares_h, curMarket)
        print("You sold shares of HydroCorp at a price of:", curMarket.stocks['HydroCorp'])
    
    def sell_bf(indicator = True):
      sell_all_shares_b = curPortfolio.shares['BrightFuture']

      if indicator and can_sell(sell_all_shares_b, 'BrightFuture'):
        curPortfolio.sell('BrightFuture', sell_all_shares_b, curMarket)
        print("You sold shares of BrightFuture, at a price of:", curMarket.stocks['BrightFuture'])

    #Can buy check
    def can_buy(shares, stock):
      "returns True if you have enough cash to make the purchase"
      return curPortfolio.cash > shares * curMarket.stocks[stock] and curPortfolio.cash > 0

    def can_sell(shares, stock):
      return shares <= curPortfolio.shares[stock] and shares > 0

    # Update Prices
    context.price_history['HydroCorp'].append(curMarket.stocks['HydroCorp'])
    context.price_history['BrightFuture'].append(curMarket.stocks['BrightFuture'])
    
    prices_h = pd.Series(context.price_history['HydroCorp'])
    returns_h = prices_h.pct_change()

    prices_bf = pd.Series(context.price_history['BrightFuture'])
    returns_bf = prices_bf.pct_change()

    #EWA Average
    ema_h_short = context.calculate_moving_average(returns_h, period = 3, type = 'EMA').iloc[-1]
    ema_bf_short = context.calculate_moving_average(returns_bf, period = 3, type = 'EMA').iloc[-1]
    ema_h_long = context.calculate_moving_average(returns_h, period = 10, type = 'SMA').iloc[-1]
    ema_bf_long = context.calculate_moving_average(returns_bf, period = 10, type = 'SMA').iloc[-1]
 
    #Boiller Bands
    boiller_h_m, boiller_h_u, boiller_h_d = context.calculate_bollinger_bands(returns_h, window = context.boillinger_window)
    boiller_bf_m, boiller_bf_u, boiller_bf_d = context.calculate_bollinger_bands(returns_bf, window = context.boillinger_window)

    #MCAD
    macd_h, signal_h, histo_h = context.calculate_macd(prices_h, context.macd_short, context.macd_long, context.macd_signal_period)
    macd_bf, signal_bf, histo_bf = context.calculate_macd(prices_bf, context.macd_short, context.macd_long, context.macd_signal_period)

    #RSI
    rsi_h = context.calculate_modified_rsi(prices_h, context.rsi_window, context.weighting_factor).iloc[-1]
    rsi_bf = context.calculate_modified_rsi(prices_bf, context.rsi_window, context.weighting_factor).iloc[-1]
    
    #Volitility
    vol_h = context.volitility(returns_h, window = 10)
    vol_bf = context.volitility(returns_bf, window = 10)

    vol_percentile_h = vol_h.quantile(0.90)
    vol_percentile_bf = vol_bf.quantile(0.90)


    #Strategy 1
    if Strat1:
      if histo_h.iloc[-1] > 0 :
        buy_indicator_h = True
        buy_h(buy_indicator_h)
      
      if histo_h.iloc[-1] < 0:
        sell_indicator_h = True
        sell_h(sell_indicator_h)

    #Strategy 2
    if Strat2:
      if len(context.price_history['HydroCorp']) == 1:
        buy_indicator_h = True
        buy_h(buy_indicator_h)

      m, u, d = context.calculate_bollinger_bands(histo_h, window = 20)
      if histo_h.iloc[-1] > u.iloc[-1]:
        buy_indicator_h = True
        buy_h(buy_indicator_h)
      if histo_h.iloc[-1] < d.iloc[-1]:
        sell_indicator_h = True
        sell_h(sell_indicator_h)

    #Strategy 3 (13.67% Return)
    if Strat3:
      if rsi_h > 70:
        buy_indicator_h = True
      if rsi_h < 30:
        sell_indicator_h = True
      if returns_h.iloc[-1] < boiller_h_d.iloc[-1]:
        print('Boillinger Band Stop Loss Activated')
        sell_indicator_h = True

    #Strategy 4 (18.14% Return)
    if Strat4:
      if rsi_bf > 80:
        buy_indicator_bf = True
        buy_bf(buy_indicator_bf)
      if rsi_bf < 20:
        sell_indicator_bf = True
        sell_bf(sell_indicator_bf)

    #Strategy 5
    if Strat5:
      high_vol_event_bf = vol_bf.iloc[-1] >= vol_percentile_bf
      high_vol_event_h = vol_h.iloc[-1] >= vol_percentile_h
      neg_returns_bf = ema_bf_short <= 0
      neg_returns_h = ema_h_short <= 0
      full_vol_h = context.volitility(returns_h, len(context.price_history['HydroCorp']))
      high_vol_full_history = full_vol_h.quantile(0.95)

      #HydroCorp Buy @ Day 1 as its the most consistent stock
      if len(context.price_history['HydroCorp']) == 1:
        buy_h()
      elif ema_h_short > 0 and curPortfolio.cash > 1:
        buy_h() 

      # if you see high momentum, volitility and positive returns, buy
      if rsi_bf > 80 and high_vol_event_bf and not neg_returns_bf: 
        sell_h()
        buy_bf()

      if full_vol_h.iloc[-1] > high_vol_full_history and neg_returns_h:
        sell_h()

      # as soon as those returns become negatve, sell
      elif neg_returns_bf:
        sell_bf()

      # Cash Vs. HydroCorp Consideration i.e. if the returns are pos. invest, else carry cash
    

    print('Returns h Today:', returns_h.iloc[-1] * 100)
    print('Returns BF Today:', returns_bf.iloc[-1] * 100)
    print(curPortfolio.evaluate(curMarket))
    

###SIMULATION###
market = Market()
portfolio = Portfolio()
context = Context()

for i in range(365):
    update_portfolio(market, portfolio, context)
    market.updateMarket()

print(portfolio.evaluate(market))



