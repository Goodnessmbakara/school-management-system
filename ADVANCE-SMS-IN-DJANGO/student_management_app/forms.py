from django import forms 
from django.forms import Form
from django.core.exceptions import ValidationError
from student_management_app.models import Classes, SessionYearModel, SubClasses, Grade

from django.contrib.auth import get_user_model
CustomUser = get_user_model()


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'session_year', 'term', 'test1', 'test2', 'test3', 'exam']

    def clean(self):
        # Add any custom validations here
        cleaned_data = super().clean()
        # Example: Validate that test and exam scores are not negative
        exam = cleaned_data.get('exam')
        if exam and exam < 0:
            raise forms.ValidationError("Exam scores cannot be negative.")
        return cleaned_data
class SessionYearForm(forms.ModelForm):
    class Meta:
        model = SessionYearModel
        fields = ['session_start_year', 'session_end_year', 'is_current']
        widgets = {
            'session_start_year': forms.DateInput(attrs={'type': 'date'}),
            'session_end_year': forms.DateInput(attrs={'type': 'date'}),
            'is_current': forms.CheckboxInput()
        }

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get("session_start_year")
        end_year = cleaned_data.get("session_end_year")
        if start_year and end_year:
            if start_year >= end_year:
                raise ValidationError("The end year must be greater than the start year.")
            if start_year.year != end_year.year - 1:
                raise ValidationError("Session should span exactly one year.")

class ClassForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = ['class_name', 'level', 'class_teacher']
        widgets = {
            'class_teacher': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, teacher_queryset=None, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        if teacher_queryset is not None:
            self.fields['class_teacher'].queryset = teacher_queryset

class SubClassForm(forms.ModelForm):
    class Meta:
        model = SubClasses
        fields = ['subclass_name', 'subclass_code', 'subclass_teacher']

    def __init__(self, *args, **kwargs):
        super(SubClassForm, self).__init__(*args, **kwargs)
        # Initially set the queryset for subclass_teacher to none
        self.fields['subclass_teacher'].queryset = CustomUser.objects.none()

    # Update the queryset for subclass_teacher based on selected parent class
    def set_teachers(self, queryset):
        self.fields['subclass_teacher'].queryset = queryset


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    #For Displaying Classes
    try:
        classes = Classes.objects.all()
        class_list = []
        for single_class in classes:
            single_class = (classes.id, classes.class_name)
            class_list.append(single_class)
    except:
        class_list = []
    
    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
            session_year_list.append(single_session_year)

    except:
        session_year_list = []

    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )

    class_id = forms.ChoiceField(label="Class", choices=class_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))

    level = forms.ChoiceField(label="Level", choices=Classes.LEVEL_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
    # Modify class_id field to not initialize choices here, it will be dynamically loaded

    class_id = forms.ChoiceField(label="Class", choices=[], widget=forms.Select(attrs={"class": "form-control"}))

    def clean(self):
        # Add any custom validations here
        cleaned_data = super().clean()
        # Example: Validate that test and exam scores are not negative
        exam = cleaned_data.get('email')
        if CustomUser.objects.get(email=email):
            raise forms.ValidationError("User already exists, Use another email")
        return cleaned_data

class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    #For Displaying Classes
    try:
        classes = Classes.objects.all()
        classes_list = []
        for classes in classes:
            single_class = (classes.id, classes.class_name)
            classes_list.append(single_class)
    except:
        classes_list = []

    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
            session_year_list.append(single_session_year)

    except:
        session_year_list = []


    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )

    class_id = forms.ChoiceField(label="Class", choices=classes_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))