import telebot
from telebot import types
from currency_converter import CurrencyConverter
import sqlite3
import webbrowser
from cred import token

bot = telebot.TeleBot(token)
currency = CurrencyConverter()
amount = 0
name = None


@bot.message_handler(commands=["convertcurrency"])
def convert_currency(message):
    bot.send_message(message.chat.id, "Enter the amount to convert")
    bot.register_next_step_handler(message, total)


def total(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Incorrect format. Please, enter the amount")
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        button_gbp_usd = types.InlineKeyboardButton("GBP/USD", callback_data="currency/GBP/USD")
        button_usd_gbp = types.InlineKeyboardButton("USD/GBP", callback_data="currency/USD/GBP")
        button_eur_usd = types.InlineKeyboardButton("EUR/USD", callback_data="currency/EUR/USD")
        button_usd_eur = types.InlineKeyboardButton("USD/EUR", callback_data="currency/USD/EUR")
        button_else = types.InlineKeyboardButton("other currencies", callback_data="currency/else")
        markup.add(button_gbp_usd, button_usd_gbp, button_eur_usd, button_usd_eur, button_else)
        bot.send_message(message.chat.id, "Select a currency pair", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "The amount must be greater than 0, please enter the correct amount")


@bot.callback_query_handler(func=lambda call: call.data.startswith("currency"))
def convert_currency_callback(call):
    if call.data != "currency/else":
        currency_to_exchange = call.data.split("/")
        currency1, currency2 = currency_to_exchange[1], currency_to_exchange[2]
        result = currency.convert(amount, currency1, currency2)
        bot.send_message(call.message.chat.id,
                         f"The total is: {round(result, 2)}.")
    else:
        bot.send_message(call.message.chat.id, "Enter a pair of values separated by a slash")
        bot.register_next_step_handler(call.message, another_currency)


def another_currency(message):
    try:
        currency1, currency2 = message.text.upper().split("/")
        result = currency.convert(amount, currency1, currency2)
        bot.send_message(message.chat.id,
                         f"The total is: {round(result, 2)}.")
    except Exception:
        bot.send_message(message.chat.id, "Something is wrong, please enter the amount")
        bot.register_next_step_handler(message, total)


@bot.message_handler(commands=["users"])
def users(message):
    connect = sqlite3.connect("users.db")
    cursor = connect.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT)")

    connect.commit()
    cursor.close()
    connect.close()

    bot.send_message(message.chat.id, "Hello. To register, please input your name:")
    bot.register_next_step_handler(message, user_name)


def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Please, input your password:")
    bot.register_next_step_handler(message, user_password)


def user_password(message):
    password = message.text.strip()

    connect = sqlite3.connect("users.db")
    cursor = connect.cursor()

    cursor.execute(f"INSERT INTO users (name, password) VALUES ('%s', '%s')" % (name, password))
    connect.commit()
    cursor.close()
    connect.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("List of users", callback_data="list_of_users"))
    bot.send_message(message.chat.id, "The user is successfully registered!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "list_of_users")
def callback(call):
    connect = sqlite3.connect("users.db")
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM users")
    users_info = cursor.fetchall()

    users_in_db = ""
    for user in users_info:
        users_in_db += f"Name: {user[1]} Password: {user[2]}\n"

    cursor.close()
    connect.close()

    bot.send_message(call.message.chat.id, users_in_db)


@bot.message_handler(commands=["start", "hello"])
def start_command(message):
    markup = types.InlineKeyboardMarkup()
    button_website = types.InlineKeyboardButton("Link to the website", url="https://onepoundassistant.online/")
    button_about = types.InlineKeyboardButton("About the bot", callback_data="about")
    button_commands = types.InlineKeyboardButton("Available commands", callback_data="commands")
    markup.add(button_website)
    markup.row(button_about, button_commands)
    bot.send_message(message.chat.id, f"Hello {message.from_user.first_name}. How can I assist you today?",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "about")
def about_callback(call):
    bot.send_message(call.message.chat.id, "This bot is designed to assist you with various tasks and information.")


@bot.callback_query_handler(func=lambda call: call.data == "commands")
def commands_callback(call):
    bot.send_message(call.message.chat.id, "Here are some available commands:\n"
                                           "/start - Start a conversation\n"
                                           "/help - Get assistance\n"
                                           "/website - Open our website\n"
                                           "/order - Place an order\n"
                                           "/feedback - Provide feedback\n"
                                           "/about - Learn about the bot\n"
                                           "/users - Register a user and view list of users\n"
                                           "/weather - Find the current weather in the city\n"
                                           "/convertcurrency - Calculate currency conversion\n"
                                           "/commands - A list of available commands")


@bot.message_handler(commands=["about"])
def about_command(message):
    bot.reply_to(message, "I am your friendly assistant bot. I can help you with various tasks and information!")


@bot.message_handler(commands=["commands"])
def commands_command(message):
    bot.send_message(message.chat.id, "Here are some available commands:\n"
                                      "/start - Start a conversation\n"
                                      "/help - Get assistance\n"
                                      "/website - Open our website\n"
                                      "/order - Place an order\n"
                                      "/feedback - Provide feedback\n"
                                      "/about - Learn about the bot\n"
                                      "/users - Register a user and view list of users\n"
                                      "/weather - Find the current weather in the city\n"
                                      "/convertcurrency - Calculate currency conversion\n"
                                      "/commands - A list of available commands")


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(message.chat.id, f"<b>How can I help you?</b> <em>Common information: <u>Your order</u></em>",
                     parse_mode="html")


@bot.message_handler(commands=["website", "site"])
def website_command(message):
    webbrowser.open("https://onepoundassistant.online/")


@bot.message_handler(commands=["order"])
def order_command(message):
    bot.reply_to(message, "To place an order, please visit our website: https://onepoundassistant.online/order")


@bot.message_handler(commands=["feedback"])
def feedback_command(message):
    bot.reply_to(message, "We would love to hear your feedback! Please email us at feedback@onepoundassistant.online")
