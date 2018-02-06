import sys
import os

# Problem is, given a set of stocks, allocation, start and end date, maximize by Sharpe Ratio
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