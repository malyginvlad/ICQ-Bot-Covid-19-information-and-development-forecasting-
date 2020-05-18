import io
import json
import logging.config
from time import sleep
import datetime
import wget
import numpy as np
import os
import pandas as pd
import math
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from bot.bot import Bot
from bot.event import Event
from bot.filter import Filter
from bot.handler import HelpCommandHandler, UnknownCommandHandler, MessageHandler, FeedbackCommandHandler, \
    CommandHandler, NewChatMembersHandler, LeftChatMembersHandler, PinnedMessageHandler, UnPinnedMessageHandler, \
    EditedMessageHandler, DeletedMessageHandler, StartCommandHandler, BotButtonCommandHandler
import warnings
import requests
from bs4 import BeautifulSoup
from tldextract import extract

warnings.filterwarnings("ignore")

logging.config.fileConfig("logging.ini")
log = logging.getLogger(__name__)

NAME = "" # имя бота
VERSION = "0.0.1"
TOKEN = "" # токен
OWNER = ""

region_translate = {
    "russia": "Россия",
    "moscow": "Москва",
    "spb": "Санкт-Петербург",
    "mo": "Московская обл."
}


def start_cb(bot, event):
    """Вывод сообщения при старте."""
    
    now = datetime.datetime.now()
    data_vr = now.strftime("%d.%m.%Y, %H:%M")
    data_rem = int(now.strftime("%H"))
    today = ''
    if data_rem < 4 or data_rem > 22:
        today = 'доброй ночи!'
    elif 4 < data_rem < 10:
        today = 'доброе утро!'
    elif 10 <= data_rem < 16:
        today = 'добрый день!'
    else:
        today = 'добрый вечер!'
    first_name = event.data['from']['firstName'].capitalize()
    last_name = event.data['from'].get('lastName', "").capitalize()
    name = '{} {}'.format(first_name, last_name) if last_name != '' else first_name
    bot.send_text(
        chat_id=event.data['chat']['chatId'],
        text="""{}, {}

Я ваш электронный помощник «COVID-19: Новости и Прогнозирование».

Я могу предоставить вам последние новости по COVID-19 и сделать прогноз по количеству зараженных, выздоровевших и смертности на различный период времени.""".format(name, today),
        inline_keyboard_markup = "{}".format(json.dumps([
            [{"text": "Новостная лента", "callbackData": "get_top_news", "style": "primary"}],
            [{"text": "Прогноз по развитию COVID-19", "callbackData": "get_region", "style": "primary"}],
            [{"text": "Карта распространения COVID-19", "callbackData": "map_russia", "style": "primary"}],
            [{"text": "Меры предосторожности", "callbackData": "precautionary_measures", "style": "primary"}],
            [{"text": "Справочная информация", "callbackData": "information", "style": "primary"}]
        ])))
    
def get_top_news(bot, event):
    """Получение последних новостей с портала стопкороновирус.рф."""
    
    message = event.data['message']
    url = 'https://стопкоронавирус.рф/news/'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    page = requests.get((url), headers=headers)

    subdomain, domain, suffix = extract(url)

    if page.encoding == 'ISO-8859-1':
        page.encoding ='UTF-8'

    soup = BeautifulSoup(page.content.decode(), 'html.parser')
    url_name = soup.findAll("div", {"class": "cv-news-page__news-list-item"})

    mess_text = ''
    for i, item in enumerate(url_name):
        tag_a = item.find('a')

        href = tag_a.get('href', '')
        text = tag_a.find('h2').get_text()
        if 'https://' not in href:
            href = url + href
        mess_text += '{}. {}\n{}\n'.format(i+1, text, href)
    text_news = "Новостная лента по COVID-19 в России:\n\n"
    bot.send_text(
        chat_id = message['chat']['chatId'],
        text = text_news + mess_text,
        inline_keyboard_markup = "{}".format(json.dumps([
            [{"text": "Назад", "callbackData": "start"}]
        ])))

    
