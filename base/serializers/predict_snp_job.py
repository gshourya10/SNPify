from rest_framework import serializers
from ..models.predict_snp_model import PredictSNPJobModel


class PredictSNPJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictSNPJobModel
        fields = (
            "id",
            "job_id",
            "status",
            "root_folder"
        )
