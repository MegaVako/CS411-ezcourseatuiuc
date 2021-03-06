from django.shortcuts import render
from django.template import loader
from .func.mysql_func import form_query, execute_query, parse_raw_result, parse_semesterNyear, form_edit, parse_subjNnum, parse_cookieCart, convert_schedule_to_calendar
from .forms import CourseForm, GenedForm, VoteForm, VoteInitForm, UpdateForm
from django.http import HttpResponse
import jsonpickle

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
    if request.method == "GET":
        search_query = None
        page = "not_found.html"
        context = {}
        gened_form = GenedForm(request.GET)
        if gened_form.is_valid():
            gened_query = form_query(gened_form.cleaned_data, "gened")
            if gened_query['ok']:
                gened_query_result = execute_query(gened_query['query'])
                if gened_query_result['ok']:
                    gened_parsed_result = parse_raw_result(gened_query_result['raw_result'], "gened")
                    if gened_parsed_result['ok']:
                        page = "search_page.html"
                        context['search_input'] = gened_query['query']
                        context['search_result'] = gened_parsed_result['parsed_result']
                    else:
                        context['msg'] = gened_parsed_result['msg']
                else:
                    context['msg'] = gened_query_result['msg']
            else:
                context['msg'] = gened_query['msg']
        else:
            context['msg'] = "Invalid gened form"

    return render(request, page, context)

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
                        if len(course_parsed_result['parsed_result']) == 0:
                            page = "not_found.html"
                            context['msg'] = "valid search on course, but no course found"
                        else:
                            page = "course_page.html"
                            
                            #assume this pass because it passed course_query
                            subjNnum = parse_subjNnum(input_str)
                            #TODO set correct prof for next semester
                            context['base_info'] = {"department": subjNnum['department'], "course_num": subjNnum['number'], "next_prof": teach_parsed_result['next_prof']}
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
    context = {}
    page = "update_page.html"
    if request.method == "GET":
        update_form = VoteInitForm(request.GET)
        if update_form.is_valid():
            context['department'] = update_form.cleaned_data['dept']
            context['course_num'] = update_form.cleaned_data['num']
        else:
            page = "not_found.html"
            context['msg'] = "Invalid update_form init"
    else:
        page = "not_found.html"
        context['mgs'] = "Vote init does not handle POST"
    return render(request, page, context)
    return render(request, page, {})

def thanks_page(request):
    page = "not_found.html"
    context = {}
    ok = True
    if request.method == "POST":
        curr_form = None
        edit_type = ""
        validate_exist = False
        fix_semesterNyear = True
        context['msg'] = None
        msg = ""

        if "insert_opinion" in request.POST:
            curr_form = VoteForm(request.POST)
            if curr_form.is_valid():
                # get fake netid
                fake_netid = execute_query("SELECT LEFT(MD5(RAND()), 8)")
                if fake_netid["ok"]:
                    fake_netid = fake_netid["raw_result"][0][0]
                    curr_form.cleaned_data['netid'] = fake_netid
                    edit_type = "insert_vote"
                    msg = "Insert success"
                else:
                    ok = False
                    context['msg'] = "Generate netid failed"

            else:
                ok = False
                context['msg'] = "Invalid VoteForm"

        elif "update_opinion" in request.POST:
            curr_form = UpdateForm(request.POST)
            if curr_form.is_valid():
                edit_type = "update_vote"
                validate_exist = True
                msg = "Update success"
        
        elif "delete_opinion" in request.POST:
            curr_form = UpdateForm(request.POST)
            if curr_form.is_valid():
                edit_type = "delete_vote"
                validate_exist = True
                fix_semesterNyear = False
                msg = "Delete success"

        if fix_semesterNyear:
            # fix semesterNyear
            semesterNyear = parse_semesterNyear(curr_form.cleaned_data['semesterNyear'])
            if semesterNyear['ok']:
                curr_form.cleaned_data['semester'] = semesterNyear['semester']
                curr_form.cleaned_data['year'] = semesterNyear['year']
            else:
                ok = False
                context['msg'] = "Invalid semester year"

        if validate_exist and context['msg'] == None:
            # validate netid exist
            base_validate = ("SELECT 1 FROM Voted WHERE netid='" + curr_form.cleaned_data['netid'] + 
                "' AND course_num=" + curr_form.cleaned_data['course_num'] + 
                " AND department='" + curr_form.cleaned_data['department'] + "'")
            validate_result = execute_query(base_validate)
            if validate_result['ok']:
                if len(validate_result['raw_result']) == 0:
                    page = "not_found.html"
                    context['msg'] = "your 8-character string has no match for this course's opinion" 
            else:
                ok = False
                context['msg'] = validate_result['msg']

        # generate edit
        if ok:
            edit_query = form_edit(curr_form.cleaned_data, edit_type)
            if edit_query['ok']:
                # execute
                curr_execute = execute_query(edit_query['query'])
                if curr_execute['ok']:
                    # return thanks page
                    page = "thanks.html"
                    context = {"query": edit_query['query'], "netid": curr_form.cleaned_data['netid'], "msg": msg}
                else:
                    context['msg'] = "execute failed " + curr_execute['msg']
            else:
                context['msg'] = edit_query['msg']

    return render(request, page, context)

#===================================================================================
def cart_page(request):
    #TODO validate course exist
    if "check_course" in request.GET:
        return HttpResponse("GET received")

#===================================================================================
def schedule_page(request):
    page = ""
    context = {}
    info_arr = {}
    ok = True
    if request.method == "GET":
        cart_arr = request.COOKIES.get("course")
        parse_cart = parse_cookieCart(cart_arr)
        if parse_cart['ok']:
            for c in parse_cart['result']:
                curr_query = form_query(c, "schedule")
                if curr_query['ok']:
                    curr_result = execute_query(curr_query['query'])    
                    if curr_result['ok']:
                        info_arr[c[0] + c[1]] = parse_raw_result(curr_result['raw_result'], "schedule") 
                    else:
                        page = "not_found.html"
                        context['msg'] = curr_result['msg'] + curr_query['query']
                        ok = False
                        break
                else:
                    page = "not_found.html"
                    context['msg'] = "Unable to format query on " + c[0] + c[1]
                    ok = False
                    break;
            if ok:
                page = "schedule_page.html"
                context['cart_info'] = convert_schedule_to_calendar(info_arr)
        else:
            page = "not_found.html"
            ok = False
            context['msg'] = parse_cart['msg']
    context['ok'] = ok
    wrapper = {}
    wrapper['context'] = jsonpickle.encode(context)
    wrapper['course_group'] = jsonpickle.encode(info_arr)
    return render(request, page, wrapper) 
