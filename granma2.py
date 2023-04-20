# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import pandas as pd
from time import sleep
from random import randint

def get_data(url_page: str, sp_topic: str) -> list:
    """

    :param url_page: url base
    :return: list of pages analyzed
    """
    url_visited = pd.read_csv('GR_visited.csv', names=['URLs']).values.tolist()
    url_visited = [item[0] for item in url_visited]
    url_analyzed = pd.read_csv('GR_results.csv', names=['year', 'month', 'day', 'n_imgs', 'url']).values.tolist()
    soup = get_page_code(url_page + sp_topic)
    url_analyzed, url_visited = extract_data_from_content_page(url_page + sp_topic, url_visited, url_analyzed, sp_topic)
    url_archive = soup.find_all('a', {'class': 'archivo'})[0]['href']
    # soup = get_page_code(url_archive)
    soup = get_page_code(url_archive)
    number_pages = int(soup.body.find_all('div')[0].find_all('div')[14].find_all('ul')[0].find_all('a')[-2].text)
    for i in range(2, number_pages + 1):
        sleep(randint(10, 30) /10)
        url_next = f'https://www.granma.cu/archivo?page={i}&q=&s=2'
        # soup = get_page_code(url_next)
        url_analyzed, url_visited = extract_data_from_content_page(url_next, url_visited, url_analyzed, sp_topic)
    return url_analyzed


def get_page_code(url_web: str) -> BeautifulSoup:
    if 'http://' not in url_web:
        if url_web[0] != '/':
            url_web = 'http://www.granma.cu/' + url_web
        else:
            url_web = 'http://www.granma.cu' + url_web
    scrap = Request(url_web, headers={'User-Agent': 'Mozilla/5.0'})
    web = urlopen(scrap).read()
    soup = BeautifulSoup(web, 'html.parser')
    return soup


def extract_data_from_content_page(url_page: str, url_visited: list, url_analyzed: pd.DataFrame, sp_topic:str) -> tuple:
    scrap = Request(url_page, headers={'User-Agent': 'Mozilla/5.0'})
    web = urlopen(scrap).read()
    soup = BeautifulSoup(web, 'html.parser')
    # list all urls in the content of website
    if 'column_1' in str(soup):
        t1 = soup.body.find_all('div')[0].find_all('div')[14].find('div', {'id': 'column_0'}).find_all('a')
        t2 = soup.body.find_all('div')[0].find_all('div')[14].find('div', {'id': 'column_1'}).find_all('a')
        t1.extend(t2)
        t = [item['href'] for item in t1]
    else:
        t = [item.h2.a['href'] for item in
             soup.body.find_all('div')[0].find_all('div')[14].find_all('article', {'class': 'g-searchpage-story'})]
    # url not visited
    url_not = list(set(t).difference(url_visited))
    if len(url_not) > 0:
        for url_ in url_not:
            if 'cuba/' in url_ or 'salud/' in url_:
                if 'http://' not in url_:
                    w1 = Request('http://www.granma.cu/' + url_, headers={'User-Agent': 'Mozilla/5.0'})
                else:
                    w1 = Request(url_, headers={'User-Agent': 'Mozilla/5.0'})
                sc = urlopen(w1).read()
                soup = BeautifulSoup(sc, 'html.parser')
                # all images
                img = soup.body.find_all('div')[0].find_all('div')[14].find('div', {'class': 'col-md-8'}).find_all('img')
                # list_url_img = [item['src'] for item in img]
                url_date = url_[url_.find('20'): url_.find('20') + 10].split('-')
                full_data = list()
                full_data.extend(url_date)
                full_data.append(sp_topic)
                full_data.append(len(img) - 1)
                if url_[0] =='/':
                    full_data.append('http://www.granma.cu' + url_)
                else:
                    full_data.append('http://www.granma.cu/' + url_)
                url_analyzed.append(full_data)
                pd.DataFrame(url_analyzed).to_csv('GR_results.csv', header=False)
                url_visited.append(url_)
                pd.DataFrame(url_visited).to_csv('GR_visited.csv', header=False)
                print(f'GR-Page number {len(url_visited)} analyzed')
                sleep(randint(10,30) / 10)

    return url_analyzed, url_visited


GR_pages = ['salud']

url = 'http://www.granma.cu/'
topic_visited = pd.read_csv('GR_visited.csv', names=['URLs']).values.tolist()
for topic in GR_pages:
    if topic not in topic_visited:
        get_data(url,  topic)
    pd.DataFrame(['topic']).to_csv('GR_topics.csv', header=False)
