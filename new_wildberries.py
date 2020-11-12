from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import json
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn

url = 'https://www.wildberries.ru'

def csv_create(file_name):
    file = open('{0}.csv'.format(file_name), 'w+')
    file.close()
    first_row = 'brand;name;link;new;basicPrice;promoPrice;basicSale;promoSale;sold;ordersCount;articul;picsCount;video;regionIds;scores;quantity;basePrice;soldOut\n'
    with open('{0}.csv'.format(file_name), 'w') as file:
            file.write(first_row)
    file.close()
    return '{0}.csv'.format(file_name)

def search(text, url):
    driver = webdriver.Chrome(executable_path='../chromedriver')
    driver.get(url)
    xpath = "/html/body[@class='ru']/div[@class='header-v1  j-header  header-with-burger']/div[@class='header-bg j-parallax-back-layer']/div[@class='header-wrapper lang-ru']/div[@class='header-content']/div[@class='wildSrch enable-img']/input[@id='tbSrch']"
    searchrow = driver.find_element_by_xpath(xpath)
    searchrow.send_keys('{0}'.format(text) + '\n')
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    return driver


def next_page(driver, file):
    next_page_button = "/html/body[@class='ru']/div[@id='body-layout']/div[@class='left-bg']/div[@class='trunkOld']/div[@id='catalog']/div[@id='catalog-content']/div[@class='pager-bottom']/div[@class='pager i-pager']/div[@class='pageToInsert']/a[@class='pagination-next']"
    goods = save_searchpage(driver.page_source)
    for good in goods:
        driver.get(good['link'])
        data = save_good(driver.page_source)
        good_data_final = {**data, **good}
        save_file(good_data_final, file)
        driver.back()
    try:
        next = driver.find_element_by_xpath(next_page_button)
        next.click()
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        next_page(driver)
    except:
        print("Я закончил")


