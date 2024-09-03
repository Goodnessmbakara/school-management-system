import json

from django.contrib import messages
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.files.storage import \
    FileSystemStorage  # To upload Profile Picture
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Count, Prefetch, Q, F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from student_management_app.models import (Attendance, AttendanceReport,
                                           Classes, ClassSubject, CustomUser,
                                           FeedBackStaffs, FeedBackStudent,
                                           LeaveReportStaff,
                                           LeaveReportStudent,
                                           SessionYearModel, Staffs, Students,
                                           SubClasses, SubclassSubject,
                                           Subject)

from .forms import (AddStudentForm, AddSubjectForm, ClassForm,
                    ClassSubjectForm, EditStudentForm, EditSubclassSubjectForm,
                    GradeForm, SessionYearForm, SubClassForm, SubjectForm)
from .models import SubclassSubject, Subject


def admin_home(request):
    all_student_count = Students.objects.count()
    subject_count = Subject.objects.count()
    class_count = Classes.objects.count()
    staff_count = Staffs.objects.count()

    # Optimize the data fetching for classes and subjects
    classes_all = Classes.objects.annotate(
        subjects_count=Count('class_subjects'),  # Ensure that 'class_subjects' is the correct related_name
        students_count=Count('students')  # Ensure that 'students' is the correct related_name
    )

    class_data = [{
        'name': cls.class_name,
        'subjects_count': cls.subjects_count,
        'students_count': cls.students_count
    } for cls in classes_all]

    # Fetching subjects and students related to them
    subjects_all = Subject.objects.annotate(
        student_count=Count('class_subjects__class_obj__students')
    ).prefetch_related('class_subjects')

    subject_data = [{
        'name': subject.subject_name,
        'student_count': subject.student_count
    } for subject in subjects_all]

    staff_data = Staffs.objects.annotate(
    attendance_count=Count('admin__teaching_subjects__attendances', distinct=True),  # Assuming attendances are related directly to ClassSubject
    leaves_count=Count('leave_reports', distinct=True)
).annotate(
    total_attendance=F('attendance_count')  # Using F to reference the annotated count
).values(
    'admin__first_name', 'admin__last_name', 'total_attendance', 'leaves_count'
)

    # Handling context for rendering
    context = {
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "class_count": class_count,
        "staff_count": staff_count,
        "class_data": class_data,
        "subject_data": subject_data,
        "staff_data": list(staff_data),
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    if request.method != "POST":
        return render(request, "hod_template/add_staff_template.html")
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        
        context = {
                'email': email,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'address': address
            }
        
        if not password:
            messages.error(request, "Password is required!")
            return render(request, 'hod_template/add_staff_template.html', context=context)

        if CustomUser.objects.filter(email=email).exists() or CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Email or username already Exist! Log In or use another email!")
            return render(request,'hod_template/add_staff_template.html', context=context)
        
        try:
            with transaction.atomic():
                
                user = CustomUser.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        user_type=2
                        )
                
                 # Check if the user was created successfully
                if not user:
                    messages.error(request, "Failed to create user!")
                    return render(request, 'hod_template/add_staff_template.html', context=context)

                 # Check if the user already has a staff entry
                if Staffs.objects.filter(admin=user).exists():
                    messages.error(request, "Staff entry for this user already exists!")
                    return render(request, 'hod_template/add_staff_template.html', context=context)

                staff = Staffs.objects.create(admin=user, address=address)
                # Check if the staff was created successfully
                if not staff:
                    messages.error(request, "Failed to create staff entry!")
                    return render(request, 'hod_template/add_staff_template.html', context=context)
            messages.success(request, 'Staff added successfully.')
            return redirect('manage_staff')
        except Exception as e:
            messages.error(request, f"Failed to Add Staff!{e}")
            return render(request,'hod_template/add_staff_template.html', context=context)



def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('manage_staff')

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')




def add_class(request):
    # Fetching all staff who could potentially be class teachers
    staffs = CustomUser.objects.filter(user_type=2)  # Assuming '2' is the user_type for teachers
    form = ClassForm(teacher_queryset=staffs)
    return render(request, "hod_template/add_class_template.html", {'form': form})


