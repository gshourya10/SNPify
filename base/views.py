from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib import messages
from .api import broker
from .api.utils.data_params import valid_data_fields
from .utils.helpers import parse_file, sanitize_data
import threading


def get_home(request):
    return render(request, 'base/landing.html')


def get_structural_tools(request):
    return render(request, 'base/structural.html')


def get_functional_tools(request):
    return render(request, 'base/functional.html')


def get_results(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    else:
        tool = request.POST['tool']
        mutation_data: InMemoryUploadedFile = request.FILES['mutation_data']
        email = ""
        if request.POST.get('email'):
            email = request.POST['email']
        try:
            parsed_data = parse_file(mutation_data)
            data = sanitize_data(tool, parsed_data)
            if len(data) == 0:
                messages.add_message(request, messages.ERROR,
                                     message=f"Data sent is invalid for {tool}. "
                                             f"Make sure the data has the following fields: {valid_data_fields[tool]}")
                return redirect('/')
            fetch_results = threading.Thread(target=broker.run_batch_jobs, args=(parsed_data, tool, email))
            fetch_results.start()
            messages.add_message(request, messages.SUCCESS, message="Successfully submitted the data for analysis.")
            return redirect('/')
        except Exception as e:
            print(e)
            messages.add_message(request, messages.WARNING, message="An error occurred.")
            return redirect('/')
