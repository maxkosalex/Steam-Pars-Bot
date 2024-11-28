from config import for_cs_money
from data import save_data_CSM, steam_links, save_data_SM
import sqlite3
from collections import defaultdict

import regex as re #Специальная библиотека для корректного преобразования " ' (кавычек) https://regex101.com/r/lmxWvC/1/
import requests
import json
import datetime
import time

cookies, headers = for_cs_money()


def main():
    get_data_from_CSMoney(50, 50.02)
    find_items_on_steam(datetime.datetime.now().strftime('%Y-%m-%d'))
    # aaa()


def get_data_from_CSMoney(min_price, max_price):

    a = 0 #счетчик страниц

    date = datetime.datetime.now().strftime('%Y-%m-%d')

    while True:

        time.sleep(1)

        params = {
            'limit': '60',  # кол-во собираемых данных за 1 запрос только 60
            'maxPrice': f'{max_price}',  # Максимальная цена в $
            'minPrice': f'{min_price}',  # Минимальная цена в $
            'offset': f'{60*a}',  # n * limit чтобы собрать данные о других предметах
            'order': 'asc',
            'priceWithBonus': '0',
            'sort': 'price',
            'withStack': 'true',
        }

        response = requests.get('https://cs.money/5.0/load_bots_inventory/730', params=params, cookies=cookies, headers=headers)

        print(a, 60*a)
        if response.json() != {"error":2}:
            a += 1
            save_on_data(response.json(), date)
        else:
            print('error')

            break


def save_on_data(json_data, date):
    item_count = defaultdict(int)
    all_items = []
    # Проход по всем элементам и подсчет повторений
    for item in json_data["items"]:
        name = item.get("fullName")
        price = item.get("price")
        steam_url = item.get("steam")

        # Ключ для словаря - кортеж (name, price)
        key = (name, price, steam_url)
        item_count[key] += 1


        # Вывод конечных результатов с одной страницы
    items = [(steam_url, name, date, count, price)
             for (name, price, steam_url), count in item_count.items()]

    save_data_CSM(items)


def find_items_on_steam(date):
    pattern = r"\(\s*(\d+)\s*\)"

    all_links = steam_links()

    for link, *_ in all_links: # "*_" - Распаковка, если нужно работать только с первым элементом

        attempt = 0

        while attempt < 5:
            print(link, attempt)
            time.sleep(10)
            response = requests.get(link, headers=headers)

            if response.status_code == 200:

                response_text = response.text

                try:
                    period_data = re.search(r'var line1=(.+);', response_text)
                    period_data = period_data.group(1)

                    data = json.loads(period_data)[-10:]

                except:
                    print("ошибка в group")
                    attempt += 1
                    break

                name_ids = re.findall(pattern, response_text)
                print(name_ids)

                for name_id in name_ids:

                    if name_id != "0":
                        attempts = 0

                        while attempts < 3:
                            try:
                                response_buy_seller = requests.get(
                                    f"https://steamcommunity.com/market/itemordershistogram?country=RU&language=russian&currency=1&item_nameid={name_id}",
                                    headers=headers)

                                buy_order = list(map(lambda x: x[:2], json.loads(response_buy_seller.text)['buy_order_graph'][:3]))
                                sell_order = list(map(lambda y: y[:2], json.loads(response_buy_seller.text)['sell_order_graph'][:3]))

                                steam_item = {"Dynamic": data,
                                              "Buyer": buy_order,
                                              "Seller": sell_order}

                                save_data_SM(link, date, json.dumps(steam_item))
                                break

                            except Exception as ex:
                                attempts += 1
                                print(attempts, ex)
                        break
                break

            else:
                print(response.status_code, " Ожидание 2 минуты")
                time.sleep(120)
                attempt += 1


def aaa():
    conn = sqlite3.connect('steam_links.db')
    cursor = conn.cursor()

    items = cursor.execute('''SELECT 
        link, 
        MIN(price) AS min_price, 
        count,
        name
    FROM 
        CSMoney
    WHERE 
        count > 3
    GROUP BY 
        count 
    HAVING 
        COUNT(*) = 1 OR MIN(price) = price''').fetchall()

    for i in items:
        print(i[0])
        a = cursor.execute(f"SELECT json FROM MarketPlace WHERE link = '{i[0]}'").fetchone()
        print(i[3])
        if a is not None and isinstance(a, tuple):

            json_string = a[0]

            if json_string is not None:

                data = json.loads(json_string)

                # Доступ к различным частям данных
                buyer_data = data.get("Buyer")[0]
                seller_data = data.get("Seller")[0]

                price = i[1]
                count = i[2]

                procent = ((buyer_data[0]-price)/price)*100

                # Выводим результаты
                print(f"купить за {price} в кол-ве {count}\nПродается за {seller_data[0]} в кол-ве {seller_data[1]}, покупается за {buyer_data[0]} в кол-ве {buyer_data[1]}\nВыгода:{procent}%")


            else:
                print("Ошибка: строка JSON является None.")
        else:
            print("Ошибка: результат запроса является None или не является кортежем.")


if __name__ == "__main__":
    main()