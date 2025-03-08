import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

def setup_chrome_driver():
    """Configure Chrome WebDriver with appropriate options for Replit environment"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Additional options for stability
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-browser-side-navigation')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')

        # Set binary location for chromium in Replit with exact path
        chrome_binary = "/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium"
        chrome_options.binary_location = chrome_binary
        logger.info(f"Chrome binary location set to: {chrome_binary}")

        # Set up ChromeDriver service with exact path
        chromedriver_path = "/nix/store/3qnxr5x6gw3k9a9i7d0akz0m6bksbwff-chromedriver-125.0.6422.141/bin/chromedriver"
        service = Service(executable_path=chromedriver_path)
        logger.info(f"ChromeDriver path set to: {chromedriver_path}")

        # Initialize WebDriver with error handling
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Error setting up Chrome WebDriver: {str(e)}")
        raise

def run_selenium_script(email, password):
    """Execute the Selenium automation script"""
    credentials_dict = {}
    credentials_dir = os.path.join(os.getcwd(), 'cridintial')
    os.makedirs(credentials_dir, exist_ok=True)

    try:
        logger.info("Starting Selenium script execution")
        driver = setup_chrome_driver()

        try:
            # Navigate to login page
            logger.info("Navigating to login page")
            driver.get("https://profile.eta.gov.eg/TaxpayerProfile")
            time.sleep(2)

            # Login process
            logger.info("Attempting to login")
            email_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.send_keys(email)

            password_field = driver.find_element(By.ID, "Password")
            password_field.send_keys(password)

            submit_button = driver.find_element(By.ID, "submit")
            submit_button.click()
            logger.info("Login form submitted")
            time.sleep(2)

            # Wait for potential "Select" button
            try:
                select_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='Select']"))
                )
                select_button.click()
                logger.info("Select button clicked")
                time.sleep(2)
            except TimeoutException:
                logger.info("No Select button found, continuing...")

            # Click ERP button
            erp_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.NAME, "ERP "))
            )
            erp_button.click()
            logger.info("ERP button clicked")
            time.sleep(2)

            # Click Add icon
            add_icon = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-icon-name="Add"]'))
            )
            add_icon.click()
            logger.info("Add icon clicked")
            time.sleep(2)

            # Enter friendly name
            friendly_name_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    '[placeholder="Create a friendly name for the ERP system "]'))
            )
            friendly_name_input.clear()
            friendly_name_input.send_keys("Mohasib Friend")
            logger.info("Friendly name entered")
            time.sleep(2)

            # Click Register
            register_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='Register']"))
            )
            register_button.click()
            logger.info("Register button clicked")
            time.sleep(3)

            # Extract credentials
            credential_containers = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.vertialFlexDiv"))
            )

            for container in credential_containers:
                try:
                    label = container.find_element(By.CSS_SELECTOR, "label.ms-Label").text.strip()
                    value = container.find_element(By.CSS_SELECTOR, "input.ms-TextField-field").get_attribute("value").strip()
                    credentials_dict[label] = value
                    logger.info(f"Extracted credential: {label}")
                except Exception as e:
                    logger.error(f"Error extracting credential: {str(e)}")

            # Save credentials to file
            if credentials_dict:
                reg_number = credentials_dict.get("Registration Number", "unknown")
                client_id = credentials_dict.get("Client ID", "unknown")
                client_secret = credentials_dict.get("Client Secret 1", "unknown")

                filename = f"{reg_number}_{client_id}_{client_secret}.txt"
                filepath = os.path.join(credentials_dir, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    for key, value in credentials_dict.items():
                        f.write(f"{key}: {value}\n")
                logger.info(f"Credentials saved to {filepath}")

        except Exception as e:
            logger.error(f"Error during automation: {str(e)}")
            raise

    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
        raise

    finally:
        if 'driver' in locals():
            driver.quit()
            logger.info("Browser closed")

    return credentials_dict
