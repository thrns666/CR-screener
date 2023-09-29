import aiohttp
import asyncio


async def exmo_exch():
    async with aiohttp.ClientSession() as session:
        base_url = 'https://api.exmo.me/v1.1/ticker'
        info_url = 'https://api.exmo.me/v1.1/payments/providers/crypto/list'
        async with session.get(base_url) as row_resp:
            resp_js = await row_resp.json()
        async with session.get(info_url) as payments_row:
            info_js = await payments_row.json()

    total_data = {
        'exch': 'exmo.com'
    }

    for coin, data in resp_js.items():
        coin_info = coin.split('_')[0]
        info = info_js.get(coin_info)
        if info and info[0]['enabled'] and info[1]['enabled']:
            total_data[coin] = {
                'buy': float(data['buy_price']),
                'sell': float(data['sell_price']),
                'volume': float(data['vol_curr']),
                'updated': data['updated'],
                'deposit': info_js[coin.split('_')[0]][0]['enabled'],
                'withdraw': info_js[coin.split('_')[0]][1]['enabled'],
                'currency_confirmation_withdraw': info_js[coin.split('_')[0]][1]['currency_confirmations']
            }
        else:
            print(coin, 'ELSE !!!WARN!!!')

    return total_data


async def kukoin_exch() -> dict:
    total_data = {
        'exch': 'kukoin.com'
    }

    async with aiohttp.ClientSession() as session:
        base_url = 'https://api.kucoin.com/api/v1/market/allTickers'
        info_url = 'https://api.kucoin.com/api/v1/currencies/'
        async with session.get(base_url) as row_resp:
            resp_js = await row_resp.json()
        async with session.get(info_url) as row_info:
            info_js = await row_info.json()
            info_js = info_js['data']

    for i in resp_js['data']['ticker']:
        coin = i['symbolName'].split('-')[0]
        for v in info_js:
            if v['name'] == coin:
                if v['isWithdrawEnabled'] and v['isDepositEnabled']:
                    total_data[i['symbolName']] = {
                        'buy': float(i['buy']),
                        'sell': float(i['sell']),
                        'volume': float(i['vol']),
                        'updated': resp_js['data']['time'],
                        'deposit': 'True',
                        'withdraw': 'True',
                        'currency_confirmation_withdraw': v['withdrawalMinFee']
                    }

    return total_data


async def bitget_exch() -> dict:
    async with aiohttp.ClientSession() as session:
        base_url = "https://api.bitget.com/api/spot/v1/market/tickers"
        info_url = 'https://api.bitget.com/api/spot/v1/public/currencies'
        async with session.get(base_url) as row_resp:
            resp_js = await row_resp.json()
        async with session.get(info_url) as info_row:
            info_js = await info_row.json()

    total_data = {
        'exch': 'bitget.com'
    }

    for i in resp_js['data']:
        for c in info_js['data']:
            if i['symbol'].startswith(c['coinName']):
                status = c['transfer']
                if c['chains']:
                    data = c['chains'][0]
                    if status == 'true':
                        if data['rechargeable'] == 'true' and data['withdrawable'] == 'true':
                            total_data[i['symbol']] = {
                                'buy': float(i['buyOne']),
                                'sell': float(i['sellOne']),
                                'volume': float(i['baseVol']),
                                'updated': i['ts'],
                                'deposit': True,
                                'withdraw': True,
                                'currency_confirmation_withdraw': data['withdrawFee']
                            }

    return total_data


async def main():
    async with asyncio.TaskGroup() as tg:
        exmo = await tg.create_task(exmo_exch())
        bitget = await tg.create_task(bitget_exch())
        kukoin = await tg.create_task(kukoin_exch())

    exch_array = [exmo, bitget, kukoin]
    messages = list()

    for exch in exch_array:
        for exch1 in exch_array:
            if exch['exch'] != exch1['exch']:
                for k, v in exch.items():
                    for k1, v1 in exch1.items():
                        if k1 in k and k != 'exch':
                            price_1 = v['buy']
                            price_2 = v1['sell']
                            spread = round((price_1 - price_2) / ((price_1 + price_2) / 2) * 100, 2)
                            mess = f'''
                            1️⃣ {exch['exch']}: {k}
                            Price buy: {v['buy']} $
                            Volume: {v['volume']} -> 
                            Withdrawal: 🟢 

                            2️⃣ {exch1['exch']}: {k1}
                            Price sell: {v1['sell']} $
                            Volume: {v1['volume']} -> 
                            Deposite: 🟢 

                            📈 Spread: {spread}% 
                            ✂️ Commission: {v1['currency_confirmation_withdraw']}'''

                            if spread > 1.75:
                                messages.append(mess)

    return messages

# Run for test
# asyncio.run(main())
