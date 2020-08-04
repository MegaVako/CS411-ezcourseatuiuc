from django.db import connection
from django.db import IntegrityError
import random
import traceback

#===================================================================================
def parse_subjNnum(input_str):
    # example CS101
    subject = ""
    number = ""
    msg = "ok"
    input_str = input_str.upper()

    for c in input_str:
        if c.isalpha():
            subject += c
        else:
            break;
    if input_str[-3:].isdigit():
        number = input_str[-3:] 
    else:
        msg = "failed"
    if len(subject) < 2:
        msg = "failed"
    return {"department": subject, "number": number, "msg": msg}

course_select = ["department", "course_num", "semester", "year", "tittle", "requirement_fulfill", "course_description"]
gened_select = ["department", "course_num", "tittle", "requirement_fulfill", "avg_gpa"]
teach_select = ["prof_fname", "prof_lname", "semester", "year", "lecture_type", "avg_gpa"]
vote_select = ["difficulty", "recommand", "comment", "grade", "semester", "year"]
schedule_select = ['crn', 'prof_fname', 'prof_lname', 'department', 'course_num', 'semester', 'year', 'credit_hour', 'part_of_term', 'day_of_week', 'date_start', 'date_end', 'time_start', 'time_end', 'location', 'room_num', 'lecture_type', 'avg_gpa', 'section_num']

#
# parse function for query
#
#===================================================================================
def form_query(input_data, query_on):
    base_query = "SELECT {attri} FROM {table} WHERE {condition} {order} {limit}"
    default_attri = "*"
    default_table = "FA2020"
    default_condition = "1"
    default_order = ""
    default_limit = "LIMIT 20"

    query = base_query
    select_arr = None
    extra_buffer = ""
    extra_ending = ""
    msg = "ok"
    ok = True

    # expect a string len = 5
    if query_on == "course":
        parse_input = parse_subjNnum(input_data)
        if parse_input['msg'] == "failed":
            msg = "failed, on parse_subjNnum"
            ok = False
        else:
            select_arr = course_select
            default_table = "Courses"
            base_condition = "course_num={num} AND department='{department}' AND year=2020 AND semester='fall'"
            default_condition = base_condition.format(num=parse_input['number'], department=parse_input['department'])

    # expect checkbox bool
    elif query_on == "gened":
        '''
        SELECT c.department, c.course_num, c.tittle, c.requirement_fulfill, ROUND(AVG(t.avg_gpa), 2)
        FROM Courses c LEFT OUTER JOIN Teach t ON (c.course_num = t.course_num AND c.department = t.department)
        WHERE c.year = 2019 AND
            c.semester = 'fall' AND
            c.requirement_fulfill LIKE "%CS%" AND
            c.requirement_fulfill LIKE "%NAT%" AND
            t.avg_gpa IS NOT NULL
        GROUP BY c.course_num, c.department
        ORDER BY AVG(t.avg_gpa) DESC
        '''
        select_arr = gened_select[:-1] # compenstae for the extra_ending
        extra_buffer = 'c.'
        extra_ending = ", ROUND(AVG(t.avg_gpa), 2)"
        default_table = "Courses c LEFT OUTER JOIN Teach t ON (c.course_num = t.course_num AND c.department = t.department)"

        has_prev = False
        for k, v in input_data.items():
            if v:
                if has_prev:
                    default_condition += "AND "
                else:
                    default_condition = ""

                default_condition += ("c.requirement_fulfill LIKE '%" + k + "%' ")
                has_prev = True
        
        if default_condition == "1":
            ok = False
            msg = "No gened selected"
        else:
            #default_condition += "AND c.year=2020 AND c.semester='fall' AND t.avg_gpa IS NOT NULL GROUP BY c.course_num, c.department"
            default_condition += "AND c.year=2020 AND c.semester='fall' GROUP BY c.course_num, c.department"
            default_order = "ORDER BY AVG(t.avg_gpa) DESC"
            default_limit = "LIMIT 30"
    
    # expect valid course form
    elif query_on == "vote":
        parse_input = parse_subjNnum(input_data)
        if parse_input['msg'] == "failed":
            msg = "failed, on parse_subjNnum"
            ok = False
        else:
            select_arr = vote_select
            default_table = "Voted"
            base_condition = "course_num={num} AND department='{department}'"
            default_condition = base_condition.format(num=parse_input['number'], department=parse_input['department'])
            default_limit = ""

    elif query_on == "teach":
        parse_input = parse_subjNnum(input_data)
        if parse_input['msg'] == "failed":
            msg = "failed, on parse_subjNnum"
            ok = False
        else:
            default_table = "Teach"
            base_condition = "course_num={num} AND department='{department}'"
            default_condition = base_condition.format(num=parse_input['number'], department=parse_input['department'])
            select_arr = teach_select[:-1]
            extra_ending = ", ROUND(avg_gpa, 2)"
            default_order = " ORDER BY prof_lname"

    elif query_on == "schedule":
        default_table = "Teach"
        select_arr = schedule_select
        base_condition = " course_num={num} AND department='{department}' AND semester='fall' AND year=2020"
        default_condition = base_condition.format(num=input_data[1], department=input_data[0])
    else:
        msg = "failed, query_on not implimented"
        ok = False

    if ok:
        default_attri = ""
        has_prev = False
        for attri in select_arr: 
            if has_prev:
                default_attri += ", "
            default_attri += (extra_buffer + attri)
            has_prev = True
        default_attri += extra_ending
        query = base_query.format(attri=default_attri, table=default_table, condition=default_condition, order=default_order, limit=default_limit)

    return {"query": query, "msg": msg, "ok": ok} 

