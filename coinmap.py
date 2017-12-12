'''
Created on Dec 10, 2017

@author: Diablew
'''
#!/usr/bin/python3
import requests
import argparse
from datetime import datetime

apiBaseUrl = "https://api.coinmarketcap.com/v1/"
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

def coinmap():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--limit", type=int, default=10)
    parser.add_argument("-s", "--sort_type", default="rank", 
                        choices=["price_usd", "rank", "market_cap_usd", "vol_usd_24h",
                                 "percentage_change_1h", "percent_change_24h", "percent_change_7d",
                                 "name", "symbol"])
    parser.add_argument("-r", "--reverse", action="store_true", default=False)
    args = parser.parse_args()

    url = apiBaseUrl + "ticker/?limit={:d}".format(args.limit)
    resp = requests.get(url)
    time_stamp = datetime.now()
    json_resp = resp.json()
    for coin in json_resp:
        coin['rank'] = int(coin['rank'])
        coin['price_usd'] = float(coin['price_usd'])
        coin['vol_usd_24h'] = float(coin['24h_volume_usd'])
        coin['percent_change_1h'] = float(coin['percent_change_1h'])
        coin['percent_change_24h'] = float(coin['percent_change_24h'])
        coin['percent_change_7d'] = float(coin['percent_change_7d'])
        coin['market_cap_usd'] = float(coin['market_cap_usd'])
    
    sorted_list = sorted(json_resp, key=lambda x: x[args.sort_type], reverse=args.reverse)

    print ("""\n\t\t\t\t\t\t\t-----CoinMap------\n\nSorting by: {:}, Reversed: {:}, Limit: {:}
------------------------------------------------------------------------------------------------------------------------------------------
║ nR │  SYM  -      Coin      │      Price    │ Change (1H) | Change (24H) │ Change (7D) │    Volume (24H)   │     Market Cap      │ Rank ║
------------------------------------------------------------------------------------------------------------------------------------------"""
        .format(args.sort_type, args.reverse, args.limit))
    n_rank = 1
    for coin in sorted_list:
        name = coin['name']
        symbol = coin['symbol']
        rank = coin['rank']
        price_usd = coin['price_usd']
        vol_usd_24h = float(coin['24h_volume_usd'])
        percent_change_1h = coin['percent_change_1h']
        percent_change_24h = coin['percent_change_24h']
        percent_change_7d = coin['percent_change_7d']
        market_cap_usd = coin['market_cap_usd']
        
        percent_change_1h_str = "{:^11.2%}".format(percent_change_1h / 100)
        if (percent_change_1h / 100) < 0 :
            percent_change_1h_str = bcolors.FAIL + percent_change_1h_str + bcolors.ENDC
            
        percent_change_24h_str = "{:^12.2%}".format(percent_change_24h / 100)
        if (percent_change_24h / 100) < 0 :
            percent_change_24h_str = bcolors.FAIL + percent_change_24h_str + bcolors.ENDC
            
        percent_change_7d_str = "{:^11.2%}".format(percent_change_7d / 100)
        if (percent_change_7d / 100) < 0 :
            percent_change_7d_str = bcolors.FAIL + percent_change_7d_str + bcolors.ENDC
        
        print ("║{:^4}│ {:^5} - {:^14} │ ${:>12,} │ {:} │ {:} │ {:} │ ${:>16,} │ ${:>18,} │ {:^4} ║"
               .format(n_rank, symbol, name, price_usd, percent_change_1h_str, 
                       percent_change_24h_str, percent_change_7d_str, vol_usd_24h, market_cap_usd,
                       rank))
        print("------------------------------------------------------------------------------------------------------------------------------------------")
        n_rank += 1
    print("Data source from coinmarketcap.com at {:}".format(time_stamp))
    
if __name__ == "__main__":
    coinmap()