def add_class_save(request):
    staffs = CustomUser.objects.filter(user_type=2)
    if request.method != "POST":
        messages.error(request, "Invalid request method. Please submit the form.")
        return redirect('add_class')

    form = ClassForm(request.POST, teacher_queryset=staffs)
    if form.is_valid():
        try:
            form.save()
            messages.success(request, "Class added successfully!")
            return redirect('manage_class')
        except Exception as e:
            messages.error(request, f"Failed to add class! Error: {e}")
            return render(request, 'hod_template/add_class_template.html', {'form': form})
    else:
        messages.error(request, "There were errors in your form. Please correct them.")
        return render(request, 'hod_template/add_class_template.html', {'form': form})



def manage_class(request):
    classes = Classes.objects.all().prefetch_related('subclasses')
    context = {
        "classes": classes
    }
    return render(request, 'hod_template/manage_class_template.html', context)


def edit_class(request, class_id):
    # Fetch the class and possible teachers
    single_class = get_object_or_404(Classes, id=class_id)
    class_teachers = CustomUser.objects.filter(user_type=2)
    
    if request.method == 'POST':
        class_name = request.POST.get('class')
        teacher_id = request.POST.get('class_teacher')

        try:
            # Update the class instance
            single_class.class_name = class_name
            single_class.class_teacher = get_object_or_404(CustomUser, id=teacher_id) if teacher_id else None
            single_class.save()

            messages.success(request, "Class Updated Successfully.")
            return redirect('manage_class')

        except Exception as e:
            messages.error(request, f"Failed to Update Class: {e}")
            return redirect(f'/edit_class/{class_id}')

    # Render the form with current class and teacher data
    return render(request, 'hod_template/edit_class_template.html', {
        'class': single_class,
        'class_teachers': class_teachers,
    })
    
def delete_class(request, class_id):
    single_class = Classes.objects.get(id=class_id)
    try:
        single_class.delete()
        messages.success(request, "Class Deleted Successfully.")
        return redirect('manage_class')
    except:
        messages.error(request, "Failed to Delete Class.")
        return redirect('manage_class')

def add_subclass(request, class_id):
    parent_class = get_object_or_404(Classes, id=class_id)
    teachers = CustomUser.objects.filter(user_type=2)  # Assuming '2' is the user_type for staff

    if request.method == "POST":
        subclass_code = request.POST.get('subclass_code')
        teacher_id = request.POST.get('subclass_teacher')
        teacher = CustomUser.objects.get(id=teacher_id) if teacher_id else None
        
        if SubClasses.objects.filter(subclass_code=subclass_code).exists():
            messages.error(request, f'Subclass Code; {parent_class} ({subclass_code}) already exists, please create a new subclass')
            return render(request, 'hod_template/add_subclass_template.html', {'parent_class': parent_class, 'teachers': teachers})
        try:
            new_subclass = SubClasses(
                parent_class=parent_class,
                subclass_name=parent_class.class_name,  # Automatically setting the subclass name
                subclass_code=subclass_code,
                subclass_teacher=teacher
            )
            new_subclass.save()
        except  Exception as e:
            print(e)
        return redirect('manage_subclass', class_id=parent_class.id)

    return render(request, 'hod_template/add_subclass_template.html', {
        'parent_class_id': class_id,
        'teachers': teachers
    })




def edit_subclass(request, subclass_id):
    subclass = get_object_or_404(SubClasses, id=subclass_id)
    subclass_teachers = CustomUser.objects.filter(user_type=2)
    
    if request.method == 'POST':
        subclass_code = request.POST.get('subclass_code')
        teacher_id = request.POST.get('subclass_teacher')
        teacher = get_object_or_404(CustomUser, id=teacher_id) if teacher_id else None

        # Update subclass instance. For example:
        subclass.subclass_code = subclass_code
        subclass.subclass_teacher = teacher
        
        subclass.save()
        # Redirect to the subclass management page for the parent class.
        return redirect('manage_subclass', class_id=subclass.parent_class.id)
    
    return render(request, 'hod_template/edit_subclass_template.html', {'subclass': subclass, 'subclass_teachers':subclass_teachers})

def delete_subclass(request, subclass_id):
    # Fetch the subclass
    subclass = get_object_or_404(SubClasses, id=subclass_id)
    parent_class_id = subclass.parent_class.id
    try:
        # Perform deletion
        subclass.delete()
        messages.success(request, "SubClass Deleted Successfully.")
        return redirect('manage_subclass', class_id=parent_class_id)
    except  Exception as e:
        messages.error(request, f"Failed to Delete SubClass. Because, {e}")
        return redirect('manage_subclass', class_id=parent_class_id)
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_subclass(request, class_id):
    parent_class = get_object_or_404(Classes, id=class_id)
    subclasses = parent_class.subclasses.all().select_related('subclass_teacher')
    return render(request, 'hod_template/manage_subclass_template.html', {'parent_class': parent_class, 'subclasses': subclasses})



