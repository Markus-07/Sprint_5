import random
import string
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Генератор уникального email: имя_фамилия_когорта_3цифры@домен
def generate_email():
    name = "testtestov"
    cohort = "1999"
    digits = "".join(random.choices(string.digits, k=3))
    return f"{name}{cohort}{digits}@yandex.ru"


# Генератор пароля (минимум 6 символов)
def generate_password(length=7):
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


# Фикстура браузера: каждый тест открывает свой Chrome и закрывает его в конце
@pytest.fixture(scope="function")
def driver():
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


# Фикстура с уникальными данными для регистрации
@pytest.fixture
def unique_credentials():
    return {
        "name": "TestUser",
        "email": generate_email(),
        "password": generate_password(),
    }
