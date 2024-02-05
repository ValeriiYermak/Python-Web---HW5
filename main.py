import json
import aiohttp
import asyncio
import platform
import sys
import logging
from datetime import datetime, timedelta
import aiofiles

class HttpError(Exception):
    pass

async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    raise HttpError(f'Error status: {resp.status} for {url}')
        except (aiohttp.ClientConnectionError, aiohttp.InvalidURL) as err:
            raise HttpError(f'Connection error for {url}', str(err))

async def fetch_exchange_rates(index_day):
    d = datetime.now() - timedelta(days=int(index_day))
    shift = d.strftime('%d.%m.%Y')
    try:
        response = await request(
            f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
        return response
    except HttpError as err:
        print(err)
        return None

def format_output(data):
    formatted_data = []
    if isinstance(data, str):
        # Перетворюємо рядок у словник
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return formatted_data

    current_date = None
    for rate in data.get('exchangeRate', []):
        if rate.get('currency') in ['EUR', 'USD']:
            currency = rate['currency']
            date = data['date']
            if date != current_date:
                formatted_data.append(date)
                current_date = date
            formatted_data.append(f"\n{{'{currency}': {{\n"
                                  f"  'sale': {rate.get('saleRateNB', 0)},\n"
                                  f"  'purchase': {rate.get('purchaseRateNB', 0)}\n}}}}")

    return formatted_data


async def main(index_day):
    try:
        formatted_data = []
        for day in range(int(index_day)):
            response = await fetch_exchange_rates(day)
            formatted_data += format_output(response)
        return formatted_data
    except HttpError as err:
        print(err)
        return None


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if len(sys.argv) != 2:
        print("Usage: python script.py <index_day>")
        sys.exit(1)

    try:
        index_day = int(sys.argv[1])
        if index_day > 10:
            raise ValueError("The quantity of days should not exceed 10.")
    except ValueError:
        print("Error: Please provide a valid value for quantity of days not more than 10.")
        sys.exit(1)

    result = asyncio.run(main(index_day))

    if result is not None:
        for entry in result:
            print(entry)
