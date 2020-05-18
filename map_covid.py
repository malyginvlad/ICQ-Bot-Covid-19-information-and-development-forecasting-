import geopandas as gpd
import matplotlib as mpl
import os
import pandas as pd

def map_covid():
    """Функция для построения карт по COVID-19."""
    # обрабатываем данные для нанесения на карту
    # загружаем датасет
    spisok = []
    for file in os.listdir("/home/morozov/icq_top/"):
        if file.endswith(".csv"):
            data1 = os.path.join(file)
            spisok.append(data1)
    path = '/home/morozov/icq_top/Russia/'
    # обработаем сообщение icq
    # загружаем данные по COVID19 по России из Яндекс
    data = pd.read_csv(spisok[-1], sep = ';')
    # приводим столбец даты в формат datetime
    data['Дата'] = pd.to_datetime(data['Дата'], format='%d.%m.%Y')
    # группируем столбцы, чтобы просуммировать общее значение за каждый день по Регионам
    data = data.groupby(['Дата','Регион']).sum().reset_index()
    data = data.sort_values(by=['Дата'])
    # берем самую последнюю дату обновления
    data_dt = data.Дата[-1:]
    # переводим в list
    data_dt = list(data_dt)
    # получаем значение
    data_dt = data_dt[-1].date().strftime("%d.%m.%Y")
    # подставляем последнее значение даты и получаем последние данные для covid-19 по регионам
    data_obr = data.loc[data.Дата == data_dt]
    # удаляем
    data_obr = data_obr.loc[~data_obr['Регион'].isin(['Чукотский АО'])]
    data_obr = data_obr.loc[~data_obr['Регион'].isin(['Крым'])]
    data_obr = data_obr.loc[~data_obr['Регион'].isin(['Севастополь'])]
    # загружаем данные карты РФ
    rf_gdf = gpd.read_file('RegionsRF.geojson')
    # преобразовываем проекцию карты
    rf_gdf_wm = rf_gdf.to_crs({'init' :'epsg:3857'}) #непосредственно преобразование проекции
    full_gdf = data_obr.merge(rf_gdf_wm[['NAME', 'ADM3_NAME', 'geometry']], left_on='Регион', right_on='NAME', how='left')
    full_gdf = gpd.GeoDataFrame(full_gdf)
    full_gdf.drop('Регион', axis=1, inplace = True)
    # выбираем шкалу нормализации
    norm = mpl.colors.Normalize(0,7000,clip=True)
    norm1 = mpl.colors.Normalize(0,2000,clip=True)
    norm2 = mpl.colors.Normalize(0,200,clip=True)
    full_gdf.plot(column = 'Заражений', linewidth=0, cmap='seismic',norm=norm,
                  legend=True, figsize=[10,7]).set_title('Карта зараженных от COVID-19 по России на {}'.format(data_dt)).figure.savefig(path + 'Заражений_Россия.png')
    full_gdf.plot(column = 'Выздоровлений', linewidth=0, cmap='summer_r',norm=norm1,
                  legend=True, figsize=[10,7]).set_title('Карта выздоровления от COVID-19 по России на {}'.format(data_dt)).figure.savefig(path + 'Выздоровлений_Россия.png')
    full_gdf.plot(column = 'Смертей', linewidth=0, cmap='PuOr',norm=norm2,
                  legend=True, figsize=[10,7]).set_title('Карта смертности от COVID-19 по России на {}'.format(data_dt)).figure.savefig(path + 'Смертей_Россия.png')
