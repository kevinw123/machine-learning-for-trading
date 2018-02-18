import sys
import os
import pandas as pd
import numpy as np
import scipy.optimize as spo

# Get daily portfolio value given daily prices for each stock in portfolio
def portfolio_values(prices, allocation, start_val=1):
    df = prices / prices.ix[0] # normalize
    df = df * allocation # multiply normalized values by allocation to each of the equities
    df = df * start_val # multiply allocated values by the start value
    port_val = df.sum(axis=1) # find entire portfolio value on each day
    return port_val


# Finds cumulative return, average daily return, standard deviation and Sharpe ratio of portfolio
def portfolio_stats(port_val, daily_rf=0, samples_per_year=252):
    cum_ret = (port_val[-1] / port_val[0]) - 1 # how much the portfolio has gone up from beginning of time to end

    # Find daily returns, needed for sharpe ratio
    daily_returns = port_val.copy()
    daily_returns = (daily_returns/daily_returns.shift(1)) - 1
    daily_returns.ix[0, 0] = 0 # set first number to 0 instead of NaN

    #average daily return
    avg_daily_ret = daily_returns.mean()
    std_daily_ret = daily_returns.std()

    #sharpe ratio
    sharpe_ratio = ((daily_returns - daily_rf).mean() / daily_returns.std()) * np.sqrt(samples_per_year)

    return cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio



# Return CSV file path given a stock symbol.
def symbol_to_path(symbol, base_dir="data"):
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))

def get_data(symbols, dates, SPY=True):
    df = pd.DataFrame(index=dates)
    # Need spy for reference
    if SPY and "SPY" not in symbols:
       symbols = ['SPY'] + symbols

    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol), index_col="Date", parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
        df_temp = df_temp.rename(columns={"Adj Close": symbol})
        df = df.join(df_temp)
        if symbol == "SPY":
            df = df.dropna(subset=["SPY"])

    return df

# Helper function for minimize
def error_optimal_allocations(allocs, prices):
    port_val = portfolio_values(prices, allocs, 1)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = portfolio_stats(port_val)
    error = sharpe_ratio * -1
    return error

# Finds optimal allocation for stock price, optimizing for Sharpe ratio
def find_optimal_allocation(portfolio_prices):
    guess = 1.0/portfolio_prices.shape[1]
    function_guess = [guess] * portfolio_prices.shape[1]
    bnds = [[0,1] for _ in portfolio_prices.columns]
    cons = ({ "type" : "eq", "fun": lambda function_guess: 1.0 - np.sum(function_guess) })
    result = spo.minimize(error_optimal_allocations, function_guess, args = (portfolio_prices,), method="SLSQP", bounds = bnds, constraints = cons, options={'disp':True})
    allocs = result.x
    return allocs

def run_optimization(symbols, start_date, end_date):
    dates = pd.date_range(start_date, end_date)
    all_prices = get_data(symbols, dates)

    portfolio_prices = all_prices[symbols]
    spy_prices = all_prices["SPY"]

    allocations = find_optimal_allocation(portfolio_prices)
    allocations = allocations / np.sum(allocations) # normalize allocations

    # get daily portfolio value
    port_val = portfolio_values(portfolio_prices, allocations)

    # Get Portfolio statistics
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = portfolio_stats(port_val)

    print(start_date)



# Problem is, given a set of stocks, start and end date, maximize by Sharpe Ratio
def run_simulation():
    start_date = "2010-02-01"
    end_date = "2012-02-01"

    symbols = ["AAPL","MSFT","YHOO","GOOG"]


    if (len(sys.argv) > 1):
        symbols = []
        for i in range(1, len(sys.argv)):
            path = "data/" + sys.argv[i] + ".csv"

            # Verify if file exists
            if not os.path.exists(path) or not os.path.isfile(path):
                print("Verify to see if symbols are in files in data folder.")
                return

            symbols.append(sys.argv[i])


    run_optimization(symbols, start_date, end_date)

if __name__ == "__main__":
    run_simulation()