def get_region(bot, event):
    """Вывод общего графика и кнопок по прогнозу."""
    
    message = event.data['message']
    spisok = []
    for file in os.listdir("/home/morozov/icq_top/"):
        if file.endswith(".csv"):
            data1 = os.path.join(file)
            spisok.append(data1)
    path = '/home/morozov/icq_top/Russia/'
    # обработаем сообщение icq
    # загружаем данные по COVID19 по России из Яндекс
    russian = pd.read_csv(spisok[-1], sep = ';')
    # приводим столбец с дата в datetime
    russian['Дата'] = pd.to_datetime(russian['Дата'], format='%d.%m.%Y')
    # формируем тестовый датасет по всей стране, удаляя столбец регионов
    russian_all = russian.drop(['Регион'], axis=1)
    # суммируем значения по дате
    russian_all = russian_all.groupby(['Дата']).sum().reset_index()
    # сортируем значения по дате
    russian_all = russian_all.sort_values(by=['Дата'])
    # посмотрим актуальные значения
    russian_all_zab = list(russian_all.iloc[:,1]) # для зараженных
    russian_all_rec = list(russian_all.iloc[:,2]) # для выздоровевших
    russian_all_death = list(russian_all.iloc[:,3]) # для смертей
    russian_all_data = list(russian_all.iloc[:,0]) # для даты
    russian_all_death_day = list(russian_all.iloc[:,4]) # для смертей за день
    russian_all_rec_day = list(russian_all.iloc[:,6]) # для выздоровевших за день
    russian_all_zab_day = list(russian_all.iloc[:,5]) # для зараженных за день
    data_end = russian_all_data[-1]
    data_vr = data_end.date().strftime("%d.%m.%Y")
    # строим график по заболевшим в России
    plt.figure(figsize=(10, 7))
    plt.plot(russian_all_data, russian_all_zab, color='r', label="Количество зараженных",linewidth = 2)
    plt.title("Статистика COVID-19 по России на {}".format(data_vr))
    plt.plot(russian_all_data, russian_all_rec, color='g', label="Количество выздоровевших",linewidth = 2)
    plt.plot(russian_all_data, russian_all_death, color='b', label="Количество смертей",linewidth = 2)
    plt.xlabel('Дата')
    plt.ylabel('Количество людей')
    plt.legend()
    plt.grid(True)
    name_fig = message['chat']['chatId']
    plt.savefig(path + str(name_fig))
    # получаем последнее значение
    russian_zab = int(russian_all_zab[-1])
    russian_rec = int(russian_all_rec[-1])
    russian_death = int(russian_all_death[-1])
    russian_death_day = int(russian_all_death_day[-1])
    russian_rec_day = int(russian_all_rec_day[-1])
    russian_zab_day = int(russian_all_zab_day[-1])
    with open(path + name_fig+'.png', 'rb') as file:
        bot.send_file(chat_id = message['chat']['chatId'], file=file,
                  caption = """Данные на {}:
(Данные обновляются каждый день в 11:00 с Yandex DataLens)

Количество заболевших: {} (+{})
Количество выздоровевших: {} (+{})
Количество смертей {} (+{})

Выберите прогноз:""".format(data_vr, russian_zab, russian_zab_day,
                                     russian_rec, russian_rec_day,
                                     russian_death, russian_death_day),
                  inline_keyboard_markup = "{}".format(json.dumps([
                    [{"text": "Прогноз по России", "callbackData": "prog_russia_1", "style": "primary"}],
                    [{"text": "Прогноз по Москве", "callbackData": "prog_moscow_1", "style": "primary"}],
                    [{"text": "Прогноз по Санкт-Петербургу", "callbackData": "prog_spb_1", "style": "primary"}],
                    [{"text": "Прогноз по Московской области", "callbackData": "prog_mo_1", "style": "primary"}],
                    [{"text": "Назад", "callbackData": "start"}]
                  ])))
    
    
def get_prognose(bot, event, date, region):
    """Построение прогноза по COVID-19."""
    
    message = event.data['message']
    path = '/home/morozov/icq_top/Russia/'
    choose_reg = region_translate[region]
    picture = choose_reg + '_' + date + '.png'
    if region == 'mo':
        picture = 'МО_' + date + '.png'
    
    covid = pd.read_csv(path + 'data_po_covid.csv', sep=';')
    
    date = int(date)
    choose_date = -3
    if date == 7:
        choose_date = -2
    elif date == 30:
        choose_date = -1
        
    row = covid.loc[covid['Регион'] == choose_reg].iloc[choose_date]
    
    ill = row['Заражений']
    recovered = row['Выздоровлений']
    death = row['Смертей']
    if date != 1:
        actual = covid.loc[covid['Регион'] == choose_reg].iloc[-3] # TODO
        actual_ill = actual['Заражений']
        actual_recovered = actual['Выздоровлений']
        actual_death = actual['Смертей']

        with open(path + picture, 'rb') as file:
            bot.send_file(chat_id = message['chat']['chatId'], file = file,
                          caption = """{}, по состоянию на {}:
                          
Заболевших: {} (+{})
Выздоровевших: {} (+{})
Умерших: {} (+{})""".format(choose_reg, row['Дата'], str(ill), str(ill-actual_ill),
                                str(recovered), str(recovered-actual_recovered), str(death), str(death-actual_death)),
                      inline_keyboard_markup = "{}".format(json.dumps([
                        [{"text": "Прогноз на неделю", "callbackData": "prog_{}_7".format(region), "style": "primary"}],
                        [{"text": "Прогноз на месяц", "callbackData": "prog_{}_30".format(region), "style": "primary"}],
                        [{"text": "Назад", "callbackData": "prog_{}_1".format(region)}]
                      ])))
    else:
        with open(path + picture, 'rb') as file:
            bot.send_file(chat_id = message['chat']['chatId'], file = file,
                          caption = """{}, по состоянию на {}:
                          
Заболевших: {}
Выздоровевших: {}
Умерших: {}""".format(choose_reg, row['Дата'], str(ill),
                                str(recovered), str(death)),
                      inline_keyboard_markup = "{}".format(json.dumps([
                        [{"text": "Прогноз на неделю", "callbackData": "prog_{}_7".format(region), "style": "primary"}],
                        [{"text": "Прогноз на месяц", "callbackData": "prog_{}_30".format(region), "style": "primary"}],
                        [{"text": "Назад", "callbackData": "get_region"}]
                      ])))
    

