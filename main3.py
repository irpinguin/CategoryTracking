"""

"""

import time
from pprint import pprint

from fake_useragent import UserAgent
from random import randint
import requests
from requests import Session, Response
from typing import Optional, List, Dict, Union, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import NoSuchElementException, TimeoutException
import pandas as pd


BASE_URL = 'https://irmag.ru'
CAT_URL = '/cat'
CAT_PAGE_SIGN = "Каталог - IRMAG.RU"
TIMEOUT = 10
PAUSE_MIN = 0
PAUSE_MAX = 2
#
CAT_CATEGORY_MENU_LOC = ('xpath', '//div[@class="alert alert-grey p-10"]')
CAT_MENU_ITEMS_LOC = 'btn btn-link preload'


def pause():
    """
    Рандомная пауза
    """

    timeout = randint(PAUSE_MIN, PAUSE_MAX)
    time.sleep(timeout)


def get_page_session(session: Session, url: str, headers: dict, timeout: int) -> Optional[Response]:
    """
        Получает страницу по-заданному URL с использованием предоставленной сессии.

        :param session: Сессия для запроса.
        :param url: URL страницы.
        :param headers: Заголовки запроса.
        :param timeout: Время ожидания запроса в секундах.
        :return: Объект Response или None, если запрос не удался.
        """

    try:
        response = session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response

    except requests.exceptions.HTTPError as http_error:
        print(f"Ошибка при выполнении запроса: {http_error}")
    except requests.exceptions.ConnectionError as connection_error:
        print(f"Ошибка подключения: {connection_error}")
    except requests.exceptions.Timeout as timeout_error:
        print(f"Превышен таймаут: {timeout_error}")
    except requests.exceptions.RequestException as request_error:
        print(f"Произошла ошибка при выполнении запроса: {request_error}")

    return None


def get_page(url: str, headers: dict, timeout: int) -> Optional[Response]:
    """
    Получает страницу по-заданному URL

    :param url: URL для запроса
    :param headers: Заголовки HTTP-запроса
    :param timeout: Таймаут для запроса
    :return: Объект Response в случае успеха, None в случае ошибки
    """

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response

    except requests.exceptions.HTTPError as http_error:
        print(f"Ошибка при выполнении запроса: {http_error}")
    except requests.exceptions.ConnectionError as connection_error:
        print(f"Ошибка подключения: {connection_error}")
    except requests.exceptions.Timeout as timeout_error:
        print(f"Превышен таймаут: {timeout_error}")
    except requests.exceptions.RequestException as request_error:
        print(f"Произошла ошибка при выполнении запроса: {request_error}")

    return None


def init_driver() -> webdriver:
    """

    :return:
    """

    service = Service(executable_path=ChromeDriverManager().install())
    options = Options()
    options.add_argument("--window-size=1280,768")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={UserAgent().random}")
    options.add_argument("--headless")
    # options.page_load_strategy = 'normal'
    options.page_load_strategy = 'eager'
    # options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=service, options=options)

    # устанавливаем геолокацию: Троицкий взвоз, Саратов, Саратовская обл., 410031
    # со скрытием ip пока не связываемся
    params = {
        "latitude": 51.527679,
        "longitude": 46.0569626,
        "accuracy": 100
    }
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)

    return driver


def get_category_tree(driver: WebDriver, level: int, url: str, class_name: str) -> Optional[Union[Dict[str, Any], None]]:
    """
    Получение списка категорий на определенном уровне иерархии

    :param driver: экземпляр объекта браузера
    :param level: уровень иерархии категорий
    :param url: ссылка на категорию
    :param class_name: локатор - класс для поиска ссылок
    :return: словарь с категориями в форме дерева или None, если вложенных категорий на этом уровне не найдено
    """

    # print(f"Обработка уровня {level}.")
    wait = WebDriverWait(driver, TIMEOUT, poll_frequency=1)
    driver.get(url)

    try:
        wait.until(EC.visibility_of_element_located(CAT_CATEGORY_MENU_LOC))
        cat_page_src = driver.page_source
        cat_page_soup = BeautifulSoup(cat_page_src, 'lxml')

        cat_tree = {}
        for category in cat_page_soup.findAll('a', class_=class_name):
            tag_href = category['href'].split('/')[2]
            cat_dict = {
                'level': level,
                f'category_id_lvl_{level}': tag_href,
                'name': category.text.split('\n')[1].strip(),
                'url': BASE_URL + CAT_URL + '/' + tag_href,
                'subcategories': get_category_tree(driver, level + 1, BASE_URL + CAT_URL + '/' + tag_href, class_name)
            }
            cat_tree[tag_href] = cat_dict

        pause()
        return cat_tree if cat_tree else None
    except TimeoutException:
        # print(f"На уровне {level} меню следующего уровня отсутствует")
        pause()
        return None


def main():

    url = BASE_URL+CAT_URL
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    # session = Session()

    response = get_page(url, headers, TIMEOUT)
    cat_page_soup = BeautifulSoup(response.text, 'lxml')

    # проверка, что страница каталога доступна и что это именно она
    cat_page_title = cat_page_soup.find('title').text
    assert response.status_code == 200, "Запрос вернул статус-код, который отличается от 200."
    assert cat_page_title == CAT_PAGE_SIGN, f"Заголовок страницы {cat_page_title} не совпадает с ожидаемым."

    # запускаем селениум
    driver = init_driver()
    # проверка геопозиции
    # driver.get('https://2ip.io/ru/geoip/')

    #
    level_to_start = 1
    result_tree = get_category_tree(driver, level_to_start, url, CAT_MENU_ITEMS_LOC)
    print(result_tree)


if __name__ == "__main__":
    main()
