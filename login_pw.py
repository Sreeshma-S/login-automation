import os
import logging
import random
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError
from config import EMAIL, PASSWORD, BASE_URL, LOGIN_URL

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


# Utility functions

def random_delay(a=1.5, b=3.5):
    time.sleep(random.uniform(a, b))


def take_screenshot(page, name):
    filename = f"{SCREENSHOT_DIR}/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    page.screenshot(path=filename, full_page=True)
    logging.info(f"Screenshot saved: {filename}")


# Human behaviour simulation

def human_mouse_move(page, x, y):

    start_x = random.randint(200, 500)
    start_y = random.randint(200, 500)

    page.mouse.move(start_x, start_y)

    steps = random.randint(30, 60)

    for i in range(steps):
        nx = start_x + (x - start_x) * (i / steps)
        ny = start_y + (y - start_y) * (i / steps)

        page.mouse.move(nx, ny)
        time.sleep(random.uniform(0.01, 0.04))


def human_type(page, selector, text):

    page.click(selector)

    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(0.05, 0.15))


def human_scroll(page):
    page.mouse.wheel(0, random.randint(300, 700))
    random_delay(0.5, 1.5)


# Cookie banner

def handle_cookie_banner(page):

    try:
        page.wait_for_selector("button:has-text('Accept')", timeout=5000)

        page.locator("button:has-text('Accept')").first.click()

        logging.info("Cookie banner accepted")

    except:
        logging.info("Cookie banner not present")


# Cloudflare verification
def handle_cloudflare(page):
    """
    If Cloudflare Turnstile appears, wait until it is solved manually.
    """
    try:
        logging.info("Checking for Cloudflare verification")

        # Wait briefly for the challenge iframe to appear (if it will)
        page.wait_for_timeout(3000)

        challenge_frame = page.locator("iframe[src*='challenges.cloudflare.com']")

        if challenge_frame.count() > 0 and challenge_frame.first.is_visible():
            logging.info("Cloudflare challenge detected. Please solve it in the browser...")

            # Wait until the iframe disappears (verification completed)
            page.wait_for_selector(
                "iframe[src*='challenges.cloudflare.com']",
                state="detached",
                timeout=180000  # up to 3 minutes
            )

            logging.info("Verification completed by user")

        else:
            logging.info("No verification challenge present")

    except TimeoutError:
        logging.error("Verification not completed within timeout")


# Main Login

def login():

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(

            user_data_dir="./user_profile",

            channel="chrome",

            headless=False,

            viewport={"width": 1280, "height": 800},

            locale="en-US",

            timezone_id="Asia/Dubai",

            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",

            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )

        page = context.new_page()

        try:

            logging.info("Opening homepage")

            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)

            random_delay()

            # take_screenshot(page, "homepage_loaded")

            human_mouse_move(page, 600, 300)

            human_scroll(page)

            handle_cookie_banner(page)

            # logging.info("Opening login page")

            page.goto(LOGIN_URL, wait_until="domcontentloaded")

            random_delay()

            # take_screenshot(page, "login_page_loaded")

            # logging.info("Waiting for login fields")

            page.wait_for_selector("#email", timeout=30000)

            logging.info("Entering credentials")

            print(EMAIL, PASSWORD)

            human_mouse_move(page, 500, 350)

            human_type(page, "#email", EMAIL)

            random_delay(1, 2)

            human_type(page, "input[type='password']", PASSWORD)

            random_delay(2, 4)

            human_scroll(page)

            handle_cloudflare(page)

            random_delay(2, 4)

            page.wait_for_timeout(8000)

            logging.info("Submitting login form")

            page.locator("button:has-text('Sign'), button:has-text('Login')").first.click()

            handle_cloudflare(page)

            random_delay(5, 7)

            if "login" not in page.url.lower():

                logging.info("Login successful")

                take_screenshot(page, "login_success")

            else:

                logging.error("Login failed")

                take_screenshot(page, "login_failed")

        except TimeoutError:

            logging.error("Timeout occurred while locating elements")

            take_screenshot(page, "timeout_error")

        except Exception as e:

            logging.error(f"Unexpected error: {e}")

            take_screenshot(page, "unexpected_error")

        finally:

            context.close()


if __name__ == "__main__":
    login()