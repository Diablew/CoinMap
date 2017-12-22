'''
Created on Dec 10, 2017

@author: Diablew
'''
#!/usr/bin/python3
import requests
import argparse
import csv
from datetime import datetime
from requests import structures

api_base_url = "https://api.coinmarketcap.com/v1/ticker/"
coin_vals = {}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    BLUE = '\x1b[0;36;40m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
        
class cols:
    opts = ['nR', 'name','symbol','rank','price_usd','24h_volume_usd','percent_change_1h',
            'percent_change_24h','percent_change_7d','market_cap_usd']
    opts_portfolio = ['nR', 'name','symbol','rank','price_usd','24h_volume_usd','percent_change_1h',
            'percent_change_24h','percent_change_7d','market_cap_usd', 'n_val', 'p_change']
    
def debugger(json_resp, verbose):
    for coin, opt in zip(json_resp, cols.opts):
        if verbose:
            print ("coin: {}\n\ncoin[{}]: {}, type({}): {})".format(coin, opt, coin[opt], coin[opt], type(coin[opt])))
        else:
            print ("coin[{}]: {}, type({}): {})".format(opt, coin[opt], coin[opt], type(coin[opt])))

def get(url):
    response = requests.get(url)
    return response.json()

def colorize(num, f, s):
    if f == 'bold':
        return bcolors.BOLD + s + bcolors.ENDC
    if num < -5:
        return bcolors.FAIL + s + bcolors.ENDC
    elif num < 0:
        return bcolors.WARNING + s + bcolors.ENDC
    elif num > 5 and num < 10:
        return bcolors.BLUE + s + bcolors.ENDC
    elif num > 10:
        return bcolors.OKGREEN + s + bcolors.ENDC
    return s
    
def print_rows(strs, row_len):
    if(len(strs) == 10):
        row = "║ {}│ {:^5} - {:^16} │ {} │ {} │ {} │ {} │ {} │ {} │ {} ║".format(strs[0], strs[1], strs[2], 
               strs[3], strs[4],strs[5], strs[6], strs[7], strs[8], strs[9])
    elif(len(strs) == 12):
        row = "║ {}│ {:^5} - {:^16} │ {} │ {} │ {} │ {} │ {} │ {} │ {} - {} │ {} ║".format(strs[0], strs[1], 
               strs[2], strs[3], strs[4], strs[5], strs[6], strs[7], strs[8], strs[9], strs[10], strs[11])
    print(row + '\n' + '-'*row_len)
    
def print_headers(args, row_len):
    print ("\n\t\t\t\t\t\t\t\t-----CoinMap------\n\n")
    if (args.coin): # specific coins selected
        print("Sorting by: {}, Reversed: {}, Limit: {}".format(args.sort_type, args.reverse, len(args.coin)))
        print("Selected Coin(s): {:}".format(args.coin))
    else:           # coinmarketcap's top 10
        print("Sorting by: {}, Reversed: {}, Limit: {}".format(args.sort_type, args.reverse, args.limit))
        print("Selected Coin(s): Top {}".format(args.limit))

    print(bcolors.HEADER + '-'*row_len)
    if args.file:
        print("║ nR  │  SYM  -       Coin       │     Price    │ Chg (1H) | Chg (1D) │ Chg (7D) │   Volume (1D)   │    Market Cap    │  Profit -  % Chg  │ oR  ║")
    else:
        print("║ nR  │  SYM  -       Coin       │     Price    │ Chg (1H) | Chg (1D) │ Chg (7D) │   Volume (1D)   │    Market Cap    │ oR  ║")
    print('-'*row_len + bcolors.ENDC) 

def print_footers(file, row_len, time_stamp, i_investment, t_profit, t_p_change, n_val, avg_p_change):
    spacing = 14*' '
    row = "Data source from coinmarketcap.com at {:}".format(time_stamp)
    if file:
        print ("Investment: {:,.2f}{}Net Value: {:,.2f}{}Total Profit - % Chg: {:,.2f} - {:.2%}{}Avg % Chg: {:.2%}\n{}".format(i_investment, spacing, n_val, spacing, t_profit, t_p_change, spacing, avg_p_change, row)) 
    else:
        print (row)
    
