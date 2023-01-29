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

UNIPROT_URL = 'https://rest.uniprot.org/uniprotkb/'


@log_error
def get_polyphen_results(mutation_data):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('http://genetics.bwh.harvard.edu/pph2/')
    wait = WebDriverWait(driver, 120)
    fasta_sequence = requests.get(url=UNIPROT_URL + f"{mutation_data['uniprot_id']}.fasta")
    if fasta_sequence.text.find("invalid") != -1:
        return
    driver.find_element(By.CSS_SELECTOR, 'textarea[name="seqres"]').send_keys(fasta_sequence.text)
    driver.find_element(By.CSS_SELECTOR, 'input[name="seqpos"]').send_keys(mutation_data["location"])
    driver.find_element(By.ID, f'v1{mutation_data["wild_type"]}').click()
    driver.find_element(By.ID, f'v2{mutation_data["mutant"]}').click()
    driver.find_element(By.CSS_SELECTOR, 'input[name="description"]') \
        .send_keys(
        f"{mutation_data['uniprot_id']}_{mutation_data['wild_type']}{mutation_data['location']}{mutation_data['mutant']}"
    )

    driver.find_element(By.CSS_SELECTOR, 'input[name="Submit"]').click()
    start = datetime.datetime.now()
    completed = False
    while datetime.datetime.now() - start <= datetime.timedelta(seconds=120):
        if driver.find_elements(By.LINK_TEXT, "View"):
            completed = True
            break
        driver.find_element(By.CSS_SELECTOR, 'input[value="Refresh"]').click()
        time.sleep(3)

    if not completed:
        return

    view_button = driver.find_element(By.LINK_TEXT, "View")
    driver.execute_script("arguments[0].setAttribute('value',arguments[1])", view_button, "")

    result_link = view_button.get_attribute('href')

    file_type = result_link[result_link.rfind('.') + 1:]

    if file_type == 'log':
        return
    driver.get(result_link)
    link = driver.current_url

    for div in driver.find_elements(By.TAG_NAME, 'div'):
        driver.execute_script("arguments[0].style.display = 'block'", div)

    driver.execute_script("""
        div = document.querySelector('#msaBlock');
        div.style.maxHeight = '100%';
    """)

    print_options = PrintOptions()
    base64code = driver.print_page(print_options)
    bytes = b64decode(base64code, validate=True)
    uniprot_id = mutation_data['uniprot_id']
    location = mutation_data['location']
    wild_type = mutation_data['wild_type']
    mutant = mutation_data['mutant']
    filename = f'{uniprot_id}_{wild_type}{location}{mutant}'
    HOME_DIR = os.path.expanduser('~')
    file_dir = os.path.join(HOME_DIR, 'SNP Results\\PolyPhen-2 Analyses')
    try:
        os.makedirs(file_dir)
    except OSError as er:
        pass
    with open(os.path.join(file_dir, f'{filename}.pdf'), 'wb') as file:
        file.write(bytes)
    driver.quit()
    return link


if __name__ == '__main__':
    get_polyphen_results({'uniprot_id': 'P01542', 'location': '24', 'wild_type': 'A', 'mutant': 'V'})
