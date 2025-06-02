# utils/selenium_utils.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

def get_driver(headless: bool = True):
    """
    Launch a Chrome WebDriver without specifying a --user-data-dir.
    By omitting that flag entirely, Chrome will automatically create
    and discard its own temp profile each time, avoiding the "in use" error.
    """
    chrome_options = ChromeOptions()

    # ─── Basic flags ───
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")

    # ─── Headless vs. headed ───
    if headless == True:
        # Use headless mode for Chrome
        chrome_options.add_argument("--headless")
    else:
        # If you want DevTools open, you can use port 0 so it never collides:
        chrome_options.add_argument("--remote-debugging-port=0")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--auto-open-devtools-for-tabs")

    service = ChromeService(ChromeDriverManager().install())

    # This line will no longer trigger the "user data dir in use" error,
    # because we are not passing --user-data-dir at all.
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
