from django import forms

class course_form(forms.Form):
    search_input = forms.CharField(max_length=5)

class gened_form(forms.Form):
    SBS = forms.BooleanField(required=False)
    QR = forms.BooleanField(required=False)
    NAT = forms.BooleanField(required=False)
    HUM = forms.BooleanField(required=False)
    CS = forms.BooleanField(required=False)
    COMP1 = forms.BooleanField(required=False)
    ACP = forms.BooleanField(required=False)