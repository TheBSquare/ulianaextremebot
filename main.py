import json
import threading
import time

import requests
from bs4 import BeautifulSoup
from telebot import TeleBot


CLEAR_TEMP_ORDERS_LIMIT = 2000
CATEGORIES = ["prikladnoe-po-23", "bazy-dannyh-25", "veb-programmirovanie-31", "internet-magaziny-61"]


def get_new_orders():
    def get_orders_from_category():
        try:
            url = f"https://www.weblancer.net/jobs/{category}/"

            response = requests.get(url)

            soup = BeautifulSoup(response.content, "html.parser")
            orders = soup.select("div.row.click_container-link.set_href")

            for order in orders:

                try:
                    order_text = order.select_one("div.collapse")

                    if order_text is None:
                        order_text = order.select_one("div.text_field")

                    yield {
                        "link": ''.join(("https://www.weblancer.net", order.find("a", {"class": "click_target"})['href'])),
                        "order_text": order_text.get_text(strip=True),
                        "listed": order.find_all("span", {"data-toggle": "tooltip"})[-1].get_text(strip=True),
                        "category": category,
                        "replies": 0
                    }
                except Exception as err:
                    yield {
                        "link": None,
                        "order_text": str(err),
                        "listed": None,
                        "category": category,
                        "replies": 0
                    }

        except Exception as err:
            yield {
                "link": None,
                "order_text": str(err),
                "listed": None,
                "category": category,
                "replies": 0
            }

    for category in CATEGORIES:
        for i in get_orders_from_category():
            yield i


def get_temp_orders():
    with open("temp_orders.json", "r") as f:
        return json.load(f)


def add_new_temp_order(order):
    data = get_temp_orders()
    data.append(order)

    with open("temp_orders.json", "w") as f:
        json.dump(data, f)


def clear_temp_orders():
    data = get_temp_orders()

    with open("temp_orders.json", "w") as f:
        json.dump(data[:CLEAR_TEMP_ORDERS_LIMIT//2], f)


def get_users():
    with open("users.json", "r") as f:
        return json.load(f)


def add_user(user):
    data = get_users()
    data.append(user)

    with open("users.json", "w") as f:
        json.dump(data, f)

    users.append(user)


bot = TeleBot(token="5532941774:AAGJTMME2kDgw7W68AEs719y-IYxuG-v5dc")
users = get_users()


@bot.message_handler(commands="start")
def start(message):
    if message.chat.id in users:
        bot.send_message(chat_id=message.chat.id, text="Congrats my brother, you have already been in my database")
    else:
        message = bot.send_message(chat_id=message.chat.id, text="Okay tell me, what is your pASSword")
        bot.register_next_step_handler(callback=register, message=message)


def register(message, **kwargs):
    if message.text == "zxcvbnnma":
        bot.send_message(message.chat.id, "Yeah, thats it. Now you can get my sweet data")
        add_user(message.chat.id)
    else:
        bot.register_next_step_handler(callback=register, message=message)


def send_new_orders():
    try:
        last_orders = get_new_orders()
        temp_orders = get_temp_orders()

        if len(temp_orders) > CLEAR_TEMP_ORDERS_LIMIT:
            clear_temp_orders()

        for last_order in last_orders:
            if last_order not in temp_orders:
                add_new_temp_order(last_order)

                message_text = f"Link - {last_order['link']}\nCategory - {last_order['category']}\nListed - {last_order['listed']}\nText: {last_order['order_text']}"

                for user in users:
                    bot.send_message(
                        chat_id=user,
                        text=message_text
                    )
    except Exception as err:
        pass

    time.sleep(2)
    send_new_orders()


if __name__ == '__main__':
    thread = threading.Thread(target=send_new_orders)
    thread.start()

    bot.polling()
