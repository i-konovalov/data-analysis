import pandas as pd
from bs4 import BeautifulSoup
import requests
from time import sleep
from datetime import datetime, timedelta

URL = 'https://www.avito.ru/moskva/garazhi_i_mashinomesta/sdam/\
mashinomesto-ASgBAgICAkSYA~YQ5gj4Wg?district=619-622-656-673-696-700-716-717-724-738&f=ASgBAQICAkSYA~\
YQ5gj4WgFAnAxE3KsB2KsB1KsB0KsB&p={}'

def prob(series):
    '''
    Возвращает «вероятность» того, есть ли у автора объявления несколько машиномест.
    
    Параметры:
    series (Series) — столбец с описанием объявления
    '''
    if 'места' in series:
        return 'Возможно, есть несколько мест'
    else:
        return 'Только одно место'

def preprocessing(df):
    '''
    Принимает таблицу, предобрабатывает и возвращает новый вариант.
    
    Параметры:
    df (DataFrame) — таблица, которую нужно предобработать
    '''
    today = datetime.today().strftime('%d-%m-%Y') # сохраняем сегодняшниый день
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y') # сохраняем вчерашний день
    year = datetime.today().year # сохраняем текущий год
    df['address'] = df['address'].replace(r'\n', '', regex=True) # убираем переносы строки из адреса
    df['date'] = df['date'].replace(r'\n', '', regex=True) # убираем переносы строки из даты
    df['date'] = ( # заменяем слова «сегодня» и «вчера» на дату
        df['date']
        .replace('сегодня в', today, regex=True)
        .replace('вчера в', yesterday, regex=True)
    )
    df['address'] = df['address'].str.strip() # убираем лишние пробелы из адреса
    df['date'] = df['date'].str.strip() # убираем лишние пробелы из даты
    df['date'] = ( # перекодируем месяцы
        df['date']
        .replace(' января в', '-01-'+str(year), regex=True)
        .replace(' февраля в', '-02-'+str(year), regex=True)
        .replace(' марта в', '-03-'+str(year), regex=True)
        .replace(' апреля в', '-04-'+str(year), regex=True)
        .replace(' мая в', '-05-'+str(year), regex=True)
        .replace(' июня в', '-06-'+str(year), regex=True)
        .replace(' июля в', '-07-'+str(year), regex=True)
        .replace(' августа в', '-08-'+str(year), regex=True)
        .replace(' сентября в', '-09-'+str(year), regex=True)
        .replace(' октября в', '-10-'+str(year), regex=True)
        .replace(' ноября в', '-11-'+str(year), regex=True)
        .replace(' декабря в', '-12-'+str(year), regex=True)
    )
    df['date'] = pd.to_datetime(df['date']) # приводим дату к формату datetime
    df['prob'] = df['description'].apply(prob) # создаем столбец с вероятностью
    df = df.sort_values('prob') # сортируем по вероятности
    return df

def avito_df(url, pages):
    '''
    Функция принимает ссылку на сайт и количество страниц, которое нужно просмотреть, и парсит все объявления с этих страниц.
    Возвращает датафрейм с адресом, ссылкой на объявление, ссылкой на автора, описание и дату размещения.
    
    Параметры:
    
    url (str) — ссылка на поддомен для парсинга
    pages (int) — количество страниц, которое нужно спарсить
    '''
    
    # создаем пустые списки
    address_list = []
    link_list = []
    user_list = []
    description_list = []
    date_list = []
    
    # перебираем страницы
    for page in range(1,pages+1):
        
        req = requests.get(url.format(page))
        
        # проверяем статус запроса
        if req.status_code == 200:
            pass
        else:
            print('Error while parsing links, status code:', req.status_code)
            break
        
        # создаём парсер
        soup = BeautifulSoup(req.text, 'lxml')
        
        # находим все ссылки на объявления
        links = soup.find_all('a', attrs={'class': 'link-link-MbQDP link-design-default-_nSbv title-root-j7cja iva-item-title-_qCwt title-listRedesign-XHq38 title-root_maxHeight-SXHes'}, href=True)
        for i in links:
            link_list.append('https://www.avito.ru' + i['href'])
        
        # отдыхаем 5 секунд, чтобы не превысить лимит запросов
        sleep(5)
    
    # перебираем каждую ссылку
    for l in link_list:
        
        req_ad = requests.get(l)
        
        # снова проверяем статус
        if req.status_code == 200:
            pass
        else:
            print('Error while parsing ads, status code:', req.status_code)
            break
        
        # создаем парсер объявления
        soup_ad = BeautifulSoup(req_ad.text, 'lxml')
        
        # собираем дату, укладываем в список
        date = soup_ad.find('div', attrs={'class': 'title-info-metadata-item-redesign'})
        try:
            date_list.append(date.text)
        except:
            date_list.append('NaN')
        
        # собираем адрес, укладываем в список
        address = soup_ad.find('span', attrs={'class': 'item-address__string'})
        try:
            address_list.append(address.text)
        except:
            address_list.append('NaN')
        
        # собираем ссылку на профиль пользователя, укладываем в список
        user = soup_ad.find('div', attrs={'class': 'seller-info-name js-seller-info-name'}).find('a' , href=True)
        try:
            user_list.append(user['href'])
        except:
            user_list.append('NaN')
        
        # собираем описание, укладываем в список
        description = soup_ad.find('p')
        try:
            description_list.append(description.text)
        except:
            description_list.append('NaN')
            
        # отдыхаем 5 секунд после каждого объявления
        sleep(5)
    
    # создаем словарь, чтобы потом сделать из него датафрейм
    obj_dict = {
        'address': address_list,
        'ad_link': link_list,
        'user_link': user_list,
        'description': description_list,
        'date' : date_list
    }
    
    # создаем датафрейм
    table = pd.DataFrame(obj_dict)
    
    # предобрабатываем
    preprocessing(table)
    
    # возвращаем датафрейм
    return table
