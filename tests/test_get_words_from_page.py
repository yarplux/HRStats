from unittest import TestCase
import pickle

from main import get_words_from_page
from constants import PATTERN

'''
Возможность написания тестов, test discovery, доки питона (часть ст. библиотеки)
Возможность описать функцию, выполняющуюся перед/после каждого теста

['Java', 'Atlassian Jira', 'REST', 'Quarkus', 'Spring']

python -m unittest test_get_words_from_page.Test in D:\DevTemp\PyCharm\parsingHH\tests

Параметризованных тестов здесь не реализованны
Есть другие. Например, pytest (хотя здесь скорее всего излишня, там можно прописать запуск тестов с параметрами, и т.д.)


'''


class Test(TestCase):

    # TODO вычитывание данных можно перенести в функции перед начало места - setup и teardown
    # test lxml vs html5lib
    def test_get_words_from_page(self):
        for i in range(20):
            file_words = f'./data/page_1_job{i}_words'
            with open(file_words, 'rb') as file:
                data = pickle.load(file)

            file_body_name = f'./data/page_1_job{i}'
            with open(file_body_name, 'r', encoding='UTF-8') as file:
                result = get_words_from_page(file.read(), PATTERN, 'lxml')

                # если нужно строгое соответствие
                # self.assertEqual(data, result) - обычно либо для скалярных значений, либо одинарных объектов
                # проверяет эквивалентность контейнеров по факту, без учёта порядка!
                self.assertCountEqual(data,result)
                print(f'TEST {file_body_name} result OK')


