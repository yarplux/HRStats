'''
1. достучаться до HH, забрать список вакансий по заданному запросу
2. распарсить список, получить описание вакансии (возможно, требуется переход на страницу вакансии)
3. выбрать все английские слова / словосочетания
4. пройти по всему списку, выбрав такие слова из всего списка вакансий
5. составить рейтинг (по частоте в количестве вакансий)
6. ...
'''
import requests
import urllib.parse
import re
import bs4
from bs4.element import Comment


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = bs(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def main():
    query = 'Java разработчик'
    referer = 'https://hh.ru/search/vacancy?from=suggest_post&fromSearchLine=true&area=113&customDomain=1&page=0&hhtmFrom=vacancy_search_list'
    agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'

    url = referer + '&text=' + urllib.parse.quote(query)
    headers = {
        'referer': url,
        'user-agent': agent
    }

    response = requests.get(url, headers=headers)
    m = re.findall(r'(https:\/.hh\.ru\/vacancy\/\d*)\?', response.text)

    for job in m:
        try:
            r = requests.get(job, headers=headers)

            print(r.status_code, job)
            bs = bs4.BeautifulSoup(r.text, features="html5lib")

            res = bs.find_all('div', attrs={"class": "g-user-content", "data-qa": "vacancy-description"})

            phrases = [i.text for i in res[0].children if i.text.strip() and re.match(".*[a-zA-Z]+.*", i.text)]

            res = bs.find_all('div', class_="bloko-tag-list")
            words = [i.text for i in res[0].children if re.match('.*[a-zA-Z]+.*', i.text)]

            # отличие от генератора - генератор не держит в памяти все генерируемые компоненты - пройтись по нему можно 1 раз
            # это list comprehensions - исчисление списков - создание списка - все храняться в памяти и доступны
            # TODO оптимизация без регулярок
            # re.compile - заранее парсит регулярное выражение

            print(words)
        except:
            print('Уникальная разметка: ', job)

    pass


if __name__ == '__main__':
    main()
