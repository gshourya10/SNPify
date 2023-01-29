from django.urls import path
from .views import get_results, get_home, get_structural_tools, get_functional_tools


urlpatterns = [
    path('', get_home, name='home'),
    path('results/', get_results, name='results'),
    path('structural/', get_structural_tools, name='structural'),
    path('functional/', get_functional_tools, name='functional')
]
