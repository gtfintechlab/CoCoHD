import json
import time
import concurrent.futures
import threading
import logging
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CLICK_WAIT = 5

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

lock = threading.Lock()
completed_count = 0

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_hearing_details(hearing_metadata, retries=3, delay=5):
    for attempt in range(retries):
        driver = setup_driver()
        hearing_details = {'govinfo_id': hearing_metadata['govinfo_id']}
        url = hearing_metadata['details']
        try:
            driver.get(url)
            # time.sleep(CLICK_WAIT)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//h4[@class='contentdetails-title']")))
            hearing_title = driver.find_element(By.XPATH, "//h4[@class='contentdetails-title']").text
            hearing_details['Title'] = hearing_title

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@id='accMetadata']")))
            metadata_panel_xpath = "//div[@id='accMetadata']"
            metadata_panel = driver.find_element(By.XPATH, metadata_panel_xpath)

            rows = metadata_panel.find_elements(By.XPATH, ".//div[@class='row']")
            for i, r in enumerate(rows):
                if i == 0: continue
                divs = r.find_elements(By.TAG_NAME, 'div')
                hearing_details[divs[0].text] = divs[1].text

            logging.info(f"Successfully scraped {url}")
            return hearing_details
        except Exception as e:
            logging.error(f"Error scraping {url} on attempt {attempt + 1}: {e}")
            time.sleep(delay)
        finally:
            driver.quit()
    logging.error(f"Failed to scrape {url} after {retries} attempts")
    return None

def write_data(output_file, data):
    with lock:
        with open(output_file, 'a') as f:
            json.dump(data, f, indent=4)
            f.write(',\n')

def add_hearing_details_for_year_type(type, congress_year):
    serial_no = congress_year['serial_no']
    output_file = f'./details/{serial_no}_{type}.json'

    with open(output_file, 'w') as f:
        f.write('[\n')

    def task(hearing):
        global completed_count
        hearing_details = get_hearing_details(hearing)
        if not hearing_details: return
        write_data(output_file, hearing_details)
        with lock:
            completed_count += 1
            logging.info(f"Progress: {completed_count}")

    if congress_year[type]:
        for committee in congress_year[type]:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(task, committee['hearings'])

    # Write the closing bracket of the JSON array
    with open(output_file, 'a') as f:
        f.seek(f.tell() - 2, 0)  # Move back to overwrite the last comma
        f.truncate()             # Remove the last comma and newline
        f.write('\n]')           # Close the JSON array

if __name__ == "__main__":
    metadata_file = 'metadata.json'
    with open(metadata_file, 'r') as json_file:
        metadata = json.load(json_file)

    for congress_year in metadata:
        if congress_year['serial_no'] > '114': continue
        # if congress_year['serial_no'] == '114': break
        
        add_hearing_details_for_year_type('house', congress_year)
        add_hearing_details_for_year_type('senate', congress_year)
        add_hearing_details_for_year_type('joint', congress_year)