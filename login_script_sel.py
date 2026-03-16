import logging
from seleniumbase import SB
from config import EMAIL, PASSWORD, LOGIN_URL


# Logging setup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Login Function

def login():

    with SB(
        uc=True,                 
        test=True,
        locale_code="en",
        headless=False
    ) as sb:

        try:

            # Open login page

            logging.info("Opening login page")

            sb.driver.uc_open_with_reconnect(LOGIN_URL, 3)

            sb.sleep(3)


            # Fill credentials

            logging.info("Entering credentials")

            sb.type("#email", EMAIL)

            sb.type("input[type='password']", PASSWORD)

            sb.sleep(2)


            # Reconnect before captcha

            sb.driver.reconnect(0.5)


            # Handle Cloudflare Turnstile

            logging.info("Checking for verification challenge")

            if sb.is_element_visible('iframe[src*="challenge"]', timeout=5):

                logging.info("Captcha detected")

                sb.uc_gui_click_captcha()

                sb.sleep(5)

            else:

                logging.info("No captcha detected")


            # Click Login

            logging.info("Submitting login form")

            sb.driver.uc_click('button:contains("Sign")', reconnect_time=3)

            sb.sleep(6)


            # Check login result

            current_url = sb.get_current_url()

            logging.info(f"Current URL: {current_url}")

            if "login" not in current_url.lower():

                logging.info("Login successful")

                sb.highlight("body")

                sb.post_message("Login successful!")

            else:

                logging.error("Login failed")

                sb.save_screenshot("login_failed.png")

        except Exception as e:

            logging.error(f"Unexpected error: {e}")

            sb.save_screenshot("error.png")


# -----------------------------

if __name__ == "__main__":
    login()