'''
Created on Dec 10, 2017

@author: Diablew
'''
#!/usr/bin/python3
import requests
import argparse
from datetime import datetime
from requests import structures

apiBaseUrl = "https://api.coinmarketcap.com/v1/ticker/"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
        
class cols:
    opts = ['name','symbol','rank','price_usd','24h_volume_usd','percent_change_1h',
            'percent_change_24h','percent_change_7d','market_cap_usd']
    
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
    elif num > 10:
        return bcolors.OKGREEN + s + bcolors.ENDC
    return s

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
    args = parser.parse_args()
    
    json_resp = []
    url = ""
    time_stamp = datetime.now()
    # if specific coin is not specified, query list api
    if(args.coin is None):
        url = apiBaseUrl + "?limit={:d}".format(args.limit)
        json_resp = get(url)
    else:
        if(len(args.coin) == 1):
            url = apiBaseUrl + args.coin[0]
            json_resp = get(url)
        else:
            urls = [None]*len(args.coin)
            json_resp = [None]*len(args.coin)
            i = 0
            # create API url list for selected coins
            for c in args.coin:
                urls[i] = apiBaseUrl + c
                i += 1 
            i = 0
            # create list of JSON responses for each coin
            for u in urls:
                json_resp[i] = get(u)[0] # returns list of dict (json)
                i += 1
    # cast str keys from JSON to correct number type for sorting
    for coin in json_resp:
        coin['rank'] = int(coin['rank'])
        coin['price_usd'] = float(coin['price_usd'])
        coin['24h_volume_usd'] = float(coin['24h_volume_usd'])
        coin['percent_change_1h'] = float(coin['percent_change_1h'])
        coin['percent_change_24h'] = float(coin['percent_change_24h'])
        coin['percent_change_7d'] = float(coin['percent_change_7d'])
        coin['market_cap_usd'] = float(coin['market_cap_usd'])

    # sort compiled list by selected metric
    sorted_list = sorted(json_resp, key=lambda x: x[args.sort_type], reverse=args.reverse)
    
    print ("\n\t\t\t\t\t\t\t\t-----CoinMap------\n\n")
    if (args.coin):
        print("Sorting by: {}, Reversed: {}, Limit: {}".format(args.sort_type, args.reverse, len(args.coin)))
        print("Selected Coin(s): {:}".format(args.coin))
    else:
        print("Sorting by: {}, Reversed: {}, Limit: {}".format(args.sort_type, args.reverse, args.limit))
        print("Selected Coin(s): Top {}".format(args.limit))
    print("""--------------------------------------------------------------------------------------------------------------------------------------------
║ nR │  SYM  -       Coin       │      Price    │ Change (1H) | Change (24H) │ Change (7D) │    Volume (24H)   │     Market Cap      │ Rank ║
--------------------------------------------------------------------------------------------------------------------------------------------""")        
    if (args.sort_type is "rank" or args.reverse): 
        n_rank = 1
    else: 
        n_rank = len(sorted_list)
    for coin in sorted_list:
        name = coin['name']
        symbol = coin['symbol']
        rank = int(coin['rank'])
        price_usd = float(coin['price_usd'])
        vol_usd_24h = float(coin['24h_volume_usd']) 
        percent_change_1h = float(coin['percent_change_1h'])
        percent_change_24h = float(coin['percent_change_24h'])
        percent_change_7d = float(coin['percent_change_7d'])
        market_cap_usd = float(coin['market_cap_usd'])
        
        # format and colorize vals 
        pchange_7d_str = colorize(percent_change_7d, None, "{:^11.2%}".format(percent_change_7d / 100))
        pchange_24h_str = colorize(percent_change_24h, None, "{:^12.2%}".format(percent_change_24h / 100))
        pchange_1h_str = colorize(percent_change_1h, None, "{:^11.2%}".format(percent_change_1h / 100))
        n_rank_str = colorize(n_rank, 'bold', "{:^4}".format(n_rank))
        price_str = colorize(price_usd, 'bold', "${:>12,}".format(price_usd))
        vol_str = colorize(vol_usd_24h, 'bold', "${:>16,}".format(vol_usd_24h))
        mcap_str = colorize(market_cap_usd, 'bold', "${:>18,}".format(market_cap_usd))
         
        print ("║{}│ {:^5} - {:^16} │ {} │ {} │ {} │ {} │ {} │ {} │ {:^4} ║"
               .format(n_rank_str, symbol, name, price_str, pchange_1h_str, 
                       pchange_24h_str, pchange_7d_str, vol_str, mcap_str,
                       rank))
        print("--------------------------------------------------------------------------------------------------------------------------------------------")
        # order rank
        if (args.sort_type is "rank" or args.reverse):
            n_rank += 1
        else:
            n_rank -= 1
    print("Data source from coinmarketcap.com at {:}".format(time_stamp))
    
if __name__ == "__main__":
    coinmap()
