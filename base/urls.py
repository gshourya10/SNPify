from django.urls import path
from .views import get_results, get_home, get_structural_tools, get_functional_tools, predict_snp_job_worker


urlpatterns = [
    path('', get_home, name='home'),
    path('results/', get_results, name='results'),
    path('structural/', get_structural_tools, name='structural'),
    path('functional/', get_functional_tools, name='functional'),
    path('predict_snp_fetch/', predict_snp_job_worker, name='predict_snp')
]
