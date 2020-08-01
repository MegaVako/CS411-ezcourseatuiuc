from django.shortcuts import render
from django.template import loader

# Create your views here.
def main_page(request):
    return render(request, "main_page.html", {})
def search_page(request):
    return render(request, "search_page.html", {})
def course_page(request):
    return render(request, "course_page.html", {})
def vote_page(request):
    return render(request, "vote_page.html", {})
def update_page(request):
    return render(request, "udpate_page.html", {})
def thanks_page(request):
    pass
def schedule_page(request):
    pass
