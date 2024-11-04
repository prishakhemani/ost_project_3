import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Initialize Selenium WebDriver
def init_driver():
    service = Service('./chromedriver.exe')  # Ensure this path points to your downloaded ChromeDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Scrape jobs from Indeed
def scrape_jobs_indeed(driver, job_title, location):
    # Encode job title and location for the URL
    job_title = urllib.parse.quote_plus(job_title)
    location = urllib.parse.quote_plus(location)

    # Construct the Indeed URL
    url = f"https://www.indeed.com/jobs?q={job_title}&l={location}"
    print(f"Scraping jobs from: {url}")
    
    driver.get(url)  # Navigate to Indeed
    time.sleep(3)  # Wait for the page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_cards = soup.find_all('div', class_='job_seen_beacon')

    jobs = []
    for card in job_cards:
        title = card.find('h2', class_='jobTitle').text.strip()
        company = card.find('span', class_='companyName').text.strip()
        job_location = card.find('div', class_='companyLocation').text.strip()
        link = "https://www.indeed.com" + card.find('a', href=True)['href']

        jobs.append({
            'title': title,
            'company': company,
            'location': job_location,
            'link': link
        })

    return jobs

# Scrape jobs from LinkedIn
def scrape_jobs_linkedin(driver, job_title, location, skills):
    # Encode job title and location for the URL
    job_title = urllib.parse.quote_plus(job_title)
    location = urllib.parse.quote_plus(location)

    # Construct the LinkedIn URL
    url = f"https://www.linkedin.com/jobs/search?keywords={job_title}&location={location}"
    print(f"Scraping jobs from: {url}")

    driver.get(url)  # Navigate to LinkedIn
    time.sleep(5)  # Wait for the page to load

    # Scroll to load more jobs (LinkedIn requires scrolling)
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Parse page content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_cards = soup.find_all('div', class_='result-card__contents')

    jobs = []
    for card in job_cards:
        title = card.find('h3', class_='result-card__title').text.strip()
        company = card.find('h4', class_='result-card__subtitle').text.strip()
        job_location = card.find('span', class_='job-result-card__location').text.strip()
        link = card.find('a', href=True)['href']

        # Check if any of the provided skills match the job description
        job_desc = card.find('p', class_='job-result-card__snippet').text.strip() if card.find('p', class_='job-result-card__snippet') else ""
        if any(skill.lower() in job_desc.lower() for skill in skills):
            jobs.append({
                'title': title,
                'company': company,
                'location': job_location,
                'link': link
            })

    return jobs

# Main function to start scraping
def scrape_jobs(job_title, location, platform='indeed', skills=None):
    driver = init_driver()

    if platform == 'indeed':
        jobs = scrape_jobs_indeed(driver, job_title, location)
    elif platform == 'linkedin':
        if skills is None:
            skills = []  # If no skills provided, use an empty list
        jobs = scrape_jobs_linkedin(driver, job_title, location, skills)
    else:
        jobs = []
        print(f"Unsupported platform: {platform}")

    driver.quit()
    return jobs

if __name__ == "__main__":
    job_title = "Software Engineer"
    location = "San Francisco"
    platform = input("Which platform? (Indeed/LinkedIn): ").lower()
    skills = ['Python', 'Automation', 'Web Development']  # List your skills here

    jobs = scrape_jobs(job_title, location, platform, skills)
    for job in jobs:
        print(job)
