"""

"""
import json
import time
from pprint import pprint

from fake_useragent import UserAgent
from random import randint
import time
import requests
from requests import Session, Response
from typing import Optional, List, Dict, Union, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException
import pandas as pd
from tqdm import tqdm
import os
from datetime import datetime, timedelta

PATH_DATA = "data"
TIMEOUT = 10
PAUSE_MIN = 0
PAUSE_MAX = 2
#
BASE_URL = 'https://irmag.ru'
CAT_URL = '/cat'
CAT_PAGE_SIGN = "Каталог - IRMAG.RU"
#
CAT_CATEGORY_MENU_LOC = ('xpath', '//div[@class="alert alert-grey p-10"]')
CAT_MENU_ITEMS_LOC = 'btn btn-link preload'


def pause():
    """
    Рандомная пауза
    """

    timeout = randint(PAUSE_MIN, PAUSE_MAX)
    time.sleep(timeout)


def format_time(seconds):
    timedelta_obj = timedelta(seconds=seconds)
    hours, remainder = divmod(timedelta_obj.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"


def save_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


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


def get_category_tree(
        driver: WebDriver,
        parent_category_name: str,
        url: str,
        class_name: str,
        max_depth: Optional[int] = None,
        file_handler: Optional[object] = None
) -> Optional[Union[Dict[str, Any], None]]:

    wait = WebDriverWait(driver, TIMEOUT, poll_frequency=1)
    driver.get(url)

    try:
        wait.until(EC.visibility_of_element_located(CAT_CATEGORY_MENU_LOC))
        cat_page_src = driver.page_source
        cat_page_soup = BeautifulSoup(cat_page_src, 'lxml')

        cat_tree = {}

        category_links = list(cat_page_soup.findAll('a', class_=class_name))
        total_categories = len(category_links)

        for i, category in enumerate(category_links, start=1):
            tag_href = category['href'].split('/')[2]
            cat_dict = {
                'level': len(parent_category_name.split(' ')),
                f'category_id_lvl_{len(parent_category_name.split(" "))}': tag_href,
                'name': category.text.split('\n')[1].strip(),
                'url': BASE_URL + CAT_URL + '/' + tag_href,
                'subcategories': None
            }

            if max_depth is None or len(parent_category_name.split(' ')) < max_depth:
                cat_dict['subcategories'] = get_category_tree(driver, f"{parent_category_name} > {cat_dict['name']}",
                                                              BASE_URL + CAT_URL + '/' + tag_href, class_name,
                                                              max_depth, file_handler)

            cat_tree[tag_href] = cat_dict

            # Вывод прогресс-бара
            progress = i / total_categories * 100
            print(
                f"\r[{parent_category_name} > {cat_dict['name']}] | {progress:.2f}% processed | {i}/{total_categories} categories",
                end='', flush=True)

        print()  # Переход на новую строку после завершения прогресс-бара

        pause()

        # Запись данных в файл после завершения парсинга каждой категории первого уровня
        file_handler.write(json.dumps(cat_tree, ensure_ascii=False, indent=2))
        file_handler.write("\n")

        return cat_tree if cat_tree else None
    except TimeoutException:
        pause()
        return None


def main():
    url = BASE_URL + CAT_URL
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    # session = Session()

    response = get_page(url, headers, TIMEOUT)
    cat_page_soup = BeautifulSoup(response.text, 'lxml')

    # проверка, что страница каталога доступна и что это именно она
    cat_page_title = cat_page_soup.find('title').text
    assert response.status_code == 200, "Запрос вернул статус-код, который отличается от 200."
    assert cat_page_title == CAT_PAGE_SIGN, f"Заголовок страницы {cat_page_title} не совпадает с ожидаемым."

    # готовим каталог для сохранения данных
    # запускаем селениум
    driver = init_driver()
    # проверка геопозиции
    # driver.get('https://2ip.io/ru/geoip/')

    # Создаем файл для сохранения информации
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    curr_catalog = os.path.dirname(__file__)
    subdirs_list = [name for name in os.listdir(curr_catalog) if os.path.isdir(os.path.join(curr_catalog, name))]

    if PATH_DATA not in subdirs_list:
        os.mkdir(PATH_DATA)
        print(f"В текущем каталоге создан каталог '{PATH_DATA}' для хранения данных.")

    filename = f'{PATH_DATA}/category_{current_datetime}.json'
    file_handler = open(filename, 'w', encoding='utf-8')

    start_time = datetime.now()
    level_to_start = 1
    max_depth = 3

    result_tree = get_category_tree(driver, 'Top Level', url, CAT_MENU_ITEMS_LOC, max_depth, file_handler)

    end_time = datetime.now()
    total_execution_time = (end_time - start_time).total_seconds()

    # Закрытие файла
    file_handler.close()

    print(f"\nTotal script execution time: {format_time(total_execution_time)}")
    print(f"The collected category data is saved to a file: {filename}")


if __name__ == "__main__":
    main()
