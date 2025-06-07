from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import tempfile

def get_driver(headless: bool = True):
    chrome_options = ChromeOptions()

    # Force Chrome to use a clean, temporary profile
    temp_profile = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_profile}")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")

    if headless:
        chrome_options.add_argument("--headless")
    else:
        chrome_options.add_argument("--remote-debugging-port=0")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--auto-open-devtools-for-tabs")

    # ✅ Match ChromeDriver version to installed Chrome
    service = ChromeService(ChromeDriverManager(driver_version="137.0.7151.55").install())
    return webdriver.Chrome(service=service, options=chrome_options)