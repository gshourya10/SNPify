import os
import time
from base64 import b64decode

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from base.utils.helpers import log_error

chrome_options = Options()
chrome_options.add_argument("--headless")


@log_error
def get_hope_result(mutation_data):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://www3.cmbi.umcn.nl/hope/input/')
    wait = WebDriverWait(driver, 120)
    driver.find_element(By.CSS_SELECTOR, 'button[onclick="setDisclaimer(); $(\'#disclaimer\').hide();"]').click()
    driver.find_element(By.ID, 'sequence').send_keys(mutation_data['uniprot_id'])
    driver.find_element(By.ID, 'seq_next_btn').click()
    wild_type = f'{mutation_data["wild_type"]}{mutation_data["location"]}'
    wait.until(EC.visibility_of(driver.find_element(By.ID, wild_type)))
    driver.find_element(By.ID, wild_type).click()
    driver.find_element(By.ID, 'wildtype_next_btn').click()
    wait.until(EC.visibility_of(driver.find_element(By.ID, mutation_data['mutant'])))
    driver.find_element(By.ID, mutation_data['mutant']).click()
    driver.find_element(By.ID, 'mutation_next_btn').click()
    wait.until(EC.visibility_of(driver.find_element(By.ID, 'submit_btn')))
    driver.find_element(By.ID, 'submit_btn').click()
    wait.until(EC.visibility_of(driver.find_element(By.CSS_SELECTOR, '.btn.btn-primary.btn-sm.pull-right')))
    driver.find_element(By.CSS_SELECTOR, '.btn.btn-primary.btn-sm.pull-right').click()
    link = driver.current_url
    try:
        first_img = driver.find_element(By.CLASS_NAME, 'generated')
        driver.execute_script("arguments[0].scrollIntoView();", first_img)
        time.sleep(11)
    except NoSuchElementException:
        pass
    print_options = PrintOptions()
    base64code = driver.print_page(print_options)
    bytes = b64decode(base64code, validate=True)
    uniprot_id = mutation_data['uniprot_id']
    location = mutation_data['location']
    wild_type = mutation_data['wild_type']
    mutant = mutation_data['mutant']
    filename = f'{uniprot_id}_{wild_type}{location}{mutant}'
    HOME_DIR = os.path.expanduser('~')
    file_dir = os.path.join(HOME_DIR, 'SNP Results\\HOPE Analyses')
    try:
        os.makedirs(file_dir)
    except OSError as er:
        pass
    with open(os.path.join(file_dir, f'{filename}.pdf'), 'wb') as file:
        file.write(bytes)
    driver.quit()
    return link


if __name__ == '__main__':
    l = get_hope_result({'uniprot_id': 'P01542', 'location': '24', 'wild_type': 'A', 'mutant': 'V'})
    print(l)
