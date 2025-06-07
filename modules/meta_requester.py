import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils.selenium_utils import get_driver
from utils.logger import setup_logger

from config import loader
from utils import telegram_utils

class MetaAccountRequester:
    logger = setup_logger("meta_cron_bot")

    def __init__(self, headless=True, timeout=15):
        self.logger.info(f"Starting Meta Account Data Requester [{'HEADLESS' if headless == 'True' else 'HEADED'} MODE]")
        self.timeout = timeout
        self.driver = get_driver(headless)
        self.wait = WebDriverWait(self.driver, self.timeout)
        self.logger = setup_logger("meta_cron_bot")
    
    def handle_cookie_banner(self):
        try:
            cookie_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Decline optional cookies')]")))
            cookie_button.click()
            self.logger.info("Clicked on 'Decline optional cookies' button")
        except TimeoutException as e:
            self.logger.warning("Cookie banner not found or already handled: %s", e)

    def is_logged_in(self):
            cookies = self.driver.get_cookies()
            instagram_cookies = [cookie for cookie in cookies if 'instagram' in cookie['domain']]
            if instagram_cookies:
                self.logger.info("Found existing Instagram cookies, skipping login")
                return True
            self.logger.info("No valid Instagram cookies found")
            return False
    
    def login(self):
        url = 'https://accountscenter.instagram.com/info_and_permissions/dyi/'
        self.driver.get(url)
        self.logger.info("Navigated to Instagram Accounts Center")

        if self.is_logged_in():
                return
                
        self.handle_cookie_banner()
        self.fill_login_data()
        self.navigate_to_data_request()
    
    def handle_otp(self):        
        try:
            # Wait to see if we get redirected to 2FA page
            self.wait.until(EC.url_contains("/accounts/login/two_factor"))
            self.logger.info("2FA verification required")
            
            
            # This snippet is to rework because we cannot send messages
            # Handle 2FA input with Telegram Bot API
            # telegram_utils.send_message("Please enter the 2FA code sent to your device.")
            # telegram_utils.wait_for_reply("Waiting for 2FA code...")
            
            otp_code = input("Please enter the 2FA code: ")
            otp_field = self.wait.until(EC.presence_of_element_located((By.NAME, "verificationCode")))
            otp_field.send_keys(otp_code)
            
            # Click confirm button
            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button'][contains(., 'Confirm') or .//div[contains(text(), 'Confirm')] or .//span[contains(text(), 'Confirm')]]")))
            submit_button.click()
            self.logger.info("Submitted 2FA code")
            
            # Wait for successful login after 2FA
            self.wait.until(EC.url_contains("/accounts/onetap"))
            self.logger.info("Redirected to Instagram Home")
            
        except TimeoutException:
            # No 2FA required, check if login was successful
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Settings')]")))
                self.logger.info("Login successful without 2FA")
            except TimeoutException:
                self.logger.error("Login failed")
                raise RuntimeError("Login verification failed")
            
    def fill_login_data(self):
        try:
            username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_field.send_keys(loader.INSTAGRAM_USERNAME)
            self.logger.info("Filled username: %s", loader.INSTAGRAM_USERNAME)

            password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_field.send_keys(loader.INSTAGRAM_PASSWORD)
            self.logger.info("Filled password")

        
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit'][.//div[contains(text(), 'Log in')]]")))
            login_button.click()
            self.logger.info("Clicked login button")
            
            self.handle_otp()  # Handle OTP if required
            

        except TimeoutException as e:
            self.logger.error(f"Failed to fill login data: {e}")
            raise RuntimeError("Login failed")
    
    

    def navigate_to_data_request(self):
        info_request_url = 'https://accountscenter.instagram.com/info_and_permissions/dyi/'
        self.driver.get(info_request_url)
        self.logger.info("Navigated to Data Download Request page")
        time.sleep(3)  # Wait for the page to load

    def _click_element(self, xpath, description):
        """Helper method to click elements with logging"""
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
            self.logger.info(f"Clicked on {description}")
            return True
        except TimeoutException as e:
            self.logger.error(f"Failed to click {description}: {e}")
            return False

    def _select_account(self):
        """Select the Instagram account"""

        self.logger.info("Selecting Instagram account for data download")
        print(f"{loader.INSTAGRAM_USERNAME}")
        account_xpath = f'//label[.//div[contains(normalize-space(.), "{loader.INSTAGRAM_USERNAME}")]]//input[@type="checkbox"]'
        account = self.wait.until(EC.element_to_be_clickable((By.XPATH, account_xpath)))
        account.click()
        self.logger.info(f"Selected account: {loader.INSTAGRAM_USERNAME}")

    def _select_data_type(self):
        """Select the type of data to download"""
        steps = [
            ("//span[contains(text(), 'Download or transfer information')]", "Download or transfer information"),
            ("//span[contains(text(), 'Next')]", "Next"),
        ]
        for xpath, description in steps:
            if not self._click_element(xpath, description):
                raise RuntimeError(f"Failed at step: {description}")

        self._select_account()

        next_steps = [
            ("//span[contains(text(), 'Next')]", "Next after selecting account"),
            ("//div[contains(text(), 'Some of your information')]", "Some of your information"),
            ("//div[contains(text(), 'Followers and following')]", "Followers and following"),
            ("(//span[normalize-space(.)='Next']/ancestor::div[@role='button'])[last()]", "Next after selecting data type")
        ]
        for xpath, description in next_steps:
            time.sleep(1)  # Add small delay between actions
            if not self._click_element(xpath, description):
                raise RuntimeError(f"Failed at step: {description}")

    def _configure_download_options(self):
        """Configure download options (format and date range)"""
        # Set download method
        self._click_element("//div[contains(text(), 'Download to device')]", "Download to device")
        
        time.sleep(1)  # Wait for the dropdown to open
        # Set date range
        self._click_element("//div[contains(text(), 'Date range')]", "Date range")
        self._click_element("//div[contains(text(), 'Last month')]", "Last month option")
        self._click_element("//span[contains(text(), 'Save')]", "Save date range")
        
        time.sleep(1)  # Wait for the dropdown to open
        # Set format
        self._click_element("//div[contains(text(), 'Format')]", "Format")
        self._click_element("//div[contains(text(), 'JSON')]", "JSON format")
        self._click_element("(//span[normalize-space(.)='Save']/ancestor::div[@role='button'])[last()]", "Save format")

        time.sleep(5)  # Wait for the dropdown to open

    def submit_data_request(self):
        """Main method to submit the data request"""
        try:
            self._select_data_type()
            self._configure_download_options()
            
            # Submit the request
            if self._click_element("(//span[normalize-space(.)='Create files']/ancestor::div[@role='button'])[last()]", "Create files"):
                self.logger.info("Data request submitted successfully")
            else:
                raise RuntimeError("Failed to submit data request")

        except Exception as e:
            self.logger.error(f"Error during data request submission: {e}")
            raise RuntimeError(f"Failed to submit data request: {e}")
        
    def close(self):
        self.driver.quit()
        self.logger.info("Browser closed and resources cleaned up")
        self.logger.info("Terminating Meta Account Requester...")