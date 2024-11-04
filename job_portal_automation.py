nimport tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from job_scraper import scrape_jobs_indeed, scrape_jobs_linkedin, init_driver
import time

# Create a simple popup using tkinter to get user's choice
def show_popup(job_title, job_company):
    # Create a new window
    window = tk.Tk()
    window.withdraw()  # Hide the root window

    # Ask the user if they want to apply for the job
    response = messagebox.askquestion(f"Job Found: {job_title}", 
                                      f"Would you like to apply to {job_title} at {job_company}?",
                                      icon='info')

    window.destroy()  # Close the window after the response
    return response

# Apply for a job automatically using Selenium
def apply_for_job(driver, job, resume_path, update_resume=False):
    driver.get(job['link'])
    time.sleep(3)

    try:
        upload_button = driver.find_element('xpath', '//input[@type="file"]')
        if update_resume:
            print("Updating resume...")
        upload_button.send_keys(resume_path)  # Upload your resume

        submit_button = driver.find_element('xpath', '//button[@type="submit"]')
        submit_button.click()

        print(f"Successfully applied for {job['title']} at {job['company']}")

    except Exception as e:
        print(f"Could not apply for {job['title']}. Error: {e}")

# Let the user choose a resume version from predefined options
def choose_resume():
    resumes = ["resume_v1.pdf", "resume_v2.pdf", "resume_v3.pdf"]  # Your predefined resume versions
    print("Choose a resume to upload:")
    for i, resume in enumerate(resumes):
        print(f"{i + 1}. {resume}")
    choice = int(input("Enter the number of the resume you want to upload: "))
    return resumes[choice - 1]

# Main function to run the automation
def main():
    # Ask the user for job details
    job_title = input("Enter the job title: ")
    location = input("Enter the job location: ")
    platform = input("Which platform? (Indeed/LinkedIn): ").lower()

    # Initialize Selenium WebDriver
    driver = init_driver()

    # Ask the user for their skills to filter job postings
    skills = ['Python', 'Automation', 'Web Development']  # Add your relevant skills here

    # Scrape jobs based on the platform
    if platform == 'indeed':
        jobs = scrape_jobs_indeed(driver, job_title, location, skills)
    elif platform == 'linkedin':
        jobs = scrape_jobs_linkedin(driver, job_title, location, skills)
    else:
        print("Unsupported platform!")
        driver.quit()
        return

    # Let the user choose a resume version for uploading
    resume_path = choose_resume()

    # Iterate through the jobs and notify the user for each
    for job in jobs:
        response = show_popup(job['title'], job['company'])

        if response == 'yes':  # User chose to apply
            apply_for_job(driver, job, resume_path)
        elif response == 'update':  # If user wants to update resume and apply
            new_resume = choose_resume()
            apply_for_job(driver, job, new_resume, update_resume=True)
        else:
            print(f"Skipped {job['title']} at {job['company']}")

    # Quit the driver after applying to all jobs
    driver.quit()

if __name__ == "__main__":
    main()
