"""
1. достучаться до HH, забрать список вакансий по заданному запросу
2. распарсить список, получить описание вакансии (возможно, требуется переход на страницу вакансии)
3. выбрать все английские слова / словосочетания
4. пройти по всему списку, выбрав такие слова из всего списка вакансий
5. составить рейтинг (по частоте в количестве вакансий)
6. ...
"""

import asyncio
import json
import os.path
import re
import urllib.parse

import bs4
import httpx
from httpx import HTTPStatusError
from typing import Dict

from constants import PATTERN, BASE_URL


# TODO оптимизация без регулярок
def get_words_from_page(body, pattern, method="html5lib"):
    bs = bs4.BeautifulSoup(body, features=method)
    phrases = []
    keywords = []

    # TODO корректно выбирать не только слова из ключевых слов, но и словосочетания из текста
    # получение английских слов / фраз из текста вакансии
    # res = bs.find_all('div', attrs={"class": "g-user-content", "data-qa": "vacancy-description"})
    # if res:
    #     phrases = [i.text for i in res[0].children if i.text.strip() and pattern.match(".*[a-zA-Z]+.*", i.text)]

    # получение английских слов из ключевых слов вакансии
    res = bs.find_all("div", class_="bloko-tag-list")
    if res:
        # это list comprehensions - исчисление списков - создание списка - все храняться в памяти и доступны
        # отличие от генератора - г-р не держит в памяти все генерируемые компоненты - пройтись по нему можно 1 раз
        keywords = [i.text for i in res[0].children if pattern.match(i.text)]

    print(
        ("phrases " + str(len(phrases)) + "; " if phrases else "")
        + ("keywords " + str(len(keywords)) if keywords else "")
    )
    return phrases + keywords


def get_headers(base: str):
    agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    return {"referer": base, "user-agent": agent}


# исключение дальше не пробрасывает, возвращает None
# TODO проскипать парсинг для страницы, которую не получили
async def get_response_text(url: str, client, headers):
    try:
        response = await client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()  # проверка на ошибку, и выкинет ошибку с HTTPError
        return url, response
    except HTTPStatusError as e:
        print(e)
        raise


def init_results():
    path = "./results/page_1.json"
    if not os.path.exists(path):
        return {}

    with open(path, "r") as file:
        return json.loads(file.read())


def save_results(word_base):
    path = "./results/page_1.json"
    with open(path, "w") as file:
        json.dump(word_base, file)


def get_max_page(text: str):
    page = [
        c.text
        for c in bs4.BeautifulSoup(text, features="lxml")
        .find("div", {"data-qa": "pager-block"})
        .children
    ][-2]
    return int(page.strip("."))


# TODO рефактор, чтобы функция воозвращала 1 тип значений
async def get_page_urls(query: str, headers: Dict[str, str], page: int = 0):
    url = BASE_URL + "?text=" + urllib.parse.quote(query) + "&page=" + str(page)

    with httpx.AsyncClient() as client:
        jobs_response = await get_response_text(url, client, headers)
        jobs = re.findall(r"(https:/.hh\.ru/vacancy/\d*)\?", jobs_response[1].text)
        return (jobs,) if page == 0 else jobs, get_max_page(jobs_response[1].text)


async def main():
    query = "Java разработчик"
    word_base = init_results()

    # Параметры подключения
    headers = get_headers(BASE_URL)

    jobs_page, max_page = get_page_urls(query, headers)
    jobs = set(jobs_page)
    for i in range(1, max_page):
        jobs.union(get_page_urls(query, headers, i)[0])

    with httpx.AsyncClient() as client:
        tasks = [
            asyncio.create_task(get_response_text(job, client, headers)) for job in jobs
        ]
        responses = await asyncio.gather(*tasks)

    for response in responses:
        if response is None:
            continue

        try:
            job_response = response[1]
            job = response[0]

            job_words = get_words_from_page(job_response.text, PATTERN, "lxml")

            for word in job_words:
                if word_base.get(word):
                    word_base[word].append(job)
                else:
                    word_base[word] = [job]

        except (TypeError, NameError) as e:
            print("Уникальная разметка: ", job, "\n", e)

        finally:
            # запись в файл, если было падение
            save_results(word_base)

    for word in word_base.keys():
        print(word + ": " + str(len(word_base[word])))


if __name__ == "__main__":
    asyncio.run(main())

"""
Чтобы параллельный код был корректен, каждый поток захватывает GIL, и остальные ждут => не "честная" многопоточность
Потоки помогают в обработке параллельных событий (то есть, когда нет необходимости непосредственно одновременно выполнять задачи)

https://docs.python.org/3/library/multiprocessing.html - для запуска нескольких процессов

  with Pool(5) as p:
        print(p.map(f, [1, 2, 3]))
        
    with as - менеджер контекстов (в конце корректно освобождает ресурсы)
    Pool(5) - создаёт контекст на 5 (в данном случае) процессов выполнения
    map - передаётся функция и аргументы, каждый будет в своём процессе обработан
    
    - результат работы можно записать в переменную    
    
    результат стоит обрабатывать уже после присваивания     
    
    Обработка json
    https://docs.python.org/3/library/json.html
"""

"""
CTRL+SPACE 2 раза - поиск/дополнение по всем возможным именам из пакетов
"""

"""
todo профилирование парсинга, чтобы понять, в чём задержка по времени парсинга

Инструменты профилирования:
1. модуль profile. Встроенный в питон. Не быстрый
2. cProfile работает также, но работает эффективнее

-m позволяет вызвать модуль, как программу. доступно в некоторых
- Модуль stats для взаимодействия со статистикой .prof
- спец. программа для просмотра в виде графиков

Детерминированный профайлер
Собирает вызовы функций, возвраты, исключения, и т.д. - оперирует событиями

Для рекурсии удобнее анализировать не график, а таблицу (суммарное время, количество вызовов)
"""

"""
Оптимизация bs
- поставить внешнюю либу, определяющую котировки (в доке по bs) - speedup
- можно заменить парсер
    - быстрее, но менее надёжно - можно сделать тест
    - делает меньше проверок, написана на C, интерпретатор как xml
    
"""

"""
Если ошибка, что venv_old не запускается автоматически при старте, то в 
Windows PowerShell от админа нужно выполнить:
Set-ExecutionPolicy RemoteSigned -Scope LocalMachine
"""

"""
pip freeze > .\requirements.txt
"""

"""
async функция - указание, что она асинхронная
    await - действие, которое нужно, чтобы программа подождала, отработав до следующего await
    
asyncio.run(функция) - создаётс цикл, внутри которого получаются задачи, и, когда задача готова к выполнению, она прокручивается до следующего 
    await, и, если может быть продолжена сразу же, то 

Используется IO    
"""

"""
если переменная нужна, но не используется, то по конвенции имя переменной _
(например, в цикле)
"""

"""
* - распаковка списка
"""

"""
Проверить, что с изменениями, и без них получаются одинаковые результаты для страниц
закинуть в git
Вопросы по асинхронности


"""