#===================================================================================
def execute_query(query):
    result = {}
    ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchall()
    except:
        return {"query": query, "msg": str(traceback.format_exc()) + " failed " + str(query), "ok": False}
    finally:
        cursor.close()
    return {"raw_result": row, "query": query, "msg": "ok", "ok": True}

#===================================================================================
def parse_raw_result(raw_result, parse_on):
    select_arr = None
    result_arr = []
    msg = "ok"
    ok = True
    requirement_fulfill = False
    day_check = False
    next_prof = False
    prof_curr = ""
    curr_type = ""

    if parse_on == "course":
        select_arr = course_select
        requirement_fulfill = True
    elif parse_on == "vote":
        select_arr = vote_select
    elif parse_on == "teach":
        select_arr = teach_select
        next_prof = True
    elif parse_on == "gened":
        select_arr = gened_select
    elif parse_on == "schedule":
        day_check = True
        select_arr = schedule_select 
    else:
        msg = "failed, parsed_on not implimented"
        ok = False

    if msg != "failed":
        for row in raw_result:
            curr_dict = {}
            counter = 0
            for attri in select_arr:
                curr_dict[attri] = row[counter]
                counter += 1
            if next_prof: # assume working on one course
                if curr_dict['year'] == 2020 and curr_dict['semester'] == 'fall':
                    curr_concat = curr_dict['prof_lname'] + "," + curr_dict['prof_fname']
                    if curr_type == "":
                        prof_curr = curr_concat 
                        curr_type = curr_dict['lecture_type']

                    elif "Lecture" in curr_type and "Lecture" in curr_dict['lecture_type']:
                        if curr_concat not in prof_curr:
                            prof_curr += " and " + curr_concat

                    elif "Lecture" not in curr_type and "Lecture" in curr_dict['lecture_type']:
                        prof_curr = curr_concat 
                       
                    elif "Lecture" not in curr_type and "Lecture" not in curr_dict['lecture_type']:
                        if curr_concat not in prof_curr:
                            prof_curr += " and " + curr_concat

            if requirement_fulfill:
                if curr_dict['requirement_fulfill'] == None or curr_dict['requirement_fulfill'] == "":
                    curr_dict['requirement_fulfill'] = "(Not a gened)"
            if day_check:
                curr_dict['color'] = random.randint(1, 12) 
                if curr_dict['time_start'] == None or curr_dict['time_start'] == "ARRANGED":
                    curr_dict['time_start'] = -1 #TODO handle in template syntax
                    curr_dict['time_end'] = -1 #TODO handle in template syntax
                else:
                    # time_start
                    orig_time = curr_dict['time_start']
                    curr_time = curr_dict['time_start']
                    if curr_time[-2:] == "PM" and curr_time[:2] != '12':                         
                        curr_dict['time_start'] = (str(int(curr_time[:2]) + 12) + curr_time[2:-3])
                    else:
                        curr_dict['time_start'] = curr_time[:-3] # 11:00 AM

                    # time_end
                    curr_time = curr_dict['time_end']
                    if curr_time[-2:] == "PM" and curr_time[:2] != '12':                         
                        curr_dict['time_end'] = (str(int(curr_time[:2]) + 12) + curr_time[2:-3])
                    else:
                        curr_dict['time_end'] = curr_time[:-3] # 11:00 AM

                    # num of 5mins block
                    curr_dict['time_diff'] = (int(curr_dict['time_end'][:2]) - int(curr_dict['time_start'][:2])) * 12 + (int(curr_dict['time_end'][-2:]) - int(curr_dict['time_start'][-2:])) / 5 

            result_arr.append(curr_dict)
    
    return {"parsed_result": result_arr, "msg": msg, "ok": ok, "next_prof": prof_curr}