def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    if request.method == "POST":
        form = SessionYearForm(request.POST)
        if form.is_valid():
            session_year = form.save(commit=False)
            if session_year.is_current:
                # Ensure only one session year is marked as current
                SessionYearModel.objects.update(is_current=False)
            session_year.save()
            messages.success(request, "Session Year added successfully!")
            return redirect("manage_sessions")  # Assuming you have a view to list session years
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = SessionYearForm()  # Create a new form for GET request
    return render(request, "hod_template/add_session_template.html", {'form': form})


def add_session_save(request):
    if request.method == "POST":
        form = SessionYearForm(request.POST)
        if form.is_valid():
            session_year = form.save(commit=False)
            if session_year.is_current:
                SessionYearModel.objects.update(is_current=False)
            session_year.save()
            messages.success(request, "Session Year added successfully!")
            return redirect("manage_session")
        else:
            # This will display form specific errors
            messages.error(request, form.errors.as_text())
            return redirect("add_session")
    else:
        messages.error(request, "Invalid Method")
        return redirect('add_session')


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Session Year Updated Successfully.")
            return redirect('manage_session')
        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


def add_student(request):
    if request.method == 'POST':
        form = AddStudentForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']
            profile_pic = form.cleaned_data['profile_pic']
            session_year_id = form.cleaned_data['session_year_id']
            level = form.cleaned_data['level']
            class_id = form.cleaned_data['class_id']
            subclass_id = form.cleaned_data['subclass_id']

            # Create the custom user
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            # Create the student instance
            student = Students(
                admin=user,
                gender=gender,
                profile_pic=profile_pic,
                address=address,
                class_id=class_id,
                sub_class_id=subclass_id,
                session_year_id=session_year_id
            )

            student.save()

            messages.success(request, "Student added successfully!")
            return redirect('manage_student')
        else:
            # Collect errors
            errors = {field: error for field, error in form.errors.items()}
            context = {
                'form': form,
                'errors': errors,
                'first_name': request.POST.get('first_name', ''),
                'last_name': request.POST.get('last_name', ''),
                'email': request.POST.get('email', ''),
                'username': request.POST.get('username', ''),
                'address': request.POST.get('address', ''),
                'gender': request.POST.get('gender', ''),
                'profile_pic': request.FILES.get('profile_pic', ''),
                'session_year_id': request.POST.get('session_year_id', ''),
                'level': request.POST.get('level', ''),
                'class_id': request.POST.get('class_id', ''),
                'subclass_id': request.POST.get('subclass_id', ''),
            }
            return render(request, 'hod_template/add_student_template.html', context)
    else:
        form = AddStudentForm()

    context = {
        'form': form
    }
    return render(request, 'hod_template/add_student_template.html', context)

def get_classes_or_subclasses(request):
    level_id = request.GET.get('level')
    if level_id == 'Nursery':  # Assuming you have this identifier for Nursery
        classes = Classes.objects.filter(level=level_id)
        return render(request, 'hod_template/class_options.html', {'classes': classes})
    else:
        subclasses = SubClasses.objects.filter(parent_class__level=level_id)
        return render(request, 'hod_template/subclass_options.html', {'subclasses': subclasses})

def check_subclass_existence(request, class_id):
    has_subclasses = SubClasses.objects.filter(parent_class_id=class_id).exists()
    return JsonResponse({'has_subclasses': has_subclasses})

def manage_student(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)


