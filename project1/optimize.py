import sys
import os
import pandas as pd

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



# Problem is, given a set of stocks, start and end date, maximize by Sharpe Ratio
def run_simulation():
    startDate = "2010-02-01"
    endDate = "2012-02-01"

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

        print(symbols)

if __name__ == "__main__":
    run_simulation()