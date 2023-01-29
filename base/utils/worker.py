from ..models.predict_snp_model import PredictSNPJobModel
from ..serializers.predict_snp_job import PredictSNPJobSerializer
from ..api.predict_snp import save_result


def update_predict_snp_tasks():
    query_set = PredictSNPJobModel.objects.filter(status='pending')
    pending_jobs = PredictSNPJobSerializer(query_set, many=True).data

    for job in pending_jobs:
        if job.get('job_id'):
            job_id = job.get("job_id")
            root_folder = job.get("root_folder")
            save_result(job_id, root_folder)
