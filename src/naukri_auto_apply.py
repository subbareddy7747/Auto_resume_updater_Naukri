import os
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ---------------------------------------------
# CONFIGURATION
# ---------------------------------------------

FIRST_NAME = "Tetali ram"
LAST_NAME = "subba reddy"

KEYWORDS = ["data scientist", "machine learning engineer", "ml engineer", "ai engineer"]
LOCATION = "Hyderabad, Telangana, India"

MAX_DAILY_APPLY = 500

RESUME_FILE = "Tetali_Ram_Subba_Reddy_Lv_New_resume.pdf"  # Must be in same folder

APPLIED_COUNT = 0
FAILED_COUNT = 0

APPLIED_LINKS = {"passed": [], "failed": []}
JOB_LINKS = []

# ---------------------------------------------
# CHROME SETUP (non-headless to verify working)
# ---------------------------------------------

CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
CHROME_OPTIONS.add_argument("--no-sandbox")
CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")

DRIVER = webdriver.Chrome(options=CHROME_OPTIONS)
WAIT = WebDriverWait(DRIVER, 25)


def login_to_naukri(email: str, password: str) -> None:
    if not email or not password:
        raise SystemExit("❌ Set NAUKRI_EMAIL and NAUKRI_PASSWORD before running this script!")

    print("\n🔐 Logging in...")
    DRIVER.get("https://www.naukri.com/nlogin/login")
    print("Page title:", DRIVER.title)

    try:
        username_field = WAIT.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id,'username')]"))
        )
    except TimeoutException as exc:
        raise SystemExit("❌ Login page didn't load — try again without headless mode") from exc

    username_field.send_keys(email)
    DRIVER.find_element(By.XPATH, "//*[contains(@id,'password')]").send_keys(password)
    DRIVER.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()

    time.sleep(5)
    print("✔ Logged in!\n")


def upload_resume() -> None:
    print("📄 Uploading resume...")
    resume_path = os.path.abspath(RESUME_FILE)

    DRIVER.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(6)

    try:
        DRIVER.find_element(By.ID, "attachCV").send_keys(resume_path)
        print("✔ Resume uploaded!\n")
    except Exception:
        print("⚠ Resume upload skipped / already up-to-date\n")


def scrape_job_links() -> list[str]:
    print("🔎 Collecting job links...")

    job_links = set()

    city = LOCATION.split(",")[0].strip().lower().replace(" ", "-")
    city = city.replace("-", " ").strip().replace(" ", "-")

    for role in KEYWORDS:
        role_slug = role.lower().strip().replace(" ", "-")

        for page in range(1, 3):
            url = f"https://www.naukri.com/{role_slug}-jobs-in-{city}-{page}"
            DRIVER.get(url)

            try:
                WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.title")))
            except TimeoutException:
                print(f"⚠ No jobs loaded / blocked for: {url}")
                continue

            DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)

            soup = BeautifulSoup(DRIVER.page_source, "html.parser")

            for anchor in soup.select("a.title"):
                href = anchor.get("href")
                if href and href.startswith("http"):
                    job_links.add(href)

    job_links_list = list(job_links)
    print(f"📌 Total jobs found: {len(job_links_list)}\n")
    return job_links_list


def apply_to_jobs(job_links: list[str]) -> None:
    global APPLIED_COUNT, FAILED_COUNT

    print("🚀 Starting auto-apply...\n")

    for link in job_links:
        if APPLIED_COUNT >= MAX_DAILY_APPLY:
            print("\n⛔ Daily quota reached — stopping")
            break

        DRIVER.get(link)
        time.sleep(3)

        try:
            apply_btn = WAIT.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Apply')]"))
            )
            apply_btn.click()
            time.sleep(2)

            APPLIED_COUNT += 1
            APPLIED_LINKS["passed"].append(link)
            print(f"✔ Applied: {link} (Total: {APPLIED_COUNT})")

        except Exception as exc:
            FAILED_COUNT += 1
            APPLIED_LINKS["failed"].append(link)
            print(f"❌ Failed: {link} | {exc}")


def save_report() -> None:
    print("\n💾 Saving results to CSV...")
    df = pd.DataFrame({k: pd.Series(v) for k, v in APPLIED_LINKS.items()})
    df.to_csv("naukri_autoapply_results.csv", index=False)


def main() -> None:
    email = os.getenv("NAUKRI_EMAIL")
    password = os.getenv("NAUKRI_PASSWORD")

    login_to_naukri(email, password)
    upload_resume()

    job_links = scrape_job_links()
    apply_to_jobs(job_links)
    save_report()

    DRIVER.quit()

    print(
        f"""
🎯 COMPLETED
-------------------------------------
Applied successfully : {APPLIED_COUNT}
Failed               : {FAILED_COUNT}
CSV saved as         : naukri_autoapply_results.csv
-------------------------------------
"""
    )


if __name__ == "__main__":
    main()
