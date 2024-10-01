import time
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

CLICK_WAIT = 0.5

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
        time.sleep(CLICK_WAIT)
    except NoSuchElementException:
        print('No house hearing for {} can be found.'.format(congressNum))
        return None
    
    committees_xpath = '//div[contains(@data-browsepath, \'{}\')]'.format('/'.join([congressNum, type, '']))
    committees = driver.find_elements(By.XPATH, committees_xpath)
    while len(committees) == 0:
        time.sleep(CLICK_WAIT)
        committees = driver.find_elements(By.XPATH, committees_xpath)

    for committee in committees:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", committee)

        committee_label = committee.find_element(By.TAG_NAME, 'span').text
        committee_dict = {'committee': committee_label, 'hearings': []};

        print(committee_label)

        committee.click()
        time.sleep(CLICK_WAIT)

        # HEARINGS
        committee_xpath = '//div[contains(@data-browsepath, \"{}\")]'.format('/'.join([congressNum, type, committee_label]))
        expanded_hearings_section = driver.find_element(By.XPATH, committee_xpath + '/following-sibling::div')

        hearings = expanded_hearings_section.find_elements(By.TAG_NAME, 'table')
        while len(hearings) == 0:
            time.sleep(CLICK_WAIT)
            hearings = expanded_hearings_section.find_elements(By.TAG_NAME, 'table')
        
        print(f'{len(hearings)} hearings found.')

        for hearing in hearings:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", hearing)
            # hearing_cnt += 1
            hearing_tds = hearing.find_elements(By.TAG_NAME, 'td')

            hearing_infos = hearing_tds[0].find_elements(By.TAG_NAME, 'span')
            hearing_title_with_serial = hearing_infos[0].text
            hearing_metadata = hearing_infos[1].text

            # Not getting title with serial excluded because different committees have this text in different formats.
            # hearing_title = hearing_title_with_serial.split(' - ')[1] if ' - ' in hearing_title_with_serial else None

            # if len(hearing_title_with_serial.split(' ')) < 3:
            #     print(f"{hearing_title_with_serial}, cannot locate serial number")
            # hearing_number = hearing_title_with_serial.split(' ')[2]

            hearing_date = hearing_metadata.split('. ')[1]

            date_format = "%A, %B %d, %Y."
            parsed_date = datetime.strptime(hearing_date, date_format)
            parsed_date = parsed_date.strftime('%Y-%m-%d')

            hearing_txt_link = hearing_tds[1].find_element(By.XPATH, './/a[text()=\' Text\']').get_attribute('href')
            hearing_details_link = hearing_tds[1].find_element(By.XPATH, './/a[text()=\' Details\']').get_attribute('href')
            govinfo_id = hearing_details_link.split('/')[-1]

            hearing_dict = {'title': hearing_title_with_serial, 'govinfo_id': govinfo_id, 'date': parsed_date, 'transcript': hearing_txt_link, 'details': hearing_details_link}
            committee_dict['hearings'].append(hearing_dict)

            # if not hearing_title:
            #     print(f"{hearing_title_with_serial} on {parsed_date} has no title, please manually fill")
            #     continue
            # if len(hearing_title) < 10:
            #     print(f"{hearing_title_with_serial}, title is likely wrong, please update")
            
            # with open(metadata_file, mode='a', newline='') as file:
            #     writer = csv.writer(file)
            #     writer.writerow([hearing_number, parsed_date, hearing_title.strip('"')])

        committee_list.append(committee_dict)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", committee)
        committee.click()
        time.sleep(CLICK_WAIT)

    return committee_list

if __name__ == "__main__":
    metadata = []
    metadata_file = 'hearing_metadata.json'

    with open(metadata_file, 'r') as json_file:
        metadata = json.load(json_file)

    driver = setup_driver()
    driver.get('https://www.govinfo.gov/app/collection/chrg')

    time.sleep(2)

    congress_years = driver.find_elements(By.XPATH, '//div[contains(@class, "panel-heading")]')
    for congress_year in congress_years:
        congress_label = congress_year.find_element(By.TAG_NAME, 'span').text
        congressNum = congress_year.get_attribute('data-browsepath')
        congress_year_dict = {'congress_year': congress_label, 'serial_no': congressNum, 'house': [], 'senate': [], 'joint': []}

        print(congressNum)

        if congressNum > '104':
            continue
        
        if congressNum < '103':
            break
        
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", congress_year)
        congress_year.click()
        time.sleep(CLICK_WAIT)
        
        print('HOUSE')
        house_hearing_list = getHearingDict('HOUSE', driver, congressNum)
        congress_year_dict['house'] = house_hearing_list

        print('JOINT')
        joint_hearing_list = getHearingDict('JOINT', driver, congressNum)
        congress_year_dict['joint'] = joint_hearing_list

        print('SENATE')
        senate_hearing_list = getHearingDict('SENATE', driver, congressNum)
        congress_year_dict['senate'] = senate_hearing_list

        metadata.append(congress_year_dict)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", congress_year)
        congress_year.click()
        time.sleep(CLICK_WAIT)

        with open(metadata_file, 'w') as json_file:
            json.dump(metadata, json_file, indent=4)

    time.sleep(2)
    driver.quit()