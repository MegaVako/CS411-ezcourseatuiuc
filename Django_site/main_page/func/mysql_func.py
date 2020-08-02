from django.db import connection
from django.db import IntegrityError
import traceback

def parse_subjNnum(input_str):
    # example CS101
    subject = ""
    number = ""
    msg = "ok"
    input_str = input_str.upper()

    for c in input_str[:-3]:
        if c.isalpha():
            subject += c
        else:
            msg = "failed"
    if input_str[-3:].isdigit():
        number = input_str[-3:] 
    else:
        msg = "failed"
    return {"department": subject, "number": number, "msg": msg}

course_select = ["department", "course_num", "semester", "year", "title", "requirement_fulfill", "course_description"]
gened_select = ["department", "course_num", "tittle", "requirement_fulfill", "avg_gpa"]
teach_select = ["prof_fname", "prof_lname", "semester", "year", "avg_gpa"]
vote_select = ["difficulty", "recommand", "comment", "grade"]
#
# parse function for query
#
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


    #TODO
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
            default_order = " ORDER BY year DESC, semester"

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
                if curr_dict['requirement_fulfill'] == None:
                    curr_dict['requirement_fulfill'] = "(Not a gened)"

            result_arr.append(curr_dict)
    
    return {"parsed_result": result_arr, "msg": msg, "ok": ok}

