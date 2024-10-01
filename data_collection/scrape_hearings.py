import time
from datetime import datetime
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

CLICK_WAIT_TIME = 0.5

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def getHearingDict(type, driver, congressNum):
    # type should be HOUSE | SENATE | JOINT
    committee_list = []

    try:
        panel_xpath = '//div[@data-browsepath=\'{}\']'.format('/'.join([congressNum, type]))
        panel = driver.find_element(By.XPATH, panel_xpath)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", panel)
        panel.click()
        time.sleep(CLICK_WAIT_TIME)
    except NoSuchElementException:
        print('No house hearing for {} can be found.'.format(congressNum))
        return None
    
    committees_xpath = '//div[contains(@data-browsepath, \'{}\')]'.format('/'.join([congressNum, type, '']))
    committees = driver.find_elements(By.XPATH, committees_xpath)
    # Wait until elements appear
    while len(committees) == 0:
        time.sleep(CLICK_WAIT_TIME)
        committees = driver.find_elements(By.XPATH, committees_xpath)

    for committee in committees:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", committee)

        committee_label = committee.find_element(By.TAG_NAME, 'span').text
        committee_dict = {'committee': committee_label, 'hearings': []};

        committee.click()
        time.sleep(CLICK_WAIT_TIME)

        # HEARINGS
        committee_xpath = '//div[contains(@data-browsepath, \"{}\")]'.format('/'.join([congressNum, type, committee_label]))
        expanded_hearings_section = driver.find_element(By.XPATH, committee_xpath + '/following-sibling::div')

        hearings = expanded_hearings_section.find_elements(By.TAG_NAME, 'table')
        while len(hearings) == 0:
            time.sleep(CLICK_WAIT_TIME)
            hearings = expanded_hearings_section.find_elements(By.TAG_NAME, 'table')
        
        print(f'{congressNum}th Congress, {type}, {committee_label}, {len(hearings)} hearings found.')

        for hearing in hearings:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", hearing)
            # hearing_cnt += 1
            hearing_tds = hearing.find_elements(By.TAG_NAME, 'td')

            hearing_infos = hearing_tds[0].find_elements(By.TAG_NAME, 'span')
            hearing_title_with_serial = hearing_infos[0].text
            hearing_metadata = hearing_infos[1].text

            hearing_date = hearing_metadata.split('. ')[1]

            date_format = "%A, %B %d, %Y."
            parsed_date = datetime.strptime(hearing_date, date_format)
            parsed_date = parsed_date.strftime('%Y-%m-%d')

            hearing_txt_link = hearing_tds[1].find_element(By.XPATH, './/a[text()=\' Text\']').get_attribute('href')
            hearing_details_link = hearing_tds[1].find_element(By.XPATH, './/a[text()=\' Details\']').get_attribute('href')
            govinfo_id = hearing_details_link.split('/')[-1]

            hearing_dict = {'title': hearing_title_with_serial, 'govinfo_id': govinfo_id, 'date': parsed_date, 'transcript': hearing_txt_link, 'details': hearing_details_link}
            committee_dict['hearings'].append(hearing_dict)

        committee_list.append(committee_dict)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", committee)
        committee.click()
        time.sleep(CLICK_WAIT_TIME)

    return committee_list

if __name__ == "__main__":
    metadata_file = '../data/hearing_data/hearing_metadata.json'

    # We check if there is an existing metadata file, and continue writing to it if there is one. 
    # TODO: update the writing mechanism to write new hearings to existing metadata file instead of appending an entire year
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as json_file:
            metadata = json.load(json_file)
    else:
        metadata = []

    driver = setup_driver()
    driver.get('https://www.govinfo.gov/app/collection/chrg')

    time.sleep(2)

    congress_years = driver.find_elements(By.XPATH, '//div[contains(@class, "panel-heading")]')
    for congress_year in congress_years:
        congress_label = congress_year.find_element(By.TAG_NAME, 'span').text
        congressNum = congress_year.get_attribute('data-browsepath')
        congress_year_dict = {'congress_year': congress_label, 'serial_no': congressNum, 'house': [], 'senate': [], 'joint': []}

        # We only collect hearings after the 105th congress due to limited txt data prior to that. 
        if congressNum < '118':
            break

        print(f'--------------------------- {congressNum} ---------------------------')
        
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", congress_year)
        congress_year.click()
        time.sleep(CLICK_WAIT_TIME)
        
        print('-------------------------- HOUSE --------------------------')
        house_hearing_list = getHearingDict('HOUSE', driver, congressNum)
        congress_year_dict['house'] = house_hearing_list

        print('-------------------------- JOINT --------------------------')
        joint_hearing_list = getHearingDict('JOINT', driver, congressNum)
        congress_year_dict['joint'] = joint_hearing_list

        print('-------------------------- SENATE --------------------------')
        senate_hearing_list = getHearingDict('SENATE', driver, congressNum)
        congress_year_dict['senate'] = senate_hearing_list

        metadata.append(congress_year_dict)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", congress_year)
        congress_year.click()
        time.sleep(CLICK_WAIT_TIME)

        with open(metadata_file, 'w') as json_file:
            json.dump(metadata, json_file, indent=4)

    time.sleep(2)
    driver.quit()