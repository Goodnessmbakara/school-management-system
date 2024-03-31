from django.shortcuts import render

def home(request):
    return render(request, 'school_website/index.html')