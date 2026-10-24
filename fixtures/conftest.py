import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.generators import generate_email, generate_password

@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def unique_credentials():
    return {
        "email": generate_email(cohort="1999"),
        "password": generate_password()
    }
