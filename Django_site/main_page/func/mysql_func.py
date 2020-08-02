from django.db import connection
from django.db import IntegrityError
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

course_select = ["department", "course_num", "semester", "year", "title", "requirement_fulfill", "course_description"]
gened_select = ["department", "course_num", "tittle", "requirement_fulfill", "avg_gpa"]
teach_select = ["prof_fname", "prof_lname", "semester", "year", "avg_gpa"]
vote_select = ["difficulty", "recommand", "comment", "grade", "semester", "year"]

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
        FROM Courses c LEFT OUTER JOIN Teach_test t ON (c.course_num = t.course_num AND c.department = t.department)
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
        default_table = "Courses c LEFT OUTER JOIN Teach_test t ON (c.course_num = t.course_num AND c.department = t.department)"
        default_condition = "c.year=2020 AND c.semester=fall"
        #TODO finish condition
        #TODO add group/order

    #TODO
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
            select_arr = teach_select[:-1]
            default_table = "Teach"
            base_condition = "course_num={num} AND department='{department}'"
            default_condition = base_condition.format(num=parse_input['number'], department=parse_input['department'])
            #default_condition += " AND avg_gpa IS NOT NULL"
            extra_ending = ", ROUND(avg_gpa, 2)"
            default_order = " ORDER BY prof_lname"

    else:
        msg = "failed, query_on not implimented"
        ok = False

    if "failed" not in msg:
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

    if parse_on == "course":
        select_arr = course_select
        requirement_fulfill = True
    elif parse_on == "vote":
        select_arr = vote_select
    elif parse_on == "teach":
        select_arr = teach_select
    elif parse_on == "gened":
        select_arr = gened_select
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
            if requirement_fulfill:
                if curr_dict['requirement_fulfill'] == None or curr_dict['requirement_fulfill'] == "":
                    curr_dict['requirement_fulfill'] = "(Not a gened)"

            result_arr.append(curr_dict)
    
    return {"parsed_result": result_arr, "msg": msg, "ok": ok}

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

