from django import forms

class CourseForm(forms.Form):
    search_input = forms.CharField(max_length=8, required=True)

class GenedForm(forms.Form):
    SBS = forms.BooleanField(required=False)
    QR = forms.BooleanField(required=False)
    NAT = forms.BooleanField(required=False)
    HUM = forms.BooleanField(required=False)
    CS = forms.BooleanField(required=False)
    COMP1 = forms.BooleanField(required=False)
    ACP = forms.BooleanField(required=False)

class VoteInitForm(forms.Form):
    dept = forms.CharField(max_length=4)
    num = forms.CharField(max_length=3)

STATUS_CHOICE = [("finished", "finished"),("unfinished", "unfinished")]
class VoteForm(forms.Form):
    semesterNyear = forms.CharField(max_length=4, required=True)
    current_status = forms.ChoiceField(choices=STATUS_CHOICE, widget=forms.RadioSelect()) 
    grade = forms.CharField(max_length=3, required=True) 
    difficulty = forms.CharField(max_length=2, required=True) 
    recommand = forms.CharField(max_length=2, required=True) 
    comment = forms.CharField(max_length=1000, required=False)
    department = forms.CharField(max_length=4)
    course_num = forms.CharField(max_length=3)

class UpdateForm(forms.Form):
    netid = forms.CharField(max_length=8, required=True)
    semesterNyear = forms.CharField(max_length=4, required=True)
    current_status = forms.ChoiceField(choices=STATUS_CHOICE, widget=forms.RadioSelect()) 
    grade = forms.CharField(max_length=3, required=True) 
    difficulty = forms.CharField(max_length=2, required=True) 
    recommand = forms.CharField(max_length=2, required=True) 
    comment = forms.CharField(max_length=1000, required=False)
    department = forms.CharField(max_length=4)
    course_num = forms.CharField(max_length=3)
