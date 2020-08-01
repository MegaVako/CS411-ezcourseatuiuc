from django.shortcuts import render
from django.template import loader
from .func.mysql_func import form_query, execute_query, parse_raw_result
from .forms import CourseForm, GenedForm 
from django.http import HttpResponse

# Create your views here.
def main_page(request):
    return render(request, "main_page.html", {})

def search_page(request):
    return HttpResponse(form_query())
    #return render(request, "search_page.html", {})

def course_page(request):
    page = "main_page.html"
    context = {}
    if request.method == "GET":
        course_form = CourseForm(request.GET)
        if course_form.is_valid():
            course_query = form_query(course_form.cleaned_data['search_input'], "course")
            if course_query["ok"]:
                course_query_result = execute_query(course_query['query'])
                if course_query_result["ok"]:
                    course_parsed_result = parse_raw_result(course_query_result['raw_result'], "course")
                    if course_parsed_result["ok"]:
                        page = "course_page.html"
                        context['course_info'] = course_parsed_result['parsed_result']
                    else:
                        page = "not_found.html"
                        context['msg'] = course_parsed_result['msg']
                else:
                    page = "not_found.html"
                    context['msg'] = course_query_result['msg']
            else:
                page = "not_found.html"
                context['msg'] = course_query['msg']
        else:
            page = "not_found.html"
            context['msg'] = "invalid course_form"
    return render(request, page, context)

def vote_page(request):
    return render(request, "vote_page.html", {})
def update_page(request):
    return render(request, "udpate_page.html", {})
def thanks_page(request):
    pass
def schedule_page(request):
    pass