def cast_strs(json_resp):
    for coin in json_resp:
            coin['rank'] = int(coin['rank'])
            coin['price_usd'] = float(coin['price_usd'])
            coin['24h_volume_usd'] = float(coin['24h_volume_usd'])
            coin['percent_change_1h'] = float(coin['percent_change_1h'])
            coin['percent_change_24h'] = float(coin['percent_change_24h'])
            coin['percent_change_7d'] = float(coin['percent_change_7d']) # FIX: breaks when n > 200, sometimes less
            coin['market_cap_usd'] = float(coin['market_cap_usd'])
#================================================================================================================
#TODO:
#Store balances & transactions, calculate total earn/loss
#Read csv
#================================================================================================================
def coinmap():
    # initialize argument parser
    parser = argparse.ArgumentParser(description="A program that lists cryptocurrency data sourced from coinmarketcap.com")
    parser.add_argument("-n", "--limit", type=int, default=10, help="The number of coins to display. If not specified the default is 10")
    parser.add_argument("-s", "--sort_type", type=str, default="rank", help="Metric to sort by. If not specified the default is rank", 
                        choices=["price_usd", "rank", "market_cap_usd", "24h_volume_usd",
                                 "percent_change_1h", "percent_change_24h", "percent_change_7d",
                                 "name", "symbol"])
    parser.add_argument("-r", "--reverse", default=False, action="store_true", help="Reverse sort order")
    parser.add_argument("-c", "--coin", type=str, nargs="+", help="Name of specific coin")
    parser.add_argument("-f", "--file", help="csv transaction history")
    args = parser.parse_args()
    
    json_resp = []
    url = ""
    time_stamp = datetime.now()
    # gather data from csv if file argument is passed
    if (args.file):
        portfolio = read_csv(args.file)
        row_len = 145
    else:
        row_len = 125
    n_val = 0
    t_profit = 0.0
    t_p_change = 0.0
    avg_p_change = 0.0
    i_investment = 0.0
    p_size = 0
    # if specific coin is not specified, query list api
    if(args.coin is None):
        url = api_base_url + "?limit={:d}".format(args.limit)
        json_resp = get(url)
    else:
        urls = []
        json_resp = []
        if(args.coin[0] != 'infile' and len(args.coin) == 1):
            url = api_base_url + args.coin[0]
            json_resp = get(url)
            if 'error' in json_resp:    
                print ("url: {}\njson_resp: {}".format(url, json_resp))
                return
        else:
            # create API url list for selected coins
            for c in args.coin:
                if(c == 'infile'):
                    for c in portfolio:
                        urls.append(api_base_url  + c.lower())
                else:
                    urls.append(api_base_url + c)
                print(urls)
        for u in urls:
            json_resp.append(get(u)[0]) # returns list of dict (json)
            if 'error' in json_resp:    
                print ("url: {}\njson_resp: {}".format(get(u), json_resp))
                return
    # cast string values from JSON to correct type for sorting\
    cast_strs(json_resp)
    
    # sort compiled list by selected metric
    if args.sort_type != 'rank' and args.sort_type != 'name':
        args.reverse = not args.reverse
    sorted_list = sorted(json_resp, key=lambda x: x[args.sort_type], reverse=args.reverse)
    
    print_headers(args, row_len)
    
    for n_rank, coin in enumerate(sorted_list, start=1):
        #pass all variables to function that constructs strs array
        name = coin['name']
        symbol = coin['symbol']
        rank = int(coin['rank'])
        price_usd = float(coin['price_usd'])
        vol_usd_24h = float(coin['24h_volume_usd']) 
        percent_change_1h = float(coin['percent_change_1h'])
        percent_change_24h = float(coin['percent_change_24h'])
        percent_change_7d = float(coin['percent_change_7d'])
        market_cap_usd = float(coin['market_cap_usd'])
        
        # Calculate net value and percent change
        p_change = None
        profit = None
        if (args.file):
            if(name in portfolio):
                p_size += 1
                o_val = 0.0
                c_val = 0.0
                for t in portfolio[name]:
                    o_val += t[1] * t[2]            # amt * price paid
                    c_val += t[1] * price_usd       # amt * current price
                    #print("{}\n\t\to_val:{}\n\t\tc_val:{}".format(t, o_val, c_val))
                p_change, profit = get_p_change(o_val, c_val)
                t_profit += profit
                avg_p_change += p_change
                i_investment += o_val
                #print("profit:{}\nt_profit:{}\np_change:{}\navg_p_change: {}".format(profit, t_profit, p_change, avg_p_change))
        
        # sorting by rank or name, forward - or - num, reverse
        if ((args.sort_type == 'rank' or args.sort_type == 'name') and not args.reverse) or \
            (args.sort_type != 'rank' and args.sort_type != 'name' and args.reverse):
            n_rank_str = "{:<4}".format(n_rank)
        # sorting by rank or name, reversed - or - num, forward
        elif ((args.sort_type == 'rank' or args.sort_type == 'name') and args.reverse) or \
              (args.sort_type != 'rank' and args.sort_type != 'name'):
            n_rank_str = "{:<4}".format(len(sorted_list) - n_rank + 1)                
        # format and colorize vals 
        price_str = "${:>11,}".format(price_usd)
        p_change_1h_str = colorize(percent_change_1h, None, "{:^8.2%}".format(percent_change_1h / 100))
        p_change_24h_str = colorize(percent_change_24h, None, "{:^8.2%}".format(percent_change_24h / 100))
        p_change_7d_str = colorize(percent_change_7d, None, "{:^8.2%}".format(percent_change_7d / 100))
        vol_str = "${:>14,.0f}".format(vol_usd_24h)
        mcap_str = "${:>15,.0f}".format(market_cap_usd)
        o_rank_str = "{:<3}".format(rank)
        #n_rank_str = colorize(n_rank, 'bold', "{:^4}".format(n_rank))
        #price_str = colorize(price_usd, 'bold', "${:>12,}".format(price_usd))
        #vol_str = colorize(vol_usd_24h, 'bold', "${:>16,}".format(vol_usd_24h))
        #mcap_str = colorize(market_cap_usd, 'bold', "${:>18,}".format(market_cap_usd))
            
        
        ## TODO: Bold/highlight every other line
        #if (n_rank % 2 == 0):
        #    for i, s in enumerate(strs):
        #        if u
        #           strs[i] = bcolors.BOLD + s + bcolors.ENDC
        # store values
        coin_vals[name] = [n_rank, symbol, price_usd, percent_change_1h, percent_change_24h, percent_change_7d,                   vol_usd_24h, market_cap_usd, rank]
        ## TODO: Add investment per coin column
        if (args.file):
            profit_str = "{:<7.2f}".format(profit) if profit else " -N/A- "
            p_change_str = "{:>7.2%}".format(p_change) if p_change else " -N/A- "
            strs = [n_rank_str, symbol, name, price_str, p_change_1h_str, p_change_24h_str, p_change_7d_str, 
                    vol_str, mcap_str, profit_str, p_change_str, o_rank_str]
        else:
            strs = [n_rank_str, symbol, name, price_str, p_change_1h_str, p_change_24h_str, p_change_7d_str, 
                    vol_str, mcap_str, o_rank_str]
        print_rows(strs, row_len)
    if(args.file):
        avg_p_change /= p_size if p_size > 0 else 1
        n_val = t_profit + i_investment
        t_p_change = (n_val - i_investment)/ i_investment if i_investment > 0 else 0
    print_footers(args.file, row_len, time_stamp, i_investment, t_profit, t_p_change, n_val, avg_p_change)
    
