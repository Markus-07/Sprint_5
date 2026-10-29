# Локаторы главной страницы
class MainPageLocators:
    # Кнопка «Войти в аккаунт» на главной
    BTN_LOGIN_ACCOUNT = ("xpath", "//button[contains(text(), 'Войти в аккаунт')]")
    # Кнопка «Личный кабинет» в шапке
    LINK_PERSONAL_CABINET = ("xpath", "//a[contains(@href, '/account')]")


# Локаторы страницы входа
class LoginPageLocators:
    # Поле Email
    INPUT_EMAIL = ("xpath", "(//label[text()='Email']/following::input)[1]")
    # Поле Пароль
    INPUT_PASSWORD = ("xpath", "(//label[text()='Пароль']/following::input)[1]")
    # Кнопка «Войти»
    BTN_LOGIN = ("xpath", "//button[contains(text(), 'Войти')]")
    # Ссылка «Зарегистрироваться» на странице входа
    LINK_REGISTER = ("xpath", "//a[contains(@href, '/register')]")
    # Ссылка «Восстановить пароль»
    LINK_RECOVERY = ("xpath", "//a[contains(@href, '/forgot-password')] | //a[contains(text(), 'Восстановить пароль')]")
        # Ссылка «Войти» на странице восстановления пароля
    LINK_LOGIN_FROM_RECOVERY = ("xpath", "//a[contains(@href, '/login')]")


# Локаторы страницы регистрации
class RegisterPageLocators:
    # Поле Имя
    INPUT_NAME = ("xpath", "(//label[text()='Имя']/following::input)[1]")
    # Поле Email
    INPUT_EMAIL = ("xpath", "(//label[text()='Email']/following::input)[1]")
    # Поле Пароль
    INPUT_PASSWORD = ("xpath", "(//label[text()='Пароль']/following::input)[1]")
    # Кнопка «Зарегистрироваться»
    BTN_REGISTER = ("xpath", "//button[contains(text(), 'Зарегистрироваться')]")
    # Текст ошибки «Некорректный пароль»
    ERROR_PASSWORD = ("xpath", "//p[contains(text(), 'Некорректный пароль')]")


# Локаторы личного кабинета
class PersonalCabinetLocators:
    # Кнопка «Выход»
    BTN_LOGOUT = ("xpath", "//button[contains(text(), 'Выход')] | //button[contains(text(), 'Выйти')]")
    # Кнопка «Конструктор»
        # Кнопка «Конструктор» (текст лежит в дочернем <p>, поэтому ищем по всему содержимому ссылки)
    LINK_CONSTRUCTOR = ("xpath", "//a[contains(., 'Конструктор')]")

    # Логотип Stellar Burgers в шапке
    IMG_LOGO = ("xpath", "//a[contains(@class, 'header__logo')] | //div[contains(@class, 'logo')]")


# Локаторы разделов конструктора
class ConstructorLocators:
    # Вкладка «Булки»
    TAB_BUN = ("xpath", "//span[contains(text(), 'Булки')]")
    # Вкладка «Соусы»
    TAB_SAUCE = ("xpath", "//span[contains(text(), 'Соусы')]")
    # Вкладка «Начинки»
    TAB_FILLING = ("xpath", "//span[contains(text(), 'Начинки')]")
