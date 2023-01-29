import datetime
import time
import os
from base64 import b64decode
import requests

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
def get_mutation_taster_results(mutation_data):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://www.mutationtaster.org/')
    driver.find_element(By.CSS_SELECTOR, 'input[name="gene"]').send_keys(mutation_data["gene"])
    driver.find_element(By.CSS_SELECTOR, '#form > table > tbody > tr:nth-child(3) > td:nth-child(2) > small > a').click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, 'input[name="transcript_stable_id_text"]').send_keys(
        mutation_data["ensembl_id"])

    driver.find_element(By.CSS_SELECTOR, 'input[name="position_be"]').send_keys(
        mutation_data["location"])
    driver.find_element(By.CSS_SELECTOR, 'input[name="new_base"]').send_keys(
        mutation_data["base"])
    driver.find_element(By.CSS_SELECTOR, 'input[name="alteration_name"]').send_keys(
        f"{mutation_data['gene']}_{mutation_data['location']}{mutation_data['base']}")

    driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
    time.sleep(5)
    if not driver.find_elements(By.TAG_NAME, 'table'):
        return

    print_options = PrintOptions()
    base64code = driver.print_page(print_options)
    bytes = b64decode(base64code, validate=True)
    gene = mutation_data['gene']
    location = mutation_data['location']
    base = mutation_data['base']
    filename = f'{gene}_{location}{base}'
    HOME_DIR = os.path.expanduser('~')
    file_dir = os.path.join(HOME_DIR, 'SNP Results\\MutationTaster Analyses')
    try:
        os.makedirs(file_dir)
    except OSError as er:
        pass
    with open(os.path.join(file_dir, f'{filename}.pdf'), 'wb') as file:
        file.write(bytes)
    driver.quit()


if __name__ == '__main__':
    get_mutation_taster_results({"gene": "BRCA2", "ensembl_id": "ENST00000544455", "location": "20", "base": "G"})
