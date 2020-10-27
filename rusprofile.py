import requests
from bs4 import BeautifulSoup
import csv
from fake_useragent import UserAgent
import time
import random
import ssl


URL = 'http://www.rusprofile.ru/codes/105130/'

HEADERS = {'user-agent': UserAgent(verify_ssl=False).chrome}
FILE = 'cheeze.csv'


# Забираем хтмл страницы
def get_html(url):
    ssl._create_default_https_context = ssl._create_unverified_context
    proxies = {
        "http": "http://scraperapi:70c82eda5418489a37bfbc632d38237d@proxy-server.scraperapi.com:8001",
        "https": "http://scraperapi:70c82eda5418489a37bfbc632d38237d@proxy-server.scraperapi.com:8001"
    }
    r = requests.get(url, headers=HEADERS, proxies=proxies, verify='my_trust_store.pem')
    return r


# Сохрание дозаписью строк в файл
def save_file(items, path):
    with open(path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for item in items:
            writer.writerow([item['company'],
                             item['director'],
                             item['address'],
                             item['INN'],
                             item['regdate'],
                             item['capital'],
                             item['business'],
                             item['attention'],
                             item['location']
                             ])


# Забираем информацию со страницы хтмл
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_="company-item")
    for item in items:
        regdate = item.find_all('dd ')
        rr_data = []
        for i in regdate:
            rr_data.append(i)

    results = []
    for item in items:
        company = item.find('div', class_="company-item__title").get_text(strip=True)
        address = item.find('address', class_='company-item__text').get_text(strip=True)
        other_items = item.find_all('dd')
        atttention = item.find('span', class_='attention-text')
        if atttention is None:
            atttention = None
        else:
            atttention = atttention.get_text(strip=True)
        try:
            director = str((other_items[0]))[4:-5]
        except IndexError:
            director = 'None'
        try:
            inn = str(other_items[1])[4:-5]
        except IndexError:
            inn = 'None'
        try:
            regdate = str(other_items[3])[4:-5]
        except IndexError:
            regdate = 'None'
        try:
            capital = str(other_items[4])[4:-5]
        except IndexError:
            capital = 'None'
        try:
            business = str(other_items[5])[4:-5]
        except IndexError:
            business = 'None'

        results.append({
            'company': company,
            'director': director,
            'address': address,
            'INN': inn,
            'regdate': regdate,
            'capital': capital,
            'business': business,
            'attention': atttention,
            'location': address.split(',')[1]
        })
    print('_________________________\nТестовый результат:\n{0}\n_________________________'.format(results[0]))
    return results


# Парсим
def parse():
    for page in range(7, 76 + 1):
        print('Подал запрос на сервер сайта....')
        print(str(URL) + str(page))
        html = get_html(str(URL) + str(page))
        print('Пришел ответ\nПрогресс {0}%\nВыполняю парсинг страницы {1} из  {2}...\n'.format(round(1 / 76) * 100, page, 76))
        if html.status_code == 200:  # Проверяем достучались ли мы до сервера. В таком случае код 200
            content = get_content(html.text)
            save_file(content, FILE)
            randomtime = random.uniform(9.4, 20.2)
            time.sleep(randomtime)

        else:
            print("Произошла ошибка")
    else:
        print("Бот закончил работу")


parse()
