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
import pprint


# TODO оптимизация без регулярок
# re.compile - заранее парсит регулярное выражение
def get_words_from_page(body):
    bs = bs4.BeautifulSoup(body, features="html5lib")
    phrases = []
    keywords = []

    # TODO корректно выбирать не только слова из ключевых слов, но и словосочетания из текста
    # получение английских слов / фраз из текста вакансии
    # res = bs.find_all('div', attrs={"class": "g-user-content", "data-qa": "vacancy-description"})
    # if res:
    #     phrases = [i.text for i in res[0].children if i.text.strip() and re.match(".*[a-zA-Z]+.*", i.text)]

    # получение английских слов из ключевых слов вакансии
    res = bs.find_all('div', class_="bloko-tag-list")
    if res:
        # это list comprehensions - исчисление списков - создание списка - все храняться в памяти и доступны
        # отличие от генератора - г-р не держит в памяти все генерируемые компоненты - пройтись по нему можно 1 раз
        keywords = [i.text for i in res[0].children if re.match('.*[a-zA-Z]+.*', i.text)]



    print(
        ('phrases ' + str(len(phrases)) + '; ' if phrases else '') +
        ('keywords ' + str(len(keywords)) if keywords else '')
    )
    return phrases + keywords


def get_headers(query: str):
    referer = 'https://hh.ru/search/vacancy?from=suggest_post&fromSearchLine=true&area=113&customDomain=1&page=0&hhtmFrom=vacancy_search_list'
    url = referer + '&text=' + urllib.parse.quote(query)

    agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    return url, {'referer': url, 'user-agent': agent}


def get_response_text(url: str, headers):
    response = requests.get(url, headers=headers)
    print(response.status_code, url)
    return response


def main():
    query = 'Java разработчик'
    job_limit = 10
    word_base = {}

    url, headers = get_headers(query)
    jobs_response = get_response_text(url, headers)
    for job in re.findall(r'(https:/.hh\.ru/vacancy/\d*)\?', jobs_response.text):
        if not job_limit:
            break

        job_limit -= 1
        try:
            job_response = get_response_text(job, headers)
            job_words = get_words_from_page(job_response.text)

            for word in job_words:
                if word_base.get(word):
                    word_base[word].append(job)
                else:
                    word_base[word] = [job]

            # todo запись в файл / чтение из файла распаршенного
            # todo в несколько потоков

        except (TypeError, NameError):
            print('Уникальная разметка: ', job)

    for word in word_base.keys():
        print(word + ": " + str(len(word_base[word])))


if __name__ == '__main__':
    main()
