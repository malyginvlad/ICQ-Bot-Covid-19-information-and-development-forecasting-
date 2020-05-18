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

def model(N, a, alpha, t0, t):
    """Инициализируем модель экспоненциального сглаживания."""
    return N * (1 - math.e**(-a * (t-t0)))**alpha

def model_loss(params, df):
    """Определяем целевую функцию для расчета потерь."""
    N, a, alpha, t0 = params
    r = 0
    # используем квадратичную функцию потерь
    # где (model(N, a, alpha, t0, t) полученный значения на выходе модели
    # df.iloc[t, 0] - истинные оценки (метки)
    for t in range(len(df)):
        r += (model(N, a, alpha, t0, t) - df.iloc[t, 0]) ** 2
    return r

def prognoz_covid(value_day, choice_data):
    """Функция для формирования прогноза."""
    
    # получаем данные для прогнозирования
    spisok = []
    for file in os.listdir("/home/morozov/icq_top/"):
        if file.endswith(".csv"):
            data1 = os.path.join(file)
            spisok.append(data1)
    path = '/home/morozov/icq_top/Russia/'
    # загружаем данные по COVID19 по России из Яндекс
    df = pd.read_csv(spisok[-1], sep = ';')
    df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y')
    if choice_data == 'Россия':
        choice_data1 = choice_data.replace(choice_data[-1], 'и')
        # формируем датасет по всей стране, удаляя столбец регионов
        df = df.drop(['Регион'], axis=1)
        # суммируем значения по дате
        df = df.groupby(['Дата']).sum().reset_index()
        # сортируем значения по дате
        df = df.sort_values(by=['Дата'])
        data_zar = df.set_index('Дата')[['Заражений']]
        data_rec = df.set_index('Дата')[['Выздоровлений']]
        data_death = df.set_index('Дата')[['Смертей']]
    else:
        df = df[df['Регион'] == choice_data]
        df = df.groupby(['Дата','Регион']).sum().reset_index()
        df = df.sort_values(by=['Дата'])
        data_zar = df.set_index('Дата')[['Заражений']]
        data_rec = df.set_index('Дата')[['Выздоровлений']]
        data_death = df.set_index('Дата')[['Смертей']]
    try:
        N = data_zar['Заражений'][-1]
        T = -data_zar['Заражений'][0]
        N1 = data_rec['Выздоровлений'][-1]
        T1 = -data_rec['Выздоровлений'][0]
        N2 = data_death['Смертей'][-1]
        T2 = -data_death['Смертей'][0]
    except:
        N = 10000
        T = 0
        N1 = 10000
        T1 = 0
        N2 = 10000
        T2 = 0

    opt = minimize(model_loss,args=(data_zar), x0=np.array([N, 0.1, 5, T]), method='Nelder-Mead', tol=1e-6).x
    opt1 = minimize(model_loss,args=(data_rec), x0=np.array([N1, 0.1, 5, T1]), method='Nelder-Mead', tol=1e-6).x
    opt2 = minimize(model_loss,args=(data_death), x0=np.array([N2, 0.1, 5, T2]), method='Nelder-Mead', tol=1e-6).x
    # создаем серию данных
    x_actual_data = list(data_zar.reset_index().iloc[:,0])
    x_actual_data = x_actual_data[-1]
    y_actual_zar = list(data_zar.reset_index().iloc[:,1])
    y_actual_zar = int(y_actual_zar[-1])
    y_actual_rec = list(data_rec.reset_index().iloc[:,1])
    y_actual_rec = int(y_actual_rec[-1])
    y_actual_death = list(data_death.reset_index().iloc[:,1])
    y_actual_death = int(y_actual_death[-1])
    # дата начала прогноза
    start_date = pd.to_datetime(data_zar.index[0])
    start_date1 = pd.to_datetime(data_rec.index[0])
    start_date2 = pd.to_datetime(data_death.index[0])
    # вводим количество дней для прогноза
    days_forecast = len(data_zar)+value_day
    days_forecast1 = len(data_rec)+value_day
    days_forecast2 = len(data_death)+value_day
    x_model = []
    y_model = []
    x_model1 = []
    y_model1 = []
    x_model2 = []
    y_model2 = []
    for t in range(days_forecast):
        x_model.append(start_date + datetime.timedelta(days=t))
        y_model.append(round(model(*opt,t)))
    for t in range(days_forecast1):
        x_model1.append(start_date1 + datetime.timedelta(days=t))
        y_model1.append(round(model(*opt1,t)))
    for t in range(days_forecast2):
        x_model2.append(start_date2 + datetime.timedelta(days=t))
        y_model2.append(round(model(*opt2,t)))
    if choice_data == 'Московская обл.':
        name_fig = 'МО' + '_' + str(value_day)
    else:
        name_fig = str(choice_data) + '_' + str(value_day)
    data_end = x_model[-1]
    data_vr = data_end.date().strftime("%d.%m.%Y")
    if value_day == 1:
        today = 'день'
    else:
        today = 'дней'
    if choice_data == 'Московская обл.':
        choice_data1 = choice_data.replace(choice_data[8:10], 'ой')
    elif choice_data == 'Санкт-Петербург':
        choice_data1 = choice_data + 'у'
    elif choice_data == 'Москва':
        choice_data1 = choice_data.replace(choice_data[-1], 'е')
    # прогноз
    y_prognoz_zar = int(y_model[-1])
    y_prognoz_rec = int(y_model1[-1])
    y_actual_death = int(y_model2[-1])
    # корректируем прогнозы
    if y_prognoz_zar < y_actual_zar:
        y_prognoz_zar = y_actual_zar
    elif y_prognoz_rec < y_actual_rec:
        y_prognoz_rec = y_actual_rec
    elif y_actual_death < y_actual_death:
        y_actual_death = y_actual_death
    # строим прогнозный график по заболевшим в России
    plt.figure(figsize=(10, 7))
    plt.plot(x_model, y_model, color='r', label="Прогноз по заболевшим ({} чел.)".format(y_prognoz_zar), linewidth = 2, linestyle='-')
    plt.title("Прогноз COVID-19 по {} на {} ({} {})".format(choice_data1, data_vr, value_day, today))
    #plt.plot(x_actual, y_actual, color='r', label="Актуальное значение", linewidth = 3, linestyle='--')
    plt.plot(x_model1, y_model1, color='g', label="Прогноз по выздоровевшим ({} чел.)".format(y_prognoz_rec), linewidth = 2, linestyle='-')
    plt.plot(x_model2, y_model2, color='b', label="Прогноз по смертям ({} чел.)".format(y_actual_death), linewidth = 2, linestyle='-')
    plt.xlabel('Дата')
    plt.ylabel('Количество людей')
    plt.legend()
    plt.grid(True)
    plt.savefig(path + str(name_fig))
    with open(path + 'data_po_covid.csv', 'a', encoding='utf-8') as fil:
        fil.write(u'{};{};{};{};{}\n'.format(data_vr, choice_data, y_prognoz_zar, y_prognoz_rec, y_actual_death))

