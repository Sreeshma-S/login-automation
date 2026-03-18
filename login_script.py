import os
import time
import random
import logging
from datetime import datetime
from DrissionPage import ChromiumPage, ChromiumOptions
from config import EMAIL, PASSWORD, BASE_URL, LOGIN_URL

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
    logging.info("Checking for Cloudflare verification")

    start = time.time()

    while time.time() - start < 180:

        page.actions.move(200, 300)
        time.sleep(1)
        page.actions.move(400, 500)

        frames = page.eles('xpath://iframe[contains(@src,"challenge") or contains(@src,"turnstile")]')

        if not frames:
            logging.info("No verification detected")
            return

        logging.info("Cloudflare challenge detected")

        # try solving automatically
        solve_turnstile(page)

        time.sleep(5)

    logging.warning("Verification timeout")

def solve_turnstile(page):

    frame = page.ele('xpath://iframe[contains(@src,"turnstile")]', timeout=10)

    if not frame:
        return

    logging.info("Turnstile frame detected")

    turnstile = frame.frame()

    checkbox = turnstile.ele('xpath://input[@type="checkbox"]', timeout=5)

    if checkbox:
        checkbox.click()
        logging.info("Clicked Cloudflare checkbox")

def login():
    # Chromium browser configuration object
    co = ChromiumOptions()

    # preferences to make the browser more human-like
    # co.set_user_data_path("./chrome_profile")
    # co.set_user_data_path("/tmp/chrome_fresh_profile")
    co.set_browser_path("/usr/bin/brave-browser")
    co.set_user_data_path("./brave_profile")
    co.set_argument("--start-maximized")
    co.set_argument("--disable-blink-features=AutomationControlled")
    co.set_argument("--disable-infobars")
    co.set_argument("--disable-dev-shm-usage")
    co.set_argument("--no-sandbox")

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

        wait_for_verification(page)

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