def save_file(item, path):
    # Пишем построчно каждый полученный результат сразу
    with open(path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([item['brand'],
                         item['name'],
                         item['link'],
                         item['new'],
                         item['basicPrice'],
                         item['promoPrice'],
                         item['basicSale'],
                         item['promoSale'],
                         item['sold'],
                         item['ordersCount'],
                         item['articul'],
                         item['picsCount'],
                         item['video'],
                         item['regionIds'],
                         item['scores'],
                         item['quantity'],
                         item['basePrice'],
                         item['soldOut']
                         ])
        print("Спарсил товар: {0}. Производитель: {1}. Стоит: {2}.".format(item['name'],
                                                                           item['brand'],
                                                                           item['promoPrice']))


def save_searchpage(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_="dtList-inner")
    less_words = ['ведро', "урна", "контейнер"]
    goods = []
    for item in items:
        item_data = {}
        item_data['brand'] = item.find('strong', class_='brand-name c-text-sm').get_text(strip=True)[:-1]
        item_data['name'] = item.find('span', class_='goods-name c-text-sm').get_text(strip=True)
        item_data['link'] = 'https://www.wildberries.ru' + \
                            item.find('a', class_="ref_goods_n_p j-open-full-product-card").get('href')
        try:
            item_data['new'] = item.find('ins', class_='noveltyImg c-text-xsm').get('title')
        except:
            item_data['new'] = 'No data'
        check = 0
        for i in less_words:
            match = re.search(i, item_data['name'])
            if match:
                check = 1
            else:
                check = 0
        if check == 0:
            goods.append(item_data)
        else:
            pass
    return goods


def save_good(html):
    soup = BeautifulSoup(html, 'html.parser')
    ourscript = html
    start = ourscript.find('data: ') + 6
    stop = ourscript.find("link: ")
    pre = str(ourscript[start:stop - 14])
    pre = json.loads(pre)
    dataforvisited = pre['dataForVisited']
    priceDetails = pre['nomenclatures']['{0}'.format(dataforvisited)]['priceDetails']
    try:
        basicPrice = priceDetails['basicPrice']
    except:
        basicPrice = 'No data'
    try:
        promoPrice = priceDetails['promoPrice']
    except:
        promoPrice = 'No data'
    try:
        basicSale = priceDetails['basicSale']
    except:
        basicSale = 'No data'
    try:
        promoSale = priceDetails['promoSale']
    except:
        promoSale = 'No data'
    data1 = pre['nomenclatures']['{0}'.format(dataforvisited)]
    key = list(data1['sizes'].keys())[0]
    try:
        quantity = data1['sizes']['{0}'.format(key)]['quantity']
    except:
        quantity = 'No data'
    try:
        basePrice = data1['sizes']['{0}'.format(key)]['price']
    except:
        basePrice = 'No data'
    try:
        issoldout = data1['sizes']['{0}'.format(key)]['isSoldOut']
    except:
        issoldout = 'No data'
    try:
        sold = data1['isSoldOut']
    except:
        sold = 'No data'
    try:
        ordersCount = data1['ordersCount']
    except:
        ordersCount = 'No data'
    try:
        articul = data1['artikul']
    except:
        articul = 'No data'
    try:
        picsCount = data1['picsCount']
    except:
        picsCount = 'No data'
    try:
        video = data1['hasVideo']
    except:
        video = 'No data'
    try:
        regionIds = data1['regionIds']
    except:
        regionIds = 'No data'
    try:
        scores = soup.findAll('div', class_='result-value xh-highlight').get_text(strip=True)
    except:
        scores = 'No data'

    return {'basicPrice': basicPrice,
            'promoPrice': promoPrice,
            'basicSale': basicSale,
            'promoSale': promoSale,
            'basePrice': basePrice,
            'sold': sold,
            'soldOut': issoldout,
            'quantity': quantity,
            'ordersCount': ordersCount,
            'articul': articul,
            'picsCount': picsCount,
            'video': video,
            'regionIds': regionIds,
            'scores': scores
            }


def merge(df):
    asana = pd.read_excel('asanaPrice.xlsx')
    new = pd.merge(df, asana, on='type')
    new['Our-Market'] = new['retailPrice'] - new['promoPrice']
    return new


def calcCategory(df, writer):

    prdf = prices(df) # Таблица бренд и цены
    shdf = shares(df) # Таблица бренд название и продажи

    prdf.to_excel(writer, sheet_name='Таблица цен', startrow=0, startcol=0)
    shdf.to_excel(writer, sheet_name='Таблица продаж', startrow=0, startcol=0)

    seaborn.distplot(prdf.promoPrice.dropna())
    plt.savefig('prices_plot_TG.png') # Распределение цен в категории
    plt.tight_layout()
    plt.close()
    prdf.plot(y='promoPrice', x='brand', kind='bar')
    plt.tight_layout()
    plt.savefig('prices_plot2_TG.png') # Демонстрация цен в категории
    plt.close()

    seaborn.distplot(shdf.ordersCount.dropna())
    plt.tight_layout()
    plt.savefig('sales_plot_TG.png') # Распределение долей рынк
    plt.close()
    shdf.plot(y='ordersCount', x='brand', kind='bar')
    plt.tight_layout()
    plt.savefig('sales_plot2_TG.png') # Демонстрация долей рынка
    worksheet_prices = writer.sheets['Таблица цен']
    worksheet_shares = writer.sheets['Таблица продаж']
    plt.close()

    worksheet_prices.insert_image('G2', 'prices_plot_TG.png')
    worksheet_prices.insert_image('G26', 'prices_plot2_TG.png')
    worksheet_shares.insert_image('G2', 'sales_plot_TG.png')
    worksheet_shares.insert_image('G26', 'prices_plot2_TG.png')


def shares(df):
    df = df[['brand', 'name', 'ordersCount']].sort_values('ordersCount', ascending=False)
    df['share'] = df['ordersCount'] / df.sum()['ordersCount']

    return df


def prices(df):
    df = df[['brand','name', 'promoPrice']]
    return df.sort_values('promoPrice', ascending=True)


def main(search_request, file_name, minus):
    file = csv_create(file_name)
    next_page(search(search_request, url), file)
    df = pd.read_csv(file, sep=';')
    x = str()
    for m in minus:
        x += m + '|'
    minus = x[:-1]
    df = df.loc[~df['name'].str.contains(minus, flags=re.I, regex=True)]
    writer = pd.ExcelWriter('Отчет {0}.xlsx'.format(file_name), engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Общие данные', startrow=0, startcol=0)
    calcCategory(df, writer)
    writer.save()