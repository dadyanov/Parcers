import requests
from bs4 import BeautifulSoup
import csv
from fake_useragent import UserAgent
import time
import random
import requests
import pandas as pd

homepage = 'https://zachestnyibiznes.ru'
headers = {'User-Agent': UserAgent(verify_ssl=False).chrome}


# Отдает список непроверенных ИНН
def undone():
    db = pd.read_excel('БазаОтформатированная.xlsx')
    inn_list = set(db['INN'].tolist())
    db = pd.read_csv('FinanceReport', delimiter=';')
    inn_ready = db["INN"].tolist()
    for i in inn_ready:
        i = int(i)
    inn_ready = set(inn_ready)
    result = inn_list - inn_ready
    return result


# Отдает 'search_check' , 'status' , 'link'
def search(inn):
    global homepage, headers
    search_url = 'https://zachestnyibiznes.ru/search?query={0}'.format(inn)
    searchpage = BeautifulSoup(
        requests.get(
            search_url,
            headers=headers
        ).text,
        'html.parser'
    )

    search_check = None
    status = None
    link = None

    try:
        searchlist_table = searchpage.find(
            'table',
            class_='table table-bordered table-striped rwd-table'
        ).find(
            'tbody'
        ).findAll(
            'tr'
        )

        rowindex = 0

        while int(searchlist_table[rowindex].findAll('td')[2].text) != inn:
            rowindex += 1
        status = searchlist_table[rowindex].findAll('td')[1].text
        status = status.replace('\n', '').replace(' ', '')
        search_check = True
        link = searchlist_table[rowindex].findAll('td')[0].find('a').get('href')
    except:
        pass
    result = {
        'search_check': search_check,
        'status': status,
        'link': homepage + link
    }
    return result


# Отдает html страницы
def get_html(link):
    global headers
    html = requests.get(link, headers=headers)
    return html


def taxes(text):
    taxes = text
    taxes = taxes.replace('\n', '')
    taxes = taxes.replace('- ', '')
    taxes = taxes.split('По данным портала ЗАЧЕСТНЫЙБИЗНЕС')

    search1 = 'акцизы, всего:'
    search2 = 'налог на добавленную стоимость:'

    excise_tax = None
    vat = None

    for i in taxes:
        if search1 in i:
            excise_tax = taxes[taxes.index(i) + 1]
            excise_tax = excise_tax.replace(' ', '')
            excise_tax = excise_tax.replace('руб.', '')
            excise_tax = excise_tax.replace(',00', '')
        if search2 in i:
            vat = taxes[taxes.index(i) + 1]
            vat = vat.replace(' ', '')
            vat = vat.replace('руб.', '')
            vat = vat.replace(',00', '')

    return {'excise_tax': excise_tax, 'vat': vat}


def financial_results_get(text):
    data = text
    data = data.replace('- ', '')
    data = data.replace('\n\n', '\n')
    data = data.split('\n')

    search1 = 'Сумма доходов: '
    search2 = 'Сумма расходов: '

    for i in data:
        if search1 in i:
            income = i[len(search1):]
            income = income.replace(' ', '')
            income = income.replace('руб.', '')
            income = income.replace(',00', '')
            income = int(income)
        elif search2 in i:
            expenditures = i[len(search2):]
            expenditures = expenditures.replace(' ', '')
            expenditures = expenditures.replace('руб.', '')
            expenditures = expenditures.replace(',00', '')
            expenditures = int(expenditures)

    return {'income': income, 'expenditures': expenditures}


def get_info(html):
    searchpage = BeautifulSoup(
        html.text,
        'html.parser'
    )
    summary_window = searchpage.findAll('div', class_="m-b-10")[1]
    hello_parcer = str(summary_window.text)

    try:
        tax = taxes(hello_parcer)
    except:
        tax = {'excise_tax': None, 'vat': None}

    try:
        income = financial_results_get(hello_parcer)
    except:
        income = {'income': None, 'expenditures': None}

    return {**tax, **income}


def parce(inn):
    srch = search(inn)
    html = get_html(srch['link'])
    data = get_info(html)
    with open('FinanceReport', 'a') as file:
        file.writelines('\n{0};{1};{2};{3};{4};{5}'.format(inn,
                                                           srch['status'],
                                                           data['excise_tax'],
                                                           data['vat'],
                                                           data['income'],
                                                           data['expenditures']
                                                           )
                        )
    answer = 'Получил информацию: \n{0};{1};{2};{3};{4};{5}'.format(inn,
                                                                    srch['status'],
                                                                    data['excise_tax'],
                                                                    data['vat'],
                                                                    data['income'],
                                                                    data['expenditures']
                                                                    )
    print(answer)


for i in undone():
    try:
        parce(int(i))
    except:
        with open('FinanceReport', 'a') as file:
            file.writelines('\n{0};{1};{2};{3};{4};{5}'.format(i,
                                                               None,
                                                               None,
                                                               None,
                                                               None,
                                                               None
                                                               )
                            )
        answer = 'Информация не получена:\n{0};{1};{2};{3};{4};{5}'.format(i,
                                                                           None,
                                                                           None,
                                                                           None,
                                                                           None,
                                                                           None
                                                                           )
        print(answer)
