import time
import datetime
from map_covid import map_covid
from prognose import prognoz_covid, data_act_covid
from load_data import load_data

while True:
    # загрузка новых данных с яндекса
    load_data()
    
    # обновление прогнозов
    data_act_covid(1, 'Россия')
    prognoz_covid(7, 'Россия')
    prognoz_covid(30, 'Россия')
    data_act_covid(1, 'Московская обл.')
    prognoz_covid(7, 'Московская обл.')
    prognoz_covid(30, 'Московская обл.')
    data_act_covid(1, 'Москва')
    prognoz_covid(7, 'Москва')
    prognoz_covid(30, 'Москва')
    data_act_covid(1, 'Санкт-Петербург')
    prognoz_covid(7, 'Санкт-Петербург')
    prognoz_covid(30, 'Санкт-Петербург')
    
    # обновление карт
    map_covid()
    
    # загрузка и обновление каждый день в 11:00 по мск
    tomorrow = datetime.datetime.combine(datetime.date.today(), datetime.time())+datetime.timedelta(days=1, hours=11)
    time_to_sleep = tomorrow - datetime.datetime.today()
    time.sleep(time_to_sleep.seconds)