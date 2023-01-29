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
def get_snps_and_go_result(mutation_data):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://snps-and-go.biocomp.unibo.it/snps-and-go/')
    wait = WebDriverWait(driver, 120)
    driver.find_element(By.CSS_SELECTOR, 'input[name="uniprot"]').send_keys(mutation_data["uniprot_id"])
    driver.find_element(By.CSS_SELECTOR, 'input[name="position"]').send_keys(mutation_data["location"])
    driver.find_element(By.CSS_SELECTOR, 'input[name="wild-type"]').send_keys(mutation_data["wild_type"])
    driver.find_element(By.CSS_SELECTOR, 'input[name="substituting"]').send_keys(mutation_data["mutant"])
    driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

    print_options = PrintOptions()
    base64code = driver.print_page(print_options)
    bytes = b64decode(base64code, validate=True)
    uniprot_id = mutation_data['uniprot_id']
    location = mutation_data['location']
    wild_type = mutation_data['wild_type']
    mutant = mutation_data['mutant']
    filename = f'{uniprot_id}_{wild_type}{location}{mutant}'
    HOME_DIR = os.path.expanduser('~')
    file_dir = os.path.join(HOME_DIR, 'SNP Results\\SNPs&Go Analyses')
    try:
        os.makedirs(file_dir)
    except OSError as er:
        pass
    with open(os.path.join(file_dir, f'{filename}.pdf'), 'wb') as file:
        file.write(bytes)
    driver.quit()


if __name__ == '__main__':
    get_snps_and_go_result({'uniprot_id': 'Q8NBP7', 'location': '53', 'wild_type': 'A', 'mutant': 'V'})
