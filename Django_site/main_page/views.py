from django.shortcuts import render
from django.template import loader
from .func.mysql_func import form_query, execute_query, parse_raw_result
from .forms import CourseForm, GenedForm 
from django.http import HttpResponse

def calculate_avg(arr, key):
    total = 0
    count = 0
    for x in arr:
        if x[key] != None and x[key] != "NULL":
            total += float(x[key])
            count += 1
    if (count == 0):
        return -1 
    return total / count

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
            input_str = course_form.cleaned_data['search_input']
            course_query = form_query(input_str, "course")
            teach_query = form_query(input_str, "teach")
            vote_query = form_query(input_str, "vote")

            if course_query["ok"]:
                course_query_result = execute_query(course_query['query'])
                teach_query_result = execute_query(teach_query['query'])
                vote_query_result = execute_query(vote_query['query'])

                if teach_query_result['ok'] and course_query_result["ok"] and vote_query_result["ok"]:
                    course_parsed_result = parse_raw_result(course_query_result['raw_result'], "course")
                    teach_parsed_result = parse_raw_result(teach_query_result['raw_result'], "teach")
                    vote_parsed_result = parse_raw_result(vote_query_result['raw_result'], "vote")

                    if course_parsed_result["ok"] and teach_parsed_result["ok"] and vote_query_result["ok"]:
                        page = "course_page.html"
                        context['base_info'] = {"department": input_str[:2].upper(), "course_num": input_str[-3:]}
                        context['course_info'] = course_parsed_result['parsed_result']
                        context['teach_info'] = teach_parsed_result['parsed_result']
                        context['vote_info'] = vote_parsed_result['parsed_result']
                        
                        diff_avg = round(calculate_avg(vote_parsed_result['parsed_result'], "difficulty") * 10, 2)
                        recom_avg = round(calculate_avg(vote_parsed_result['parsed_result'], "recommand") * 10, 2)
                        if diff_avg == -10:
                            diff_avg = 50
                            recom_avg = 50
                        gpa_avg = round(calculate_avg(teach_parsed_result['parsed_result'], "avg_gpa") / 0.04, 2)
                        context['avg_info'] = {"diff_avg": diff_avg, "recom_avg": recom_avg, "gpa_avg": gpa_avg, "gpa_info_gpa": round(gpa_avg * 0.04, 2)}
                    else:
                        page = "not_found.html"
                        context['msg'] = course_parsed_result['msg'] + " " + teach_parsed_result['msg']
                else:
                    page = "not_found.html"
                    context['msg'] = course_query_result['msg'] + " " + teach_query_result['msg'] + " " + vote_query_result['msg']
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

