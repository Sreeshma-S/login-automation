import os
import time
import random
import logging
from datetime import datetime
from DrissionPage import ChromiumPage, ChromiumOptions
from config import EMAIL, PASSWORD, BASE_URL, LOGIN_URL, HEADLESS

logging.basicConfig(level=logging.INFO)

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def save_screenshot(page, name):
    filename = f"{SCREENSHOT_DIR}/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    page.get_screenshot(filename)
    logging.info(f"Screenshot saved: {filename}")


def type_like_human(element, text):
    """
    Type text like a human (character by character)
    """
    for char in text:
        element.input(char)
        time.sleep(random.uniform(0.08, 0.25))

# exception handling for verification challenge
def wait_for_verification(page):
    """
    Wait for Cloudflare / verification challenge
    to be completed manually if it appears.
    """

    logging.info("Checking for verification challenge")

    start = time.time()

    while time.time() - start < 180:

        frames = page.eles('xpath://iframe[contains(@src,"challenges.cloudflare")]')

        if not frames:
            logging.info("No verification iframe detected")
            return

        logging.info("Verification present. Please complete it in browser...")
        time.sleep(5)

        frames = page.eles('xpath://iframe[contains(@src,"challenges.cloudflare")]')

        if not frames:
            logging.info("Verification completed")
            return

    logging.warning("Verification timeout reached")


def login():
    # Chromium browser configuration object
    co = ChromiumOptions()

    # preferences to make the browser more human-like
    co.set_user_data_path("./user_profile")
    
    if HEADLESS:
        co.executable_path = "/usr/bin/google-chrome" 
        co.set_argument("--headless")
        co.set_argument("--remote-debugging-port=9224")
        co.set_argument("--remote-debugging-address=127.0.0.1")  # force IPv4
        co.set_argument("--window-size=1920,1080")
        co.set_argument("--disable-gpu")          # required for headless on Linux
        co.set_argument("--no-sandbox")           # required for root or restricted env
        co.set_argument("--disable-dev-shm-usage") # avoid shared memory issues
        co.set_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        co.set_argument("--start-maximized")
    else:
        co.set_argument("--start-maximized")
    
    co.set_argument("--disable-blink-features=AutomationControlled")
    co.set_argument("--disable-infobars")

    # creates the browser instance
    page = ChromiumPage(co)

    try:

        logging.info("Opening homepage")
        page.get(BASE_URL)

        time.sleep(random.uniform(2, 4))

        logging.info("Opening login page")
        page.get(LOGIN_URL)

        # wait for email field
        email = page.ele("#email", timeout=30)

        wait_for_verification(page)

        logging.info("Entering credentials")

        time.sleep(random.uniform(1, 2))

        # EMAIL typing
        email.click()
        type_like_human(email, EMAIL)

        time.sleep(random.uniform(1, 2))

        # PASSWORD typing
        pwd = page.ele('xpath://input[@type="password"]', timeout=20)
        pwd.click()
        type_like_human(pwd, PASSWORD)

        time.sleep(random.uniform(1, 2))

        wait_for_verification(page)

        logging.info("Submitting login")

        login_btn = page.ele('xpath://button[contains(.,"Sign In") or contains(.,"Login")]', timeout=20)

        if login_btn:
            login_btn.click()

        time.sleep(5)

        logging.info(f"Current URL: {page.url}")

        if "login" not in page.url.lower():
            logging.info("Login successful")
            save_screenshot(page, "login_success")
        else:
            logging.error("Login failed")
            save_screenshot(page, "login_failed")

    except Exception as e:
        logging.error(f"Error: {e}")
        save_screenshot(page, "error")

    finally:
        time.sleep(5)


if __name__ == "__main__":
    login()