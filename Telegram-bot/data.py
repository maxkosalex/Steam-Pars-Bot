import sqlite3
import json
import datetime


def calculate_info():
    conn = sqlite3.connect('../steam_links.db')
    cursor = conn.cursor()

    items = cursor.execute('''SELECT 
        link, 
        MIN(price) AS min_price, 
        count,
        name
    FROM 
        CSMoney
    WHERE 
        count > 3 AND date = ?
    GROUP BY 
        count 
    HAVING 
        COUNT(*) = 1 OR MIN(price) = price''',(datetime.datetime.now().strftime('%Y-%m-%d'),)).fetchall()
    info = []
    for i in items:

        a = cursor.execute(f"SELECT json FROM MarketPlace WHERE link = '{i[0]}'").fetchone()

        if a is not None and isinstance(a, tuple):

            json_string = a[0]

            if json_string is not None:
                #print(i[0])
                #print(i[3])
                data = json.loads(json_string)

                # Доступ к различным частям данных
                buyer_data = data.get("Buyer")[0]
                seller_data = data.get("Seller")[0]

                price = i[1]
                count = i[2]

                procent = round(((buyer_data[0]-price)/price)*100, 4)

                # Выводим результаты
                #print(f"купить за {price} в кол-ве {count}\nПродается за {seller_data[0]} в кол-ве {seller_data[1]}, покупается за {buyer_data[0]} в кол-ве {buyer_data[1]}\nВыгода:{procent}%")
                info += [f"{i[0]}\n{i[3]}\nКупить за ${price} в кол-ве {count} на CS.Market\nПродается за ${seller_data[0]} в кол-ве {seller_data[1]}, покупается за ${buyer_data[0]} в кол-ве {buyer_data[1]} на Steam Market\nВыгода:{procent}%"]

            else:
                pass#print("Ошибка: строка JSON является None.")
        else:
            pass#print("Ошибка: результат запроса является None или не является кортежем.") #Означает то, что предмета нет в наличии

    return info
