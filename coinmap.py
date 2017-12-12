'''
Created on Dec 10, 2017

@author: Diablew
'''
#!/usr/bin/python3
import requests
import argparse
from datetime import datetime

apiBaseUrl = "https://api.coinmarketcap.com/v1/ticker/"
#https://api.coinmarketcap.com/v1/ticker/?limit=10

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def get(url):
    response = requests.get(url)
    return response.json()

def coinmap():
    #initialize argument parser
    parser = argparse.ArgumentParser(description="A program that lists cryptocurrency data sourced from coinmarketcap.com")
    parser.add_argument("-n", "--limit", type=int, default=10, help="The number of coins to display. If not specified the default is 10")
    parser.add_argument("-s", "--sort_type", type=str, default="rank", help="Metric to sort by. If not specified the default is rank", 
                        choices=["price_usd", "rank", "market_cap_usd", "vol_usd_24h",
                                 "percent_change_1h", "percent_change_24h", "percent_change_7d",
                                 "name", "symbol"])
    parser.add_argument("-r", "--reverse", default=False, action="store_true", help="Reverse sort order")
    parser.add_argument("-c", "--coin", type=str, nargs="+", help="Name of specific coin")
    args = parser.parse_args()
    
    json_resp = []
    url = ""
    time_stamp = datetime.now()
    #if specific coin is not specified, query list api
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
            #create API url list for selected coins
            for c in args.coin:
                urls[i] = apiBaseUrl + c
                i += 1 
            i = 0
            #create list of JSON responses for each coin
            for u in urls:
                json_resp[i] = get(u)[0] # returned list of 1
                i += 1
    #cast str keys from JSON to correct number type
    for coin in json_resp:
        coin['rank'] = int(coin['rank'])
        coin['price_usd'] = float(coin['price_usd'])
        coin['vol_usd_24h'] = float(coin['24h_volume_usd'])
        coin['percent_change_1h'] = float(coin['percent_change_1h'])
        coin['percent_change_24h'] = float(coin['percent_change_24h'])
        coin['percent_change_7d'] = float(coin['percent_change_7d'])
        coin['market_cap_usd'] = float(coin['market_cap_usd'])
 
    sorted_list = sorted(json_resp, key=lambda x: x[args.sort_type], reverse=args.reverse)
    
    print ("\n\t\t\t\t\t\t\t\t-----CoinMap------\n\n")
    print("Sorting by: {:}, Reversed: {:}, Limit: {:}".format(args.sort_type, args.reverse, args.limit))
    if (args.coin):
        print("Selected Coin(s): {:}".format(args.coin))
    else:
        print("Selected Coin(s): Top {:}".format(args.limit))
    print("""--------------------------------------------------------------------------------------------------------------------------------------------
║ nR │  SYM  -       Coin       │      Price    │ Change (1H) | Change (24H) │ Change (7D) │    Volume (24H)   │     Market Cap      │ Rank ║
--------------------------------------------------------------------------------------------------------------------------------------------""")        
    if (args.sort_type is "rank" or args.reverse): 
        n_rank = 1
    else: 
        #n_rank = sorted_list.__len__()
        n_rank = len(sorted_list)
    for coin in sorted_list:
        name = coin['name']
        symbol = coin['symbol']
        rank = int(coin['rank'])
        price_usd = float(coin['price_usd'])
        vol_usd_24h = float(coin['24h_volume_usd']) #had to recast for some reason...
        percent_change_1h = float(coin['percent_change_1h'])
        percent_change_24h = float(coin['percent_change_24h'])
        percent_change_7d = float(coin['percent_change_7d'])
        market_cap_usd = float(coin['market_cap_usd'])
        
        #colorize %chg nums 
        percent_change_1h_str = "{:^11.2%}".format(percent_change_1h / 100)
        if percent_change_1h < -5:
            percent_change_1h_str = bcolors.FAIL + percent_change_1h_str + bcolors.ENDC
        elif percent_change_1h < 0:
            percent_change_1h_str = bcolors.WARNING + percent_change_1h_str + bcolors.ENDC
        elif percent_change_1h > 10:
            percent_change_1h_str = bcolors.OKGREEN + percent_change_1h_str + bcolors.ENDC
            
        percent_change_24h_str = "{:^12.2%}".format(percent_change_24h / 100)
        if percent_change_24h < -5 :
            percent_change_24h_str = bcolors.FAIL + percent_change_24h_str + bcolors.ENDC
        elif percent_change_24h < 0 :
            percent_change_24h_str = bcolors.WARNING + percent_change_24h_str + bcolors.ENDC
        elif percent_change_24h > 10:
            percent_change_24h_str = bcolors.OKGREEN + percent_change_24h_str + bcolors.ENDC
            
        percent_change_7d_str = "{:^11.2%}".format(percent_change_7d / 100)
        if percent_change_7d < -5 :
            percent_change_7d_str = bcolors.FAIL + percent_change_7d_str + bcolors.ENDC
        elif percent_change_7d < 0 :
            percent_change_7d_str = bcolors.WARNING + percent_change_7d_str + bcolors.ENDC
        elif percent_change_7d > 10:
            percent_change_7d_str = bcolors.OKGREEN + percent_change_7d_str + bcolors.ENDC
        
        print ("║{:^4}│ {:^5} - {:^16} │ ${:>12,} │ {:} │ {:} │ {:} │ ${:>16,} │ ${:>18,} │ {:^4} ║"
               .format(n_rank, symbol, name, price_usd, percent_change_1h_str, 
                       percent_change_24h_str, percent_change_7d_str, vol_usd_24h, market_cap_usd,
                       rank))
        print("--------------------------------------------------------------------------------------------------------------------------------------------")
        #order rank
        if (args.sort_type is "rank" or args.reverse):
            n_rank += 1
        else:
            n_rank -= 1
    print("Data source from coinmarketcap.com at {:}".format(time_stamp))
    
if __name__ == "__main__":
    coinmap()
