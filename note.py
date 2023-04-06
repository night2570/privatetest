import numpy as np
import ccxt, time, math, os

def get_market_select():
    markets = exchange.load_markets()
    markets_USDT = markets.copy()

    for m_key in markets.keys():
        if not m_key.endswith("USDT"):
            del (markets_USDT[m_key])

    market_value = markets_USDT.values()
    market_select_usdt = [m['id'] for m in market_value]
    market_select = []
    for m_idx in range(len(market_select_usdt)):
        if (not ('BEAR' in market_select_usdt[m_idx])) and (not ('BULL' in market_select_usdt[m_idx])) and (not ('UP' in market_select_usdt[m_idx])) and (not ('DOWN' in market_select_usdt[m_idx])):
            market_select.append(market_select_usdt[m_idx])
    market_select = list(set(market_select))

    quotevolume_mat = []
    for m_idx in range(len(market_select)):
        market_mm = market_select[m_idx]
        tick_info = exchange.fetch_ticker(market_mm)['info']
        try:
            quotevolume_mat.append(float(tick_info['quoteVolume']))
        except:
            quotevolume_mat.append(float(0))

    sorted_idx = np.argsort(np.array(quotevolume_mat))

    market_select_sort = np.array(market_select)[sorted_idx][::-1].tolist()

    return market_select_sort

def get_cryp_price(sim_day, num_mkt, market_select):
    cryp_price_new = np.zeros([int(sim_day * 1440), 6, num_mkt])

    for m_idx in range(num_mkt):
        symbol_id = market_select[m_idx]
        start_time = last_time + 60000
        temp_time = time.time()
        try:
            for dd in range(int(sim_day * 2)):
                price_temp = exchange.fetch_ohlcv(symbol_id, '1m', int(start_time), 720)
                price_mat = np.array(price_temp)
                start_time += 60 * 720 * 1000
                if dd == 0:
                    price_final = np.array(price_mat)
                else:
                    price_final = np.concatenate((price_final, price_mat), axis=0)

            cryp_price_new[:, :, m_idx] = price_final
        except:
            continue
        print(time.time() - temp_time)

    time_length = len(cryp_price_new)
    count_max = time_length / 720

    for mm in range(num_mkt):
        count = 0
        while cryp_price_new[count * 720, 1, mm] == cryp_price_new[0, 1, mm]:
            count += 1
            if count == count_max:
                break

        cryp_price_new[: count * 720, :, mm] = np.nan

    cryp_price_new = cryp_price_new[len(cryp_price_new)%7200, :, :]

    cryp_price = cryp_price_new

    return cryp_price

subtitle = '_till30'
exchange = ccxt.binance(config={'options': {'defaultType': 'future'}})
# market_select = market_select = np.load('market_select/markets_select_230325.npy').tolist()
market_select_sort = get_market_select()[:30]

date_idx = '230401'
subtitle = ''
device = 'cuda'

price_mat = np.load('history/' + date_idx + subtitle + '/hist_data.npz')['arr_0']
markets_select = np.load('history/' + date_idx + subtitle + '/hist_data.npz')['arr_1']

sort_idx = []
for ii in range(30):
    sort_idx.append(int(np.where(np.array(markets_select) == market_select_sort[ii])[0]))