def get_p_change(orig, curr):
    if curr > orig:     # increase / profit
        p_change = ((curr - orig) / orig)
    else:               # decrease / loss
        p_change = ((orig - curr) / orig)
    return [p_change, orig * p_change]
        
## Approach 1: make map of coin name to list of transactions then calculate totals from there
# {coin_name: [net value, net %]}
#  Ethereum    BOUGHT    1.0    730.0    Dec-13
#  curr_price = 800 -> %
# Approach 2: ->>> map coin to list of lists
# Approach 3: map coin name to list of tuples (action, quantity, price), pass list to coinmap(), calculate and 
#             display when working on selected coin
#
def read_csv(file):
    #parser = argparse.ArgumentParser(description="test read csv")   
    #parser.add_argument("-f", "--file", help="csv transaction history")
    #args = parser.parse_args()
    #with open(args.file, 'r') as f:
    with open(file, 'r') as f:
        reader = csv.reader(f)
        coins = {}
        for row in reader:
            r = row[0].split('\t')
            coin_name = r[0]
            action = r[1]
            quantity = float(r[2])
            coin_price = float(r[3])
            date = r[4]
            if (coin_name in coins):
                coins[coin_name].append((action, quantity, coin_price))
            else:
                coins[coin_name] = [(action, quantity, coin_price)]
        return coins
        
if __name__ == "__main__":
    coinmap()
    #read_csv()
