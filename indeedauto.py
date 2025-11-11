import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time


class IndeedAutoApply:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            config = json.load(f)

        self.email = config.get("email")
        self.password = config.get("password")
        self.google_email = config.get("google_email")
        self.google_password = config.get("google_password")
        self.keyword = config.get("keyword")
        self.location = config.get("location")

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 40)

#login
    def login(self):
        print("Opening Indeed login page...")

        self.driver.get(" https://secure.indeed.com/auth;jsessionid=node01nc78aozmzd4tcx54ofnkjvqa996001.node0?hl=en_US&service=my&co=US&continue=https%3A%2F%2Fwww.indeed.com%2F  ")
        time.sleep(2)

        email_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "__email")))
        email_input.clear()
        email_input.send_keys(self.email)
        time.sleep(1)

        checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        if checkboxes:
            checkbox = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']")))
            self.driver.execute_script("arguments[0].click();", checkbox)
            print("Checkbox clicked.")
        else:
            print("No standard checkbox found — skipping.")
        time.sleep(3)

        continue_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tn-element='auth-page-email-submit-button' and not(contains(., 'Google'))]")))
        self.driver.execute_script("arguments[0].click();", continue_button)
        print("Email Continue button clicked.")
        time.sleep(3)

        '''try:
            continue_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tn-element='auth-page-email-submit-button' and not(contains(., 'Google'))]")))
            self.driver.execute_script("arguments[0].click();", continue_button)
            print("Email Continue button clicked.")
            time.sleep(3)
        except TimeoutException:
            print("Continue button not found. Skipping...")'''

        google_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='gsuite-login-google-button' and .//span[normalize-space()='Continue with Google']]")))
        self.driver.execute_script("arguments[0].click();", google_button)
        print(" 'Continue with Google' button clicked.")
        time.sleep(3)

        print(" Switching to Google login popup...")
        main_window = self.driver.current_window_handle
        WebDriverWait(self.driver, 20).until(lambda d: len(d.window_handles) > 1)
        new_window = [w for w in self.driver.window_handles if w != main_window][0]
        self.driver.switch_to.window(new_window)
        print("Switched to Google login popup.")

        self.driver.maximize_window()
        time.sleep(2)
        
        # Step 6: Google login - email
        email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "identifierId")))
        email_field.clear()
        email_field.send_keys(self.google_email)
        self.driver.find_element(By.XPATH, "//span[@jsname='V67aGc' and text()='Next']").click()
        print("Google email entered.")
        time.sleep(3)

        # Google login - password
        password_field = self.wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))
        password_field.clear()
        password_field.send_keys(self.google_password)
        self.driver.find_element(By.XPATH, "//div[@id='passwordNext']").click()
        print("Google password entered and submitted.")
        time.sleep(10)


        # SSwitch back to Indeed window
        #self.driver.switch_to.window(main_window)
        #print("Switched back to Indeed after login.")
        #print("Login flow completed successfully.")


        #home
        home_button = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "FindJobs")))
        #home_button = self.wait.until(EC.presence_of_element_located((By.ID, "FindJobs")))
        home_button.click()
        time.sleep(5)


    def search_jobs(self):

        what_input = self.wait.until(EC.presence_of_element_located((By.ID, "text-input-what")))
        what_input.clear()
        what_input.send_keys(self.keyword)

        where_input = self.wait.until(EC.presence_of_element_located((By.ID, "text-input-where")))
        where_input.clear()
        where_input.send_keys(self.location)

        search_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Find jobs']]")))
        self.driver.execute_script("arguments[0].click();", search_button)
        print("Job search completed")
        time.sleep(5)


    def click_apply_button(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1 | //div[@id='jobDescriptionText']")))
            time.sleep(2)

            apply_button = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'jobsearch-IndeedApplyButton-newDesign') and text()='Apply now']")
            time.sleep(10)

            if not apply_button:
                print("'Apply now' button not found — skipping.")
                return

            button = apply_button[0]
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(10)
            self.driver.execute_script("arguments[0].click();", button)
            print(" 'Apply now' clicked successfully.")
            time.sleep(3)

        
        #resume
            resume_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@data-testid='document-card-header-subtitle' and contains(text(), 'Uploaded today')]/ancestor::span[contains(@class, 'mosaic-provider-module-apply-resume-selection-vbfzk2')]//span[@data-testid='resume-selection-file-resume-radio-card-indicator']")))
            resume_button.click()
            time.sleep(2)


        #continue button
            first_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Continue']]")))
            first_button.click()
            time.sleep(2)


        #submit button
            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Submit your application']]")))
            submit_button.click()
            print("Application submitted successfully")
   
        except Exception as e:
            print(f" Error clicking apply button: {e}")
            return False
        


        
    def apply_to_jobs(self):
        applied_links = set()
        original_tab = self.driver.current_window_handle
        page_number = 1

        while True:
            print(f"\n📄 Processing Page {page_number}...")

            try:
                job_cards = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'jcs-JobTitle')]")))
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
                    # Open in new tab
                    self.driver.execute_script(f"window.open('{link}', '_blank');")
                    WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(3)

                    # Try applying
                    self.click_apply_button()

                except Exception as e:
                    print(f"⚠️ Error applying to job: {e}")

                finally:
                    # Close tab and return to main
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                    self.driver.switch_to.window(original_tab)

                time.sleep(random.uniform(3, 6))

            # Pagination
            try:
                next_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-testid='pagination-page-next']")))

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

    def run(self):
        self.login()
        self.search_jobs()
        self.apply_to_jobs()

        print("automation complete")

if __name__ == "__main__":
    bot = IndeedAutoApply("config.json")
    bot.run()