def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['class_id'].initial = student.class_id.id
    form.fields['gender'].initial = student.gender
    form.fields['session_year_id'].initial = student.session_year_id.id

    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    
    student_id = request.session.get('student_id')
    if student_id is None:
        return redirect('/manage_student')

    form = EditStudentForm(request.POST, request.FILES)
    if form.is_valid():
        email = form.cleaned_data['email']
        username = form.cleaned_data['username']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        address = form.cleaned_data['address']
        class_id = form.cleaned_data['class_id']
        gender = form.cleaned_data['gender']
        session_year_id = form.cleaned_data['session_year_id']

        profile_pic = form.cleaned_data.get('profile_pic')

        try:
            # Update Custom User Model
            user = CustomUser.objects.get(id=student_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            # Update Students Model
            student_model = Students.objects.get(admin=student_id)
            student_model.address = address
            student_model.class_id = get_object_or_404(Classes, id=class_id)
            student_model.session_year_id = get_object_or_404(SessionYearModel, id=session_year_id)
            student_model.gender = gender

            if profile_pic:
                student_model.profile_pic = profile_pic

            student_model.save()
            
            del request.session['student_id']

            messages.success(request, "Student Updated Successfully!")
            return redirect('manage_student')
        except Exception as e:
            messages.error(request, f"Failed to Update Student: {e}")
            return redirect(f'/edit_student/{student_id}')
    else:
        messages.error(request, "Invalid form data")
        return redirect(f'/edit_student/{student_id}')


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')


def delete_subclass_subject(request, subclass_subject_id):
    subclass_subject = get_object_or_404(SubclassSubject, id=subclass_subject_id)
    subclass_subject.delete()
    messages.success(request, "Subclass subject deleted successfully.")
    return redirect('manage_this_subject', subject_id=subclass_subject.subject.id)

def manage_this_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Retrieve all subclasses related to this subject
    subclass_subjects = SubclassSubject.objects.filter(subject=subject)
    
    if subject.subject_level == 'Nursery':
        subclass_subjects = ClassSubject.objects.filter(subject=subject)
    

    if request.method == 'POST':
        form = EditSubclassSubjectForm(request.POST)
        if form.is_valid():
            subclass_subject_id = form.cleaned_data['subclass_subject_id']
            subject_teacher = form.cleaned_data['subject_teacher']
            
            
            # Update the SubclassSubject
            subclass_subject = SubclassSubject.objects.get(id=subclass_subject_id)
            if subject.subject_level == 'Nursery':
                subclass_subject = ClassSubject.objects.get(id=subclass_subject_id)
            subclass_subject.subject_teacher = subject_teacher.admin
            subclass_subject.save()
            
            messages.success(request, 'Subject teacher updated successfully.')
            return redirect('manage_this_subject', subject_id=subject_id)
    else:
        form = EditSubclassSubjectForm()

    context = {
        'subject': subject,
        'subclass_subjects': subclass_subjects,
        'form': form,
    }

    return render(request, 'hod_template/manage_this_subject.html', context)


def add_subject(request):
    if request.method == 'POST':
        form = AddSubjectForm(request.POST)
        if form.is_valid():
            subject_name = form.cleaned_data['subject_name']
            level = form.cleaned_data['level']
            class_obj = form.cleaned_data['class_obj']
            subject_teacher = form.cleaned_data.get('subject_teacher')
            
            subject_teacher = subject_teacher.admin

            if level == 'Nursery' and not subject_teacher:
                subject_teacher = class_obj.class_teacher

            subject = Subject.objects.create(subject_name=subject_name, subject_level=level)
            ClassSubject.objects.create(subject=subject, class_obj=class_obj, subject_teacher=subject_teacher)
            subclasses = class_obj.subclasses.all()  
            for subclass in subclasses:
                SubclassSubject.objects.create(subject=subject, subclass=subclass, subject_teacher=subject_teacher)
            messages.success(request, "Subject added successfully!")
            return redirect('manage_subject')
        else:
            # If form is invalid, make sure the class_obj queryset is populated based on level
            level = request.POST.get('level')
            form.fields['class_obj'].queryset = Classes.objects.filter(level=level)
    else:
        form = AddSubjectForm()

    return render(request, 'hod_template/add_subject_template.html', {'form': form})




def manage_subject(request):
    search_query = request.GET.get('search', '')
    if search_query:
        subjects = Subject.objects.filter(subject_name__icontains=search_query)
    else:
        subjects = Subject.objects.all().prefetch_related('class_subjects__class_obj', 'class_subjects__subject_teacher', 'subclass_subjects__subclass', 'subclass_subjects__subject_teacher')

    context = {
        'subjects': subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    levels = Classes.LEVEL_CHOICES
    context = {
        "subject": subject,
        "levels": levels,
    }
    return render(request, 'hod_template/edit_subject_template.html', context)

def edit_subject_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject_name')
        subject_level = request.POST.get('subject_level')

        try:
            subject = Subject.objects.get(id=subject_id)
            subject.subject_name = subject_name
            subject.subject_level = subject_level

            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            return HttpResponseRedirect(reverse("manage_subject"))

        except Exception as e:
            messages.error(request, f"Failed to Update Subject. Error: {str(e)}")
            return HttpResponseRedirect(reverse("manage_subject", kwargs={"subject_id": subject_id}))


def delete_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')

def get_classes_for_level(request):
    level = request.GET.get('level')
    classes = Classes.objects.filter(level=level).order_by('class_name')
    class_options = [{'id': cls.id, 'name': cls.class_name} for cls in classes]
    return JsonResponse({"class_options": class_options})


def get_classes_for_levels(request):
    level = request.GET.get('level')
    classes = Classes.objects.filter(level=level)
    classes_options = [{"id": cls.id, "name": cls.class_name} for cls in classes]
    return JsonResponse({"classes_options": classes_options})

def get_subclasses_for_class(request):
    class_id = request.GET.get('class_id')
    subclasses = SubClasses.objects.filter(parent_class_id=class_id).order_by('subclass_name')
    context = {'subclasses': subclasses}
    html = render_to_string('hod_template/subclass_options.html', context)
    return HttpResponse(html)

def get_subclasses_for_classs(request):
    class_id = request.GET.get('class_id')
    subclasses = SubClasses.objects.filter(class_obj_id=class_id)
    subclasses_options = ''.join([f'<option value="{subcls.id}">{subcls.name}</option>' for subcls in subclasses])
    return JsonResponse({'subclasses_options': subclasses_options})

def get_subclasses(request, class_id):
    subclasses = SubClasses.objects.filter(parent_class_id=class_id).values('id', 'subclass_name', 'subclass_code')
    return JsonResponse(list(subclasses), safe=False)

@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    return HttpResponse(CustomUser.objects.filter(email=email).exists())


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    return HttpResponse(CustomUser.objects.filter(username=username).exists())


def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Class, class has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subject.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(class_id=subject_model.class_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')


def staff_profile(request):
    pass


def student_profile(requtest):
    pass


def manage_session_years(request):
    if request.method == 'POST':
        form = SessionYearForm(request.POST)
        if form.is_valid():
            session_year = form.save(commit=False)
            # If marked as current, reset others
            if session_year.is_current:
                SessionYearModel.objects.update(is_current=False)
            session_year.save()
            return redirect('manage_session_years')
    else:
        form = SessionYearForm()

    session_years = SessionYearModel.objects.all().order_by('-session_start_year')
    return render(request, 'hod_template/manage_session_years.html', {'form': form, 'session_years': session_years})

def set_current_session(request, year_id):
    SessionYearModel.objects.update(is_current=False)  # Reset the current flag on all years
    session_year = get_object_or_404(SessionYearModel, pk=year_id)
    session_year.is_current = True
    session_year.save()
    return redirect('manage_session_years')

def search_sessions(request):
    query = request.GET.get('table_search', '')  # Get the search keyword from the query parameter
    if query:
        session_years = SessionYearModel.objects.filter(
            # Assuming you're searching by a string representation of years
            # Update the filter according to your specific search requirements
            session_start_year__year__icontains=query) | SessionYearModel.objects.filter(session_end_year__year__icontains=query)
    else:
        session_years = SessionYearModel.objects.all()

    return render(request, 'manage_session_years.html', {'session_years': session_years})

def add_grade(request):
    session_years = SessionYearModel.objects.all()
    current_session = session_years.filter(is_current=True).first()

    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            # Set the user who updated the grades
            grade_instance = form.save(commit=False)
            grade_instance.updated_by = request.user
            grade_instance.save()
            messages.success(request, "Grade added/updated successfully!")
            return redirect('manage_grades')
        else:
            messages.error(request, "Error adding/updating grade.")
    else:
        form = GradeForm()

    return render(request, 'grades_template/add_grades.html', {
        'form': form,
        'session_years': session_years,
        'current_session': current_session
    })

def edit_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, "Grade updated successfully!")
            return redirect('manage_grades')
        else:
            messages.error(request, "Error updating grade.")
    else:
        form = GradeForm(instance=grade)
    return render(request, 'grades/edit_grade.html', {'form': form})

def delete_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    grade.delete()
    messages.success(request, "Grade deleted successfully!")
    return redirect('manage_grades')

def manage_grades(request):
    grades = Grade.objects.all()
    return render(request, 'grades/manage_grades.html', {'grades': grades})

def search_grades(request):
    query = request.GET.get('search')
    if query:
        grades = Grade.objects.filter(subject__subject_name__icontains=query)
    else:
        grades = Grade.objects.all()
    return render(request, 'grades/manage_grades.html', {'grades': grades})