def parse_semesterNyear(input_str):
    ok = True
    semester = ""
    year = ""
    msg = ""

    first_two = input_str[:2].upper()
    if first_two == "FA":
        semester = "fall"
    elif first_two == "SP":
        semester = "spring"
    elif first_two == "SU":
        semester = "summer"
    elif first_two == "WI":
        semester = "winter"
    else:
        ok = False
        msg = "Not recognized semester"

    if input_str[-2:].isdigit():
        year = str(int(input_str[-2:]) + 2000)
    else:
        ok = False
        msg = "Not recognized year"

    return {"msg": msg, "year": year, "semester": semester, "ok": ok}


vote_attri = ['netid', 'department', 'course_num', 'semester', 'year', 'difficulty', 'recommand', 'comment', 'current_status', 'grade']
base_edit = "{operation} {table} {condition}"
#===================================================================================
def form_edit(input_data, edit_on):
    ok = True
    msg = ""
    default_operation = ""
    default_table = "Voted"
    default_condition = ""

    if edit_on == "insert_vote":
        default_operation = "INSERT INTO"
        default_table = "Voted"
        default_condition = "VALUES({value})"
        curr_condition = ""
        has_prev = False
        for attri in vote_attri:
            if has_prev:
                curr_condition += ", "
            if input_data[attri].isdigit():
                curr_condition += str(input_data[attri])
            else:
                curr_condition += "'" + str(input_data[attri]) + "'"
            has_prev = True
        default_condition = default_condition.format(value=curr_condition)
        
    elif edit_on == "update_vote":
        default_operation = "UPDATE"
        default_condition = "SET {attri} WHERE {condition}"
        has_prev = False
        curr_set = ""
        for attri in vote_attri:
            if has_prev:
                curr_set += ", "
            if input_data[attri].isdigit():
                curr_set += (attri + "=" + str(input_data[attri]))
            else:
                curr_set += (attri + "='" + str(input_data[attri]) + "'")
            has_prev = True
        curr_condition = (" netid='" + input_data['netid'] + 
            "' AND course_num=" + input_data['course_num'] + 
            " AND department='" + input_data['department'] + "'")
        default_condition = default_condition.format(attri=curr_set, condition=curr_condition)

    elif edit_on == "delete_vote":
        default_operation = "DELETE FROM"
        default_condition = ("WHERE netid='" + input_data['netid'] + 
            "' AND course_num=" + input_data['course_num'] + 
            " AND department='" + input_data['department'] + "'")

    else:
        ok = False
        msg = "edit_on not implimented"

    return {"query": base_edit.format(operation=default_operation, table=default_table, condition=default_condition), "msg": msg, "ok": ok}


# return arr of tuple [("CS", "101"), ...]
#===================================================================================
def parse_cookieCart(input_str):
    ok = True
    msg = ""
    result = []
    
    if len(input_str) == 0:
        msg = "no course selected"
        ok = False
    else:
        each_course = input_str.split("|")
        if len(each_course) == 0:
            msg = 'manually modified cart?'
            ok = False
        else:
            for c in each_course:
                if len(c) > 7:
                    msg = 'manually modified cart? Invalid course ' + c
                    ok = False
                    break
                else:
                    split_sNn = parse_subjNnum(c) 
                    if split_sNn['msg'] == 'ok':
                        result.append((split_sNn['department'], split_sNn['number']))
                    else:
                        ok = False
                        msg = "Invalid course format " + c
                        break
    return {"result": result, "msg": msg, "ok": ok}

# expect a dict of dict with where 2nd dict has key "parsed_result" 
#       and it contains val = arr of sections dict
#===================================================================================
def convert_schedule_to_calendar(input_dict):
    result = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}
    key_arr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for k, v in input_dict.items():
        for info in v['parsed_result']:
            curr_bit = info['day_of_week']
            for x in range(0, 5):
                if (curr_bit & 0x01) != 0: 
                    result[key_arr[x]].append(info)
                curr_bit = curr_bit >> 1
    return result
