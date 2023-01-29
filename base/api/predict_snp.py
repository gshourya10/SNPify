import datetime
import time
import os
from base64 import b64decode
import requests
from urllib import parse
import json
import zipfile
import io

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from base.models.predict_snp_model import PredictSNPJobModel
from base.utils.helpers import log_error, retry_thrice

chrome_options = Options()
chrome_options.add_argument("--headless")

UNIPROT_URL = 'https://rest.uniprot.org/uniprotkb/'


@log_error
@retry_thrice
def get_predict_snp_results(mutation_data):
    print(mutation_data)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://loschmidt.chemi.muni.cz/predictsnp1/')
    wait = WebDriverWait(driver, 120)
    fasta_sequence = requests.get(url=UNIPROT_URL + f"{mutation_data['uniprot_id']}.fasta")
    if fasta_sequence.text.find("invalid") != -1:
        return
    driver.find_element(By.CSS_SELECTOR, '#isc_18').send_keys(fasta_sequence.text)
    driver.find_element(By.CSS_SELECTOR, '#isc_14').click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '#isc_22').click()

    mutations = []
    for mut in mutation_data.get("mutations"):
        formatted_text = f"{mut['wild_type']}{mut['location']}{mut['mutant']}"
        mutations.append(formatted_text)

    button = driver.find_element(By.CSS_SELECTOR, '#isc_23 > table > tbody > tr > td')
    driver.execute_script("arguments[0].click();", button)
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, 'textarea[name="isc_TextAreaItem_2"]').send_keys('\n'.join(mutations))
    driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/div/div/div/table/tbody/tr/td/div').click()
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, '#isc_C4').send_keys(mutation_data["email"])
    driver.find_element(By.CSS_SELECTOR, '#isc_BY').click()
    wait.until(EC.url_contains('jobId'))
    link = driver.current_url
    driver.quit()
    query_params = dict(parse.parse_qsl(parse.urlsplit(link).query))
    job_id = query_params.get('jobId')
    print(job_id)
    if job_id:
        new_job = PredictSNPJobModel(job_id=job_id,
                                     status='pending',
                                     root_folder=mutation_data.get('uniprot_id'))
        new_job.save()
    return link


def save_result(job_id, root_folder):
    response = requests.get(f"https://loschmidt.chemi.muni.cz/predictsnp1-data/"
                            f"resources/?action=results&format=zip&jobId={job_id}")

    job = PredictSNPJobModel.objects.get(job_id=job_id)
    if response.status_code == 500:
        job.status = "failed"
        job.save()
        return

    folder_name = root_folder
    HOME_DIR = os.path.expanduser('~')
    file_dir = os.path.join(HOME_DIR, f'SNP Results\\PredictSNP Analyses\\{folder_name}')
    try:
        os.makedirs(file_dir)
    except OSError as er:
        return

    results_file = zipfile.ZipFile(io.BytesIO(response.content))
    results_file.extractall(file_dir)
    job.status = "completed"
    job.save()


if __name__ == '__main__':
    id = get_predict_snp_results({'uniprot_id': 'P51587 ',
                                  'mutations': [{'wild_type': 'A', 'location': 39, 'mutant': 'V'},
                                                {'wild_type': 'F', 'location': 590, 'mutant': 'A'},
                                                {'wild_type': 'K', 'location': 2939, 'mutant': 'C'},
                                                {'wild_type': 'L', 'location': 2999, 'mutant': 'P'},
                                                {'wild_type': 'D', 'location': 1898, 'mutant': 'W'}],
                                  'email': 'jim@gmail.com'})
    print(id)