def data_act_covid(value_day, choice_data):
    """Функция актуальных данных."""
    
    # получаем данные для прогнозирования
    spisok = []
    for file in os.listdir("/home/morozov/icq_top/"):
        if file.endswith(".csv"):
            data1 = os.path.join(file)
            spisok.append(data1)
    path = '/home/morozov/icq_top/Russia/'
    # загружаем данные по COVID19 по России из Яндекс
    df = pd.read_csv(spisok[-1], sep = ';')
    df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y')
    if choice_data == 'Россия':
        choice_data1 = choice_data.replace(choice_data[-1], 'и')
        # формируем датасет по всей стране, удаляя столбец регионов
        df = df.drop(['Регион'], axis=1)
        # суммируем значения по дате
        df = df.groupby(['Дата']).sum().reset_index()
        # сортируем значения по дате
        df = df.sort_values(by=['Дата'])
        data_zar = df.set_index('Дата')[['Заражений']]
        data_rec = df.set_index('Дата')[['Выздоровлений']]
        data_death = df.set_index('Дата')[['Смертей']]
    else:
        df = df[df['Регион'] == choice_data]
        df = df.groupby(['Дата','Регион']).sum().reset_index()
        df = df.sort_values(by=['Дата'])
        data_zar = df.set_index('Дата')[['Заражений']]
        data_rec = df.set_index('Дата')[['Выздоровлений']]
        data_death = df.set_index('Дата')[['Смертей']]
    # актуальные значения
    x_actual_data = list(data_zar.reset_index().iloc[:,0])
    y_actual_zar = list(data_zar.reset_index().iloc[:,1])
    x_actual_data1 = list(data_rec.reset_index().iloc[:,0])
    y_actual_rec = list(data_rec.reset_index().iloc[:,1])
    x_actual_data2 = list(data_death.reset_index().iloc[:,0])
    y_actual_death = list(data_death.reset_index().iloc[:,1])
    data_end = x_actual_data[-1]
    data_vr = data_end.date().strftime("%d.%m.%Y")
    if choice_data == 'Московская обл.':
        name_fig = 'МО' + '_' + str(value_day)
    else:
        name_fig = str(choice_data) + '_' + str(value_day)
    if value_day == 1:
        today = 'день'
    if choice_data == 'Московская обл.':
        choice_data1 = choice_data.replace(choice_data[8:10], 'ой')
    elif choice_data == 'Санкт-Петербург':
        choice_data1 = choice_data + 'у'
    elif choice_data == 'Москва':
        choice_data1 = choice_data.replace(choice_data[-1], 'е')
    # строим прогнозный график по заболевшим в России
    plt.figure(figsize=(10, 7))
    plt.plot(x_actual_data, y_actual_zar, color='r', label="Текущее значение по заболевшим ({} чел.)".format(int(y_actual_zar[-1])), linewidth = 2, linestyle='-')
    plt.title("Актуальное значение COVID-19 по {} на {} ({} {})".format(choice_data1, data_vr, value_day, today))
    plt.plot(x_actual_data1, y_actual_rec, color='g', label="Текущее значение по выздоровевшим ({} чел.)".format(int(y_actual_rec[-1])), linewidth = 2, linestyle='-')
    plt.plot(x_actual_data2, y_actual_death, color='b', label="Текущее значение по смертям ({} чел.)".format(int(y_actual_death[-1])), linewidth = 2, linestyle='-')
    plt.xlabel('Дата')
    plt.ylabel('Количество людей')
    plt.legend()
    plt.grid(True)
    plt.savefig(path + str(name_fig))
    with open(path + 'data_po_covid.csv', 'a', encoding='utf-8') as fil:
            fil.write(u'{};{};{};{};{}\n'.format(x_actual_data[-1].strftime("%d.%m.%Y"),choice_data,int(y_actual_zar[-1]),
                                                 int(y_actual_rec[-1]),int(y_actual_death[-1])))