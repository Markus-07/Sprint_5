import time

import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

from locators import (
    MainPageLocators,
    LoginPageLocators,
    RegisterPageLocators,
    PersonalCabinetLocators,
    ConstructorLocators,
)

BASE_URL = "https://qa-stellarburgers.education-services.ru/"
WAIT_TIME = 10


def wait_clickable(driver, locator):
    return WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable(locator))


def wait_visible(driver, locator):
    return WebDriverWait(driver, WAIT_TIME).until(EC.visibility_of_element_located(locator))


def register_user(driver, credentials):
    """Вспомогательная функция: открывает форму регистрации и регистрирует пользователя"""
    driver.get(BASE_URL)
    wait_clickable(driver, MainPageLocators.BTN_LOGIN_ACCOUNT).click()
    wait_clickable(driver, LoginPageLocators.LINK_REGISTER).click()

    wait_visible(driver, RegisterPageLocators.INPUT_NAME).send_keys(credentials["name"])
    wait_visible(driver, RegisterPageLocators.INPUT_EMAIL).send_keys(credentials["email"])
    wait_visible(driver, RegisterPageLocators.INPUT_PASSWORD).send_keys(credentials["password"])
    wait_clickable(driver, RegisterPageLocators.BTN_REGISTER).click()


def login_user(driver, credentials):
    """Вспомогательная функция: входит в аккаунт через форму входа"""
    # Дожидаемся, что страница входа полностью отрисовалась
    wait_visible(driver, LoginPageLocators.BTN_LOGIN)

    for attempt in range(3):  # до 3 попыток на случай перерисовки DOM
        try:
            email_input = wait_visible(driver, LoginPageLocators.INPUT_EMAIL)
            email_input.clear()  # очищаем, если поле предзаполнено после регистрации
            email_input.send_keys(credentials["email"])

            password_input = wait_visible(driver, LoginPageLocators.INPUT_PASSWORD)
            password_input.clear()
            password_input.send_keys(credentials["password"])

            wait_clickable(driver, LoginPageLocators.BTN_LOGIN).click()
            return  # всё получилось — выходим
        except StaleElementReferenceException:
            # Страница перерисовалась — пробуем ещё раз со свежими элементами
            continue


def go_to_cabinet(driver):
    """Вспомогательная функция: после входа переходим в личный кабинет"""
    # Сначала дожидаемся загрузки главной страницы — значит логин прошёл
    wait_visible(driver, ConstructorLocators.TAB_BUN)
    wait_clickable(driver, MainPageLocators.LINK_PERSONAL_CABINET).click()
    wait_visible(driver, PersonalCabinetLocators.BTN_LOGOUT)


def click_tab(driver, tab_locator):
    """Кликает по вкладке раздела, обходя перекрытие слоем страницы"""
    tab = wait_visible(driver, tab_locator)
    try:
        tab.click()
    except ElementClickInterceptedException:
        # вкладку перекрывает контейнер страницы — кликаем напрямую через JS
        driver.execute_script("arguments[0].click();", tab)


class TestRegistration:
    def test_successful_registration(self, driver, unique_credentials):
        """Успешная регистрация нового пользователя"""
        register_user(driver, unique_credentials)

        # После успешной регистрации оказываемся на странице входа
        wait_visible(driver, LoginPageLocators.BTN_LOGIN)
        assert "/login" in driver.current_url or "/register" not in driver.current_url

    def test_registration_invalid_password(self, driver, unique_credentials):
        """Ошибка при некорректном пароле (меньше 6 символов)"""
        credentials = dict(unique_credentials)
        credentials["password"] = "12345"  # 5 символов — некорректный пароль

        register_user(driver, credentials)

        # Ждём сообщение об ошибке
        error = wait_visible(driver, RegisterPageLocators.ERROR_PASSWORD)
        assert error.is_displayed()


