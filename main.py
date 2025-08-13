from telebot import *

bot = telebot.TeleBot('6321314870:AAEeMBQVsXSFTtGJyCbljAJi1wPgxwU7yaM')

markup = types.InlineKeyboardMarkup()
btn = types.InlineKeyboardButton("Нажми меня", callback_data="click")
markup.add(btn)

@bot.message_handler(commands=['test'])
def send_button(message):
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(call.id, "Кнопка нажата!")

bot.infinity_polling()