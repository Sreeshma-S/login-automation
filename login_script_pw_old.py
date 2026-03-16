import os
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError
from config import EMAIL, PASSWORD, BASE_URL, LOGIN_URL, HEADLESS

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def take_screenshot(page, name):
    """Save screenshot with timestamp"""
    filename = f"{SCREENSHOT_DIR}/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    page.screenshot(path=filename, full_page=True)
    logging.info(f"Screenshot saved: {filename}")


def handle_cookie_banner(page):
    """Accept cookie popup if visible"""
    try:
        page.wait_for_selector("button:has-text('Accept')", timeout=5000)
        page.locator("button:has-text('Accept')").first.click()
        logging.info("Cookie banner accepted")
    except:
        logging.info("Cookie banner not present")


def login():
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        try:

            logging.info("Opening homepage")

            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)

            take_screenshot(page, "homepage_loaded")

            handle_cookie_banner(page)

            logging.info("Opening login page")

            page.goto(LOGIN_URL, wait_until="domcontentloaded")

            take_screenshot(page, "login_page_loaded")

            logging.info("Waiting for login fields")

            page.wait_for_selector("#email", timeout=30000)

            logging.info("Entering credentials")

            print(EMAIL, PASSWORD)

            page.fill("#email", EMAIL)
            page.fill("input[type='password']", PASSWORD)

            page.wait_for_timeout(2000)

            logging.info("Submitting login form")

            page.locator("button:has-text('Sign'), button:has-text('Login')").first.click()

            page.wait_for_timeout(5000)

            # Detect login result
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
            browser.close()


if __name__ == "__main__":
    login()