def map_russia(bot, event):
    """Построение карты распространения COVID-19."""
    
    message = event.data['message']
    path = '/home/morozov/icq_top/Russia/'
    picture_zar = 'Заражений_Россия.png'
    picture_rec = 'Выздоровлений_Россия.png'
    picture_death = 'Смертей_Россия.png'
    bot.send_text(chat_id = message['chat']['chatId'], 
                  text = """На графиках представлена карта распространения COVID-19 по России.
                  
Она позволяет пользователям получать данные в режиме реального времени.
Карта собирается на основе сведений, полученных из различных официальных источников (Всемирная организация здравоохранения и Yandex)
На графиках карты отмечены все главные данные - количество заболевших по странам, ежедневная динамика новых случаев выявления болезни и количество излечившихся.

(Графики нормализованы по шкале для наглядного представления результатов распространения COVID-19)""")
    with open(path + picture_zar, 'rb') as file:
        bot.send_file(chat_id = message['chat']['chatId'], file = file,
                      caption = "")
    with open(path + picture_rec, 'rb') as file:
        bot.send_file(chat_id = message['chat']['chatId'], file = file,
                      caption = "")
    with open(path + picture_death, 'rb') as file:
        bot.send_file(chat_id = message['chat']['chatId'], file = file,
                      caption = "",
                      inline_keyboard_markup = "{}".format(json.dumps([
                          [{"text": "Назад", "callbackData": "start"}]
                      ])))
    
    
def precautionary_measures(bot, event):
    """Меры предосторожности."""
    
    message = event.data['message']
    bot.send_text(message['chat']['chatId'], 
                  text = """Основные меры предосторожности для защиты от новой коронавирусной инфекции:
                  
- Регулярно мойте руки;
- Соблюдайте дистанцию в общественных местах;
- По возможности, не трогайте руками глаза, нос и рот;
- Соблюдайте правила респираторной гигиены;
- При повышении температуры, появлении кашля и затруднении дыхания как можно быстрее обращайтесь за медицинской помощью;
- Следите за новейшей информацией и выполняйте рекомендации медицинских специалистов;

Меры индивидуальной защиты для тех, кто недавно (в последние 14 дней) посещал районы распространения COVID-19:

- Если вы почувствовали себя плохо, оставайтесь дома до выздоровления, даже если у вас легкие симптомы заболевания, например, головная боль или небольшой насморк;
- Если у вас повышенная температура тела, кашель и затруднение дыхания, не откладывайте обращение за медицинской помощью, так как эти симптомы могут быть вызваны респираторной инфекцией или другим серьезным заболеванием. Сначала позвоните в медицинское учреждение и сообщите обо всех последних поездках или контактах с путешествующими людьми.""",
                  inline_keyboard_markup = "{}".format(json.dumps([
                      [{"text": "Коронавирус", "callbackData": "recommendation_know", "style": "primary"}],
                      [{"text": "Рекомендации", "callbackData": "recommendation_reco", "style": "primary"}],
                      [{"text": "Профилактика", "callbackData": "recommendation_buss", "style": "primary"}],
                      [{"text": "Рекомендации для организаций", "callbackData": "recommendation_rosp", "style": "primary"}],
                      [{"text": "Узнать больше", "url": "http://www.viniti.ru/covid-19"}],
                      [{"text": "Назад", "callbackData": "start"}]
                  ])))

    
