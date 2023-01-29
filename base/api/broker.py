from .hope import get_hope_result
from .missense import get_missense_result
from .polyphen import get_polyphen_results
from .snps_and_go import get_snps_and_go_result
from .mutation_taster import get_mutation_taster_results
from .predict_snp import get_predict_snp_results
from base.utils.helpers import combine_data
import threading

tool_apis = {
    'hope': get_hope_result,
    'missense': get_missense_result,
    'polyphen': get_polyphen_results,
    'snps_and_go': get_snps_and_go_result,
    'mutation_taster': get_mutation_taster_results,
    'predict_snp': get_predict_snp_results
}

THREAD_POOL_SIZE = 3


def run_batch_jobs(data, tool, email):
    if tool == 'predict_snp':
        data = combine_data(data)
        if not email:
            email = "xyz@gmail.com"

    i = 0

    while i < len(data):
        objects = data[i:i + THREAD_POOL_SIZE]
        threads = []
        for obj in objects:
            if email:
                obj['email'] = email
            threads.append(threading.Thread(target=tool_apis[tool], args=(obj,)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        i += THREAD_POOL_SIZE
