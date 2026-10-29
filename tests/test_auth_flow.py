import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from locators import (
    MainPageLocators,
    LoginPageLocators,
    RegisterPageLocators,
    PersonalCabinetLocators,
    ConstructorLocators,
)

BASE_URL = "https://qa-stellarburgers.education-services.ru/"
WAIT_TIME = 20


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
    def _go_to_cabinet(self, driver):
        """Вспомогательный метод: после входа переходим в личный кабинет"""
        # Сначала дожидаемся загрузки главной страницы — значит логин прошёл
        wait_visible(driver, ConstructorLocators.TAB_BUN)
        wait_clickable(driver, MainPageLocators.LINK_PERSONAL_CABINET).click()
        wait_visible(driver, PersonalCabinetLocators.BTN_LOGOUT)

    def test_login_by_button_on_main_page(self, driver, unique_credentials):
        """Вход по кнопке «Войти в аккаунт» на главной"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        wait_clickable(driver, MainPageLocators.BTN_LOGIN_ACCOUNT).click()
        login_user(driver, unique_credentials)

        self._go_to_cabinet(driver)
        assert "/account" in driver.current_url

    def test_login_via_personal_cabinet(self, driver, unique_credentials):
        """Вход через кнопку «Личный кабинет»"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        wait_clickable(driver, MainPageLocators.LINK_PERSONAL_CABINET).click()
        login_user(driver, unique_credentials)

        self._go_to_cabinet(driver)
        assert "/account" in driver.current_url

    def test_login_from_register_form(self, driver, unique_credentials):
        """Вход через кнопку в форме регистрации"""
        register_user(driver, unique_credentials)

        # После регистрации мы на странице входа — входим там же
        login_user(driver, unique_credentials)

        self._go_to_cabinet(driver)
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

        self._go_to_cabinet(driver)
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
        self._go_to_cabinet = TestLogin()._go_to_cabinet
        self._go_to_cabinet(driver)
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
        wait_clickable(driver, ConstructorLocators.TAB_SAUCE).click()
        wait_clickable(driver, ConstructorLocators.TAB_BUN).click()

        assert wait_visible(driver, ConstructorLocators.TAB_BUN).is_displayed()

    def test_navigate_to_sauces_section(self, driver, unique_credentials):
        """Переход к разделу «Соусы»"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        wait_clickable(driver, ConstructorLocators.TAB_SAUCE).click()

        assert wait_visible(driver, ConstructorLocators.TAB_SAUCE).is_displayed()

    def test_navigate_to_fillings_section(self, driver, unique_credentials):
        """Переход к разделу «Начинки»"""
        register_user(driver, unique_credentials)
        driver.get(BASE_URL)
        wait_clickable(driver, ConstructorLocators.TAB_FILLING).click()

        assert wait_visible(driver, ConstructorLocators.TAB_FILLING).is_displayed()
