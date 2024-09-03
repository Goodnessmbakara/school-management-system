from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import Form
from student_management_app.models import (Classes, Grade, SessionYearModel, Subject, ClassSubject,Staffs,
                                           Students, SubClasses)

CustomUser = get_user_model()


class AddSubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_name', 'level', 'class_obj', 'subject_teacher']

    level = forms.ChoiceField(choices=Classes.LEVEL_CHOICES, label="Level")
    class_obj = forms.ModelChoiceField(queryset=Classes.objects.none(), label="Class")
    subject_teacher = forms.ModelChoiceField(queryset=Staffs.objects.none(), required=False, label="Subject Teacher")

    def __init__(self, *args, **kwargs):
        super(AddSubjectForm, self).__init__(*args, **kwargs)
        self.fields['subject_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['level'].widget.attrs.update({'class': 'form-select custom-select'})
        self.fields['class_obj'].widget.attrs.update({'class': 'form-select custom-select'})
        self.fields['subject_teacher'].widget.attrs.update({'class': 'form-select custom-select'})
        
        # Ensure queryset is populated based on level if POST data is provided
        if 'level' in self.data:
            try:
                level = self.data.get('level')
                self.fields['class_obj'].queryset = Classes.objects.filter(level=level)
            except (ValueError, TypeError):
                self.fields['class_obj'].queryset = Classes.objects.none()
        elif self.instance.pk:
            self.fields['class_obj'].queryset = Classes.objects.filter(level=self.instance.level)
        
        self.fields['subject_teacher'].queryset = Staffs.objects.all()

class EditSubclassSubjectForm(forms.Form):
    subclass_subject_id = forms.IntegerField(widget=forms.HiddenInput())
    subject_teacher = forms.ModelChoiceField(queryset=Staffs.objects.all(), required=True, label="Subject Teacher", widget=forms.Select(attrs={'class': 'form-select custom-select'}))

    def __init__(self, *args, **kwargs):
        super(EditSubclassSubjectForm, self).__init__(*args, **kwargs)
        self.fields['subject_teacher'].widget.attrs.update({'class': 'form-control form-control-sm'})
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

class SubjectForm(forms.ModelForm):
    class_level = forms.ChoiceField(choices=Classes.LEVEL_CHOICES)
    
    class Meta:
        model = Subject
        fields = ['subject_name', 'class_level']

class ClassSubjectForm(forms.ModelForm):
    class_level = forms.ChoiceField(choices=[('Nursery', 'Nursery'), ('Primary', 'Primary'), ('Secondary', 'Secondary')], required=True)
    class_id = forms.ModelChoiceField(queryset=Classes.objects.none(), required=True)
    subject_teacher = forms.ModelChoiceField(queryset=CustomUser.objects.filter(user_type='2'), required=False)

    class Meta:
        model = ClassSubject
        fields = ['class_id', 'subject_teacher']

    def __init__(self, *args, **kwargs):
        class_level = kwargs.pop('class_level', None)  # Retrieve class_level from kwargs
        super(ClassSubjectForm, self).__init__(*args, **kwargs)
        
        if class_level:
            self.fields['class_id'].queryset = Classes.objects.filter(level=class_level)  # Set queryset based on level

        # Hide subject teacher field initially if not Nursery
        if class_level != 'Nursery':
            self.fields['subject_teacher'].widget = forms.HiddenInput()


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'})
        }
    # # Additional fields for Students model
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(choices=Students.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    profile_pic = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    session_year_id = forms.ModelChoiceField(queryset=SessionYearModel.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    level = forms.ChoiceField(choices=Classes.LEVEL_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    class_id = forms.ModelChoiceField(queryset=Classes.objects.none(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    subclass_id = forms.ModelChoiceField(queryset=SubClasses.objects.none(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already in use.")
        return username
    
    
            
    def __init__(self, *args, **kwargs):
        super(AddStudentForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
    
        # Prepopulate classes and subclasses if instance is provided
        if self.instance.pk:
            self.fields['class_id'].queryset = Classes.objects.filter(level=self.instance.level)
            self.fields['subclass_id'].queryset = SubClasses.objects.filter(parent_class=self.instance.class_id)

        # Dynamically load class_id and subclass_id choices based on the level
        if 'level' in self.data:
            try:
                level = self.data.get('level')
                self.fields['class_id'].queryset = Classes.objects.filter(level=level)
                if 'class_id' in self.data:
                    class_id = self.data.get('class_id')
                    self.fields['subclass_id'].queryset = SubClasses.objects.filter(parent_class__id=class_id)
            except (ValueError, TypeError):
                pass



class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))

    try:
        classes_list = [(cls.id, cls.class_name) for cls in Classes.objects.all()]
    except:
        classes_list = []

    try:
        session_year_list = [(sy.id, f"{sy.session_start_year} to {sy.session_end_year}") for sy in SessionYearModel.objects.all()]
    except:
        session_year_list = []

    gender_list = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    class_id = forms.ChoiceField(label="Class", choices=classes_list, widget=forms.Select(attrs={"class": "form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class": "form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list, widget=forms.Select(attrs={"class": "form-control"}))
    profile_pic = forms.ImageField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class": "form-control"}))

