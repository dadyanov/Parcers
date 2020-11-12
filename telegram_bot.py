import telebot
import wildberries.new_wildberries as parser
import time

# Передаю питону токен телеграма
bot = telebot.TeleBot("TOKEN")
state = str()
minus = list()
search = str()


@bot.message_handler(commands=['start'])
def handle_start(message):
    global state
    bot.send_message(message.from_user.id, 'Введите поисковой запроc:')
    state = 'search'


@bot.message_handler(content_types=['text'])
def handle_command(message):
    global state, search, minus
    if state == 'search':
        search = message.text
        bot.send_message(message.from_user.id,'Открой в браузере свой поисковой запрос и посмотри товары. Напиши '
                                              'список стоп слов в описаниях. Эти товары будут исключены. Поиск '
                                              'будет быстрее, а аналитика качественнее\n\n КОГДА ЗАКОНЧИШЬ НАПИШИ ТРИ'
                                              'РАЗА БУКУ Й и я начну поиск. ВОТ ТАК\n ЙЙЙ')
        state = 'minuswords'
    if state == 'minuswords' and message.text != 'ЙЙЙ':
        minus.append(message.text)
    if state == 'minuswords' and message.text == 'ЙЙЙ':
        state = 'working'
        parser.main(search, str(message.from_user.id), minus)
        bot.send_message(message.from_user.id, 'Я закончил')

        time.sleep(0.5)
        xl = open('Отчет {0}.xlsx'.format(message.from_user.id), 'rb')
        bot.send_document(message.from_user.id, xl)
        xl.close()
        time.sleep(0.5)

        img = open('prices_plot_TG.png', 'rb')
        bot.send_photo(message.from_user.id, img)
        img.close()
        time.sleep(0.5)

        img = open('prices_plot2_TG.png', 'rb')
        bot.send_photo(message.from_user.id, img)
        img.close()
        time.sleep(0.5)

        img = open('sales_plot_TG.png', 'rb')
        bot.send_photo(message.from_user.id, img)
        img.close()
        time.sleep(0.5)

        img = open('sales_plot2_TG.png', 'rb')
        bot.send_photo(message.from_user.id, img)
        img.close()
        time.sleep(0.5)


        bot.send_message(message.from_user.id, 'Введите поисковой запроc:')
        state = 'search'
        minus = list()
        search = str()



try:
    bot.polling(none_stop=True, timeout=9999)
except Exception or ConnectionError as err:
    if ConnectionError is True:
        print("Bad Internet connection!")
    elif Exception is True:
        print("Internet error!")
