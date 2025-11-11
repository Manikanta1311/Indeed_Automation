import random
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class IndeedAutoApply:
    def __init__(self, config_path="config.json"):
        # Load config credentials
        with open(config_path, "r") as f:
            config = json.load(f)

        self.email = config.get("email")
        self.password = config.get("password")
        self.google_email = config.get("google_email")
        self.google_password = config.get("google_password")
        self.keyword = config.get("keyword")
        self.location = config.get("location")

        # Chrome setup
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 40)

    # ------------------------ LOGIN ------------------------
    def login(self):
        print("Opening Indeed login page...")
        self.driver.get(
            "https://secure.indeed.com/auth?hl=en_US&service=my&co=US&continue=https%3A%2F%2Fwww.indeed.com%2F"
        )
        time.sleep(3)

        # Email entry
        email_input = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "__email"))
        )
        email_input.clear()
        email_input.send_keys(self.email)
        print("Entered email.")
        time.sleep(1)

        # Handle optional "Verify you're human" checkbox
        self.handle_turnstile_checkbox()

        # Continue after email
        continue_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-tn-element='auth-page-email-submit-button']")
            )
        )
        self.driver.execute_script("arguments[0].click();", continue_button)
        print("Clicked 'Continue' after email.")
        time.sleep(3)

        # Continue with Google
        google_button = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[@id='gsuite-login-google-button' and .//span[normalize-space()='Continue with Google']]",
                )
            )
        )
        self.driver.execute_script("arguments[0].click();", google_button)
        print("Clicked 'Continue with Google'.")
        time.sleep(3)

        # Handle Google login popup
        print("Switching to Google login popup...")
        main_window = self.driver.current_window_handle
        WebDriverWait(self.driver, 20).until(lambda d: len(d.window_handles) > 1)
        new_window = [w for w in self.driver.window_handles if w != main_window][0]
        self.driver.switch_to.window(new_window)
        print("Switched to Google login window.")

        # Google email
        email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "identifierId")))
        email_field.clear()
        email_field.send_keys(self.google_email)
        self.driver.find_element(By.XPATH, "//span[text()='Next']").click()
        print("Entered Google email.")
        time.sleep(3)

        # Google password
        password_field = self.wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))
        password_field.clear()
        password_field.send_keys(self.google_password)
        self.driver.find_element(By.ID, "passwordNext").click()
        print("Entered Google password.")
        time.sleep(8)

        # Switch back to Indeed
        self.driver.switch_to.window(main_window)
        print("Switched back to Indeed after login.")
        print("✅ Login completed successfully.")

    # ------------------------ HANDLE CAPTCHA ------------------------
    def handle_turnstile_checkbox(self):
        """Handles Cloudflare Turnstile checkbox if present."""
        try:
            print("Checking for Turnstile verification checkbox...")
            # Try switching to Turnstile iframe
            try:
                iframe = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "iframe[src*='turnstile']")
                    )
                )
                self.driver.switch_to.frame(iframe)
                print("🪟 Switched to Turnstile iframe.")
            except TimeoutException:
                print("⚠️ No Turnstile iframe found — continuing in main context.")

            # Wait for and click checkbox
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkbox)
            time.sleep(0.5)
            checkbox.click()
            time.sleep(1)

            if checkbox.is_selected():
                print("✅ Checkbox clicked successfully!")
            else:
                print("ℹ️ Checkbox clicked but not visibly selected — handled asynchronously.")

        except Exception as e:
            print(f"❌ Checkbox handling error: {e}")
        finally:
            self.driver.switch_to.default_content()

    # ------------------------ JOB SEARCH ------------------------
    def search_jobs(self):
        print("🔍 Navigating to Indeed home page...")
        #self.driver.get("https://www.indeed.com/")
        time.sleep(5)

        try:
            # Wait until the search input fields are visible
            what_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "text-input-what"))
            )
            where_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "text-input-where"))
            )
        except TimeoutException:
            print("⚠️ Default search fields not found — trying alternative selectors...")
            try:
                what_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@aria-label='What']"))
                )
                where_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Where']"))
                )
            except TimeoutException:
                print("❌ Could not locate search fields on Indeed home.")
                self.driver.save_screenshot("search_page_error.png")
                return

        # Fill out the job search form
        what_input.clear()
        what_input.send_keys(self.keyword)
        print(f"🧑‍💻 Entered keyword: {self.keyword}")

        where_input.clear()
        where_input.send_keys(self.location)
        print(f"📍 Entered location: {self.location}")

        # Click the 'Find jobs' button
        try:
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Find jobs']]"))
            )
            self.driver.execute_script("arguments[0].click();", search_button)
            print("✅ Job search initiated successfully.")
        except TimeoutException:
            print("⚠️ Could not click 'Find jobs' button — trying ENTER key fallback...")
            where_input.send_keys(Keys.RETURN)

        time.sleep(5)

    # ------------------------ APPLY TO A SINGLE JOB ------------------------
    def click_apply_button(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1 | //div[@id='jobDescriptionText']")))
            time.sleep(2)

            apply_buttons = self.driver.find_elements(
                By.XPATH, "//span[contains(@class, 'jobsearch-IndeedApplyButton') and text()='Apply now']"
            )

            if not apply_buttons:
                print(" 'Apply now' button not found — skipping.")
                return

            button = apply_buttons[0]
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(2)
            button.click()
            print(" 'Apply now' clicked successfully.")
            time.sleep(3)

            # Resume upload / selection
            try:
                resume_button = self.wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//span[@data-testid='document-card-header-subtitle' and contains(text(), 'Uploaded')]/ancestor::span[contains(@class,'mosaic-provider-module-apply-resume-selection')]//span[@data-testid='resume-selection-file-resume-radio-card-indicator']",
                        )
                    )
                )
                resume_button.click()
                print("📄 Resume selected.")
                time.sleep(2)
            except TimeoutException:
                print("⚠️ Resume selection step not found — skipping.")

            # Continue
            try:
                continue_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Continue']]"))
                )
                continue_button.click()
                print("➡️ Clicked Continue.")
                time.sleep(2)
            except TimeoutException:
                pass

            # Submit
            try:
                submit_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Submit your application']]"))
                )
                submit_button.click()
                print("🎉 Application submitted successfully!")
                time.sleep(2)
            except TimeoutException:
                print("⚠️ Submit button not found — possibly manual step required.")

        except Exception as e:
            print(f"❌ Error clicking apply button: {e}")

    # ------------------------ APPLY TO ALL JOBS ------------------------
    def apply_to_jobs(self):
        applied_links = set()
        original_tab = self.driver.current_window_handle
        page_number = 1

        while True:
            print(f"\n📄 Processing Page {page_number}...")

            try:
                job_cards = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'jcs-JobTitle')]"))
                )
            except TimeoutException:
                print("❌ No jobs found. Exiting.")
                break

            links = list({card.get_attribute("href") for card in job_cards if card.get_attribute("href")})
            print(f"🔗 Found {len(links)} job listings.")

            for idx, link in enumerate(links, start=1):
                if not link or link in applied_links:
                    continue
                applied_links.add(link)
                print(f"\n➡️ Opening job {idx}/{len(links)}: {link}")

                try:
                    self.driver.execute_script(f"window.open('{link}', '_blank');")
                    WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(3)
                    self.click_apply_button()
                except Exception as e:
                    print(f"⚠️ Error applying to job: {e}")
                finally:
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                    self.driver.switch_to.window(original_tab)
                time.sleep(random.uniform(3, 6))

            # Pagination
            try:
                next_button = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-testid='pagination-page-next']"))
                )

                if not next_button.get_attribute("href"):
                    print("✅ Last page reached.")
                    break

                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_button)
                time.sleep(1)
                next_button.click()
                page_number += 1
                print(f"➡️ Moving to next page: {page_number}")
                time.sleep(random.uniform(5, 8))
            except TimeoutException:
                print("✅ No more pages.")
                break
            except Exception as e:
                print(f"⚠️ Pagination error: {e}")
                break

    # ------------------------ RUN BOT ------------------------
    def run(self):
        self.login()
        self.search_jobs()
        self.apply_to_jobs()
        print("✅ Automation complete.")


# ------------------------ MAIN ------------------------
if __name__ == "__main__":
    bot = IndeedAutoApply("config.json")
    bot.run()
