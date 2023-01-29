import io
import os
import requests
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from base.utils.helpers import log_error

from .utils import residue

chrome_options = Options()
chrome_options.add_argument("--headless")


@log_error
def get_missense_result(mutation_data):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("http://missense3d.bc.ic.ac.uk/~missense3d/")
    driver.implicitly_wait(2)
    proteinSeqChoice = driver.find_element(By.XPATH,
                                           "/html/body/div[1]/div/div[2]/div[1]/div/div/div/form/div/div[1]/label[1]/h3")
    proteinSeqChoice.click()

    nextButton = driver.find_element(By.XPATH,
                                     "/html/body/div[1]/div/div[2]/div[1]/div/div/div/form/div/div[1]/div/button")
    nextButton.click()

    driver.find_element(By.ID, "UNIPROT").send_keys(mutation_data['uniprot_id'])
    driver.find_element(By.ID, "PDBCODE").send_keys(mutation_data['pdb_code'])
    driver.find_element(By.ID, "PDBCHAIN").send_keys(mutation_data['pdb_chain'])
    driver.find_element(By.ID, "UNIRESIDUE").send_keys(mutation_data['location'])
    Select(driver.find_element(By.ID, "PDBRESNAME")).select_by_value(residue.amino_acid[mutation_data['wild_type']])
    Select(driver.find_element(By.ID, "PDBMUTATION")).select_by_value(residue.amino_acid[mutation_data['mutant']])
    submitButton = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]"
                                                 "/div[1]/div/div/div/form/div"
                                                 "/div[2]/div/div[5]/input")
    submitButton.click()
    wait = WebDriverWait(driver, 10)
    wait.until(EC.title_is('Missense3D Results'))
    result = driver.find_element(By.XPATH, "/html/body/main/div[2]/h3/div/a[2]")
    link = result.get_attribute('href')
    driver.quit()
    uniprot_id = mutation_data['uniprot_id']
    location = mutation_data['location']
    wild_type = mutation_data['wild_type']
    mutant = mutation_data['mutant']
    folder_name = f'{uniprot_id}_{wild_type}{location}{mutant}'
    HOME_DIR = os.path.expanduser('~')
    file_dir = os.path.join(HOME_DIR, f'SNP Results\\Missense3D Analyses\\{folder_name}')
    try:
        os.makedirs(file_dir)
    except OSError as er:
        return link
    response = requests.get(link)
    results_file = zipfile.ZipFile(io.BytesIO(response.content))
    results_file.extractall(file_dir)
    return link


if __name__ == '__main__':
    get_missense_result({
        'uniprot_id': 'P06280',
        'pdb_code': '3hg3',
        'pdb_chain': 'B',
        'location': '52',
        'wild_type': 'C',
        'mutant': 'R'
    })
