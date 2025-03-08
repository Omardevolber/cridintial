import os
import time
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException

# استيراد WebDriverManager لإدارة التنزيل والتحديث التلقائي لـ ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager

# تهيئة نظام اللوج
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# إنشاء Flask app
app = Flask(__name__)
# يمكنك تغيير مفتاح الجلسة أو وضعه في متغير بيئة
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")


def setup_chrome_driver():
    """
    تهيئة Chrome WebDriver باستخدام WebDriverManager،
    بحيث لا تحتاج إلى تحديد مسار محدد لـ ChromeDriver.
    """
    chrome_options = Options()
    # وضع الـ headless إذا أردت العمل بدون واجهة
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # خيارات إضافية للثبات
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-browser-side-navigation')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')

    # يضبط ChromeDriverManager نسخة متوافقة مع متصفحك
    service = Service(ChromeDriverManager().install())

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
        raise


def run_selenium_script(email, password):
    """
    تنفيذ سكربت Selenium لتسجيل الدخول في بوابة الضرائب والحصول على بيانات الاعتماد.
    """
    credentials_dict = {}
    credentials_dir = os.path.join(os.getcwd(), 'cridintial')
    os.makedirs(credentials_dir, exist_ok=True)

    try:
        logger.info("Starting Selenium script execution")
        driver = setup_chrome_driver()

        try:
            # الذهاب لصفحة تسجيل الدخول
            logger.info("Navigating to login page")
            driver.get("https://profile.eta.gov.eg/TaxpayerProfile")
            time.sleep(2)

            # تعبئة بيانات الدخول
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

            # محاولة الضغط على زر "Select" إن وجد
            try:
                select_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='Select']"))
                )
                select_button.click()
                logger.info("Select button clicked")
                time.sleep(2)
            except TimeoutException:
                logger.info("No Select button found, continuing...")

            # الضغط على زر ERP
            erp_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.NAME, "ERP "))
            )
            erp_button.click()
            logger.info("ERP button clicked")
            time.sleep(2)

            # الضغط على أيقونة Add
            add_icon = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-icon-name="Add"]'))
            )
            add_icon.click()
            logger.info("Add icon clicked")
            time.sleep(2)

            # إدخال اسم النظام
            friendly_name_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[placeholder="Create a friendly name for the ERP system "]')
                )
            )
            friendly_name_input.clear()
            friendly_name_input.send_keys("Mohasib Friend")
            logger.info("Friendly name entered")
            time.sleep(2)

            # الضغط على زر Register
            register_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='Register']"))
            )
            register_button.click()
            logger.info("Register button clicked")
            time.sleep(3)

            # استخراج بيانات الاعتماد
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

            # حفظ بيانات الاعتماد في ملف
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


@app.route('/')
def index():
    """
    الصفحة الرئيسية لعرض فورم تسجيل الدخول.
    تأكد أن لديك ملف `index.html` في فولدر templates.
    """
    return render_template('index.html')


@app.route('/run-script', methods=['POST'])
def run_script():
    """
    يستقبل البيانات من النموذج ويشغّل سكربت Selenium.
    """
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash('يرجى إدخال البريد الإلكتروني وكلمة المرور', 'error')
        return redirect(url_for('index'))

    try:
        credentials = run_selenium_script(email, password)
        if credentials:
            # اعرض صفحة تحتوي على النتائج
            return render_template('result.html', credentials=credentials)
        else:
            flash('لم يتم العثور على بيانات الاعتماد', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    # شغّل التطبيق على المنفذ 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
