import telebot
from telebot import types
from currency_converter import CurrencyConverter
from cred import token

bot = telebot.TeleBot(token)
currency = CurrencyConverter()
amount = 0


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