class TestLogin:
    def test_login_by_button_on_main_page(self, driver, unique_credentials):
        """Вход по кнопке «Войти в аккаунт» на главной"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        wait_clickable(driver, MainPageLocators.BTN_LOGIN_ACCOUNT).click()
        login_user(driver, unique_credentials)

        go_to_cabinet(driver)
        assert "/account" in driver.current_url

    def test_login_via_personal_cabinet(self, driver, unique_credentials):
        """Вход через кнопку «Личный кабинет»"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        wait_clickable(driver, MainPageLocators.LINK_PERSONAL_CABINET).click()
        login_user(driver, unique_credentials)

        go_to_cabinet(driver)
        assert "/account" in driver.current_url

    def test_login_from_register_form(self, driver, unique_credentials):
        """Вход через кнопку «Войти» в форме регистрации"""
        register_user(driver, unique_credentials)

        # Открываем форму регистрации заново
        driver.get(BASE_URL + "register")
        # Нажимаем «Войти» в самой форме регистрации
        wait_clickable(driver, RegisterPageLocators.LINK_LOGIN).click()

        # Оказались на форме входа — входим
        login_user(driver, unique_credentials)
        go_to_cabinet(driver)
        assert "/account" in driver.current_url

    def test_login_from_password_recovery_form(self, driver, unique_credentials):
        """Вход через кнопку в форме восстановления пароля"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        wait_clickable(driver, MainPageLocators.BTN_LOGIN_ACCOUNT).click()

        # Переходим в форму восстановления пароля
        wait_clickable(driver, LoginPageLocators.LINK_RECOVERY).click()
        # Возвращаемся на вход по ссылке «Войти» (на этой странице ссылка, а не кнопка)
        wait_clickable(driver, LoginPageLocators.LINK_LOGIN_FROM_RECOVERY).click()
        login_user(driver, unique_credentials)

        go_to_cabinet(driver)
        assert "/account" in driver.current_url


class TestPersonalCabinet:
    def _login_and_open_cabinet(self, driver, unique_credentials):
        """Вспомогательный метод: регистрация, вход, открытие личного кабинета"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        wait_clickable(driver, MainPageLocators.BTN_LOGIN_ACCOUNT).click()
        login_user(driver, unique_credentials)
        wait_clickable(driver, MainPageLocators.LINK_PERSONAL_CABINET).click()
        wait_visible(driver, PersonalCabinetLocators.BTN_LOGOUT)

    def test_navigate_to_personal_cabinet(self, driver, unique_credentials):
        """Переход в личный кабинет по клику на «Личный кабинет»"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        wait_clickable(driver, MainPageLocators.LINK_PERSONAL_CABINET).click()
        login_user(driver, unique_credentials)

        # После входа попали на главную — снова идём в личный кабинет
        go_to_cabinet(driver)
        assert "/account" in driver.current_url

    def test_navigate_from_cabinet_to_constructor_by_button(self, driver, unique_credentials):
        """Переход из личного кабинета в конструктор по кнопке «Конструктор»"""
        self._login_and_open_cabinet(driver, unique_credentials)

        wait_clickable(driver, PersonalCabinetLocators.LINK_CONSTRUCTOR).click()
        wait_visible(driver, ConstructorLocators.TAB_BUN)
        assert driver.current_url.rstrip("/") == BASE_URL.rstrip("/")

    def test_navigate_from_cabinet_to_constructor_by_logo(self, driver, unique_credentials):
        """Переход из личного кабинета в конструктор по клику на логотип"""
        self._login_and_open_cabinet(driver, unique_credentials)

        wait_clickable(driver, PersonalCabinetLocators.IMG_LOGO).click()
        wait_visible(driver, ConstructorLocators.TAB_BUN)
        assert driver.current_url.rstrip("/") == BASE_URL.rstrip("/")

    def test_logout_from_account(self, driver, unique_credentials):
        """Выход из аккаунта по кнопке «Выход» в личном кабинете"""
        self._login_and_open_cabinet(driver, unique_credentials)

        wait_clickable(driver, PersonalCabinetLocators.BTN_LOGOUT).click()

        # После выхода снова видим форму входа
        wait_visible(driver, LoginPageLocators.INPUT_EMAIL)
        assert "/login" in driver.current_url


class TestConstructorSections:

    def test_navigate_to_buns_section(self, driver, unique_credentials):
        """Переход к разделу «Булки»"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        # «Булки» выбраны при открытии страницы — сначала переключаемся на «Соусы»
        click_tab(driver, ConstructorLocators.TAB_SAUCE)
        WebDriverWait(driver, WAIT_TIME).until(
            EC.text_to_be_present_in_element(ConstructorLocators.ACTIVE_TAB, "Соусы")
        )
        # Теперь кликаем «Булки» — если клик не сработает, тест это покажет
        click_tab(driver, ConstructorLocators.TAB_BUN)
        WebDriverWait(driver, WAIT_TIME).until(
            EC.text_to_be_present_in_element(ConstructorLocators.ACTIVE_TAB, "Булки")
        )
        active_tab = driver.find_element(*ConstructorLocators.ACTIVE_TAB)
        assert "Булки" in active_tab.text

    def test_navigate_to_sauces_section(self, driver, unique_credentials):
        """Переход к разделу «Соусы»"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        click_tab(driver, ConstructorLocators.TAB_SAUCE)
        WebDriverWait(driver, WAIT_TIME).until(
            EC.text_to_be_present_in_element(ConstructorLocators.ACTIVE_TAB, "Соусы")
        )
        active_tab = driver.find_element(*ConstructorLocators.ACTIVE_TAB)
        assert "Соусы" in active_tab.text

    def test_navigate_to_fillings_section(self, driver, unique_credentials):
        """Переход к разделу «Начинки»"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        click_tab(driver, ConstructorLocators.TAB_FILLING)
        WebDriverWait(driver, WAIT_TIME).until(
            EC.text_to_be_present_in_element(ConstructorLocators.ACTIVE_TAB, "Начинки")
        )
        active_tab = driver.find_element(*ConstructorLocators.ACTIVE_TAB)
        assert "Начинки" in active_tab.text