def recommendation(bot, event, picture): 
    """Рекомендации по COVID-19."""
    
    message = event.data['message']
    path = '/home/morozov/icq_top/coronavirus/'
    with open(path + picture, 'rb') as file:
        bot.send_file(chat_id=message['chat']['chatId'], file=file,
                      caption="",
                      inline_keyboard_markup = "{}".format(json.dumps([
                          [{"text": "Назад", "callbackData": "precautionary_measures"}]
                      ])))
    
    
    
def information(bot, event):
    """Информация."""
    
    message = event.data['message']
    bot.send_text(message['chat']['chatId'], text = """Описание функционала бота:
    
Кнопка "Новостная лента": отображает основную информацию о состоянии и развитии COVID19 в России по данным портала стопкороновирус.рф.
Данные содержат топ-10 новостей с сайта и обновляются при каждом вызове кнопки.

Кнопка "Прогноз по развитию COVID-19": показывает данные из ВОЗ (Всемирной организации здравоохранения) и портала Yandex на сегодняшний день.
Данные обновляются каждый день в 11:00 из https://datalens.yandex/covid19.
Далее выводится график показателей заболевших, выздоровевших и смертности на текущую дату и кнопки для получения прогноза по данным по на разный период времени (неделя, месяц).

Прогнозная модель основана на анализе временных рядов. За основу взята модель экспоненциального сглаживания.
Модель экспоненциального сглаживания и прогнозирования относится к классу адаптивных методов прогнозирования,
основной характеристикой которой является способность непрерывно учитывать эволюцию динамических характеристик изучаемых процессов,
подстраиваться под эту динамику, придавая, в частности, тем больший вес и тем более высокую информационную ценность имеющимся наблюдениям,
чем ближе они расположены к текущему моменту времени.
В качестве функциии потерь была взята квадратичная функция, преимуществом которой является инвариантность к знаку - значение функции всегда положительно.Т.е. независимо от знака ошибки результат будет один и тот же.
Минимизируем значения функции потерь с помощью оптимизации на основе метода Нелдера — Мида,
также известного как метод деформируемого многогранника. Этот метод безусловной оптимизации функции от нескольких переменных,
не использующий производной функции, а поэтому легко применим к негладким или зашумлённым функциям.

Кнопка "Меры предосторожности": показывает, что надо знать о короновирусе, рекомендации по профилактике в жизни и на работе.

КНопка: "Справочная информация": показывает описание бота.""",
      inline_keyboard_markup = "{}".format(json.dumps([
          [{"text": "Назад", "callbackData": "start"}]
      ])))
    
    
def buttons_answer_cb(bot, event):
    """Кнопки ответа."""
    
    message = event.data['message']
    
    event_callback_split = event.data['callbackData'].split('_')
    
    if event.data['callbackData'] == "start":
        bot.send_text(
            chat_id=message['chat']['chatId'],
            text='Выберите категорию, которую Вы хотите посмотреть:',
            inline_keyboard_markup = "{}".format(json.dumps([
                [{"text": "Новостная лента", "callbackData": "get_top_news", "style": "primary"}],
                [{"text": "Прогноз по развитию COVID-19", "callbackData": "get_region", "style": "primary"}],
                [{"text": "Карта распространения COVID-19", "callbackData": "map_russia", "style": "primary"}],
                [{"text": "Меры предосторожности", "callbackData": "precautionary_measures", "style": "primary"}],
                [{"text": "Справочная информация", "callbackData": "information", "style": "primary"}]
            ])))
        
    elif event.data['callbackData'] == "get_top_news":
        get_top_news(bot, event)
        
    elif event.data['callbackData'] == "get_region":
        get_region(bot, event)
        
    elif event_callback_split[0] == "prog":
        region = event_callback_split[1]
        date = event_callback_split[2]
        get_prognose(bot, event, date, region)
        
    elif event.data['callbackData'] == "map_russia":
        map_russia(bot, event)
        
    elif event.data['callbackData'] == "precautionary_measures":
        precautionary_measures(bot, event)
        
    elif event_callback_split[0] == "recommendation":
        pictures = {
            'know': 'have2know.jpg',
            'reco': 'recommend.jpg',
            'buss': 'business.jpg',   
            'rosp': 'recom_rospotreb.jpg'              
        }
        recommendation(bot, event, pictures[event_callback_split[1]])
        
    elif event.data['callbackData'] == "information":
        information(bot, event)
        
    bot.answer_callback_query(
        query_id=event.data['queryId'],
        text="",
        show_alert=False)




def main():
    bot = Bot(token=TOKEN, name=NAME, version=VERSION)
    bot.dispatcher.add_handler(StartCommandHandler(callback=start_cb))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_answer_cb))
    bot.start_polling()
    bot.idle()

if __name__ == "__main__":
    main()