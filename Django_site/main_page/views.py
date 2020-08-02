from django.shortcuts import render
from django.template import loader
from .func.mysql_func import form_query, execute_query, parse_raw_result, parse_sememsterNyear, form_edit
from .forms import CourseForm, GenedForm, VoteForm, VoteInitForm
from django.http import HttpResponse

#===================================================================================
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

#===================================================================================
def main_page(request):
    return render(request, "main_page.html", {})

#===================================================================================
def search_page(request):
    return HttpResponse(form_query())
    #return render(request, "search_page.html", {})

#===================================================================================
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


#===================================================================================
def vote_page(request):
    context = {}
    page = "vote_page.html"
    if request.method == "GET":
        vote_form = VoteInitForm(request.GET)
        if vote_form.is_valid():
            context['department'] = vote_form.cleaned_data['dept']
            context['course_num'] = vote_form.cleaned_data['num']
        else:
            page = "not_found.html"
            context['msg'] = "Invalid vote_form init"
    else:
        page = "not_found.html"
        context['mgs'] = "Vote init does not handle POST"
    return render(request, page, context)


#===================================================================================
def update_page(request):
    #if request.method == "GET":
    return render(request, "udpate_page.html", {})

def thanks_page(request):
    page = "not_found.html"
    context = {}
    if request.method == "POST":
        vote_form = VoteForm(request.POST)
        if vote_form.is_valid():
            if "insert_opinion" in request.POST:
                # get fake netid
                fake_netid = execute_query("SELECT LEFT(MD5(RAND()), 8)")
                if fake_netid["ok"]:
                    fake_netid = fake_netid["raw_result"][0][0]
                    vote_form.cleaned_data['netid'] = fake_netid
                else:
                    context['msg'] = "Generate netid failed"

                # fix sememsterNyear
                sememsterNyear = parse_sememsterNyear(vote_form.cleaned_data['sememsterNyear'])
                if sememsterNyear['ok']:
                    vote_form.cleaned_data['semester'] = sememsterNyear['semester']
                    vote_form.cleaned_data['year'] = sememsterNyear['year']
                else:
                    context['msg'] = "Invalid semester year"

                # generate edit
                edit_query = form_edit(vote_form.cleaned_data, "insert_vote")
                if edit_query['ok']:
                    # execute
                    insert_execute = execute_query(edit_query['query'])

                    if insert_execute['ok']:
                        # return thanks page
                        page = "thanks.html"
                        context = {"query": edit_query['query'], "netid": fake_netid}
                    else:
                        context['msg'] = "execute failed " + insert_execute['msg']
                else:
                    context['msg'] = edit_query['msg']


            elif "update_opinion" in request.POST:
                pass
            elif "delete_opinion" in request.POST:
                pass
            else:
                pass
        else:
            context['msg'] = "Invalid VoteForm"
    return render(request, page, context)

#===================================================================================
def schedule_page(request):
    pass

