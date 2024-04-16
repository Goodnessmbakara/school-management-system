from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from .forms import ClassForm, SubClassForm
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_control
from django.shortcuts import get_object_or_404

from student_management_app.models import CustomUser, Staffs, Classes,SubClasses, Subject, Students, SessionYearModel, FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport
from .forms import AddStudentForm, EditStudentForm


def admin_home(request):
    all_student_count = Students.objects.all().count()
    subject_count = Subject.objects.all().count()
    class_count = Classes.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Class
    classes_all = Classes.objects.all()
    class_name_list = []
    subject_count_list = []
    student_count_list_in_class = []

    for single_class in classes_all:
        subjects = Subject.objects.filter(class_id=single_class.id).count()
        students = Students.objects.filter(class_id=single_class.id).count()
        class_name_list.append(single_class.class_name)
        subject_count_list.append(subjects)
        student_count_list_in_class.append(students)

    subject_all = Subject.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        single_class = Classes.objects.get(id=subject.classs)
        student_count = Students.objects.filter(class_id=single_class.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        subject_ids = Subject.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.admin.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(student.admin.first_name)


    context={
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "class_count": class_count,
        "staff_count": staff_count,
        "class_name_list": class_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_class": student_count_list_in_class,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')



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
            return redirect('/edit_staff/'+staff_id)

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
    single_class = Classes.objects.get(id=class_id)
    context = {
        "single_class": single_class,
        "id": class_id
    }
    return render(request, 'hod_template/edit_class_template.html', context)


def edit_class_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        class_id = request.POST.get('class_id')
        class_name = request.POST.get('class')

        try:
            single_class = Classes.objects.get(id=class_id)
            single_class.class_name = class_name
            single_class.save()

            messages.success(request, "Class Updated Successfully.")
            return redirect('/edit_class/'+class_id)

        except:
            messages.error(request, "Failed to Update Class.")
            return redirect('/edit_class/'+class_id)


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

        new_subclass = SubClasses(
            parent_class=parent_class,
            subclass_name=parent_class.class_name,  # Automatically setting the subclass name
            subclass_code=subclass_code,
            subclass_teacher=teacher
        )
        new_subclass.save()
        return redirect('manage_subclass', class_id=parent_class.id)

    return render(request, 'hod_template/add_subclass_template.html', {
        'parent_class_id': class_id,
        'teachers': teachers
    })




def edit_subclass(request, subclass_id):
    subclass = get_object_or_404(SubClasses, id=subclass_id)
    
    if request.method == 'POST':
        subclass_code = request.POST.get('subclass_code')
        # Update subclass instance. For example:
        subclass.subclass_code = subclass_code
        subclass.save()
        # Redirect to the subclass management page for the parent class.
        return redirect('manage_subclass', class_id=subclass.parent_class.id)
    
    return render(request, 'hod_template/edit_subclass_template.html', {'subclass': subclass})

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
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_class')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Session Year added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Session Year")
            return redirect("add_session")


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
            return redirect('/edit_session/'+session_id)
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
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)




def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            session_year_id = form.cleaned_data['session_year_id']
            class_id = form.cleaned_data['class_id']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None


            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                user.students.address = address

                class_obj = Classes.objects.get(id=class_id)
                user.students.class_id = class_obj

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                user.students.session_year_id = session_year_obj

                user.students.gender = gender
                user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
            except:
                messages.error(request, "Failed to Add Student!")
                return redirect('add_student')
        else:
            return redirect('add_student')


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
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
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

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address

                single_class = Classes.objects.get(id=class_id)
                student_model.class_id = single_class

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                student_model.session_year_id = session_year_obj

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                messages.success(request, "Student Updated Successfully!")
                return redirect('/edit_student/'+student_id)
            except:
                messages.success(request, "Failed to Uupdate Student.")
                return redirect('/edit_student/'+student_id)
        else:
            return redirect('/edit_student/'+student_id)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')


def add_subject(request):
    classes = Classes.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "classes": classes,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)




def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')

    subject_name = request.POST.get('subject')
    class_id = request.POST.get('class')
    single_class = get_object_or_404(Classes, pk=class_id)
    subclass_id = request.POST.get('subclass', None)
    staff_id = request.POST.get('staff')
    staff = get_object_or_404(CustomUser, pk=staff_id)

    # Check for Nursery level and subclass assignment attempt
    if single_class.level == 'Nursery' and subclass_id:
        messages.error(request, "Nursery classes cannot have subclasses.")
        return redirect('add_subject')

    # Create the subject for either class or subclass
    if subclass_id:
        subclass = get_object_or_404(SubClasses, pk=subclass_id)
        subject = Subject(subject_name=subject_name, subclass_id=subclass, staff_id=staff)
    else:
        subject = Subject(subject_name=subject_name, class_id=single_class, staff_id=staff)

    subject.save()
    messages.success(request, "Subject added successfully.")
    return redirect('add_subject')  # Redirect after successful save


def manage_subject(request):
    search_query = request.GET.get('search', '')
    if search_query:
        subjects = Subject.objects.filter(subject_name__icontains=search_query)
    else:
        subjects = Subject.objects.all()

    context = {
        'subjects': subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    classes = Classes.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "Classes": classes,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        class_id = request.POST.get('class')
        staff_id = request.POST.get('staff')

        try:
            subject = Subject.objects.get(id=subject_id)
            subject.subject_name = subject_name

            single_class = Classes.objects.get(id=class_id)
            subject.class_id = single_class

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff

            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



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
    context = {'classes': classes}
    html = render_to_string('hod_template/class_options.html', context)
    return HttpResponse(html)

def get_subclasses_for_class(request, class_id):
    subclasses = SubClasses.objects.filter(parent_class_id=class_id).order_by('subclass_name')
    context = {'subclasses': subclasses}
    html = render_to_string('hod_template/subclass_options.html', context)
    return HttpResponse(html)

def get_subclasses(request, class_id):
    subclasses = SubClasses.objects.filter(parent_class_id=class_id).values('id', 'subclass_name', 'subclass_code')
    if subclasses:
        return JsonResponse(list(subclasses), safe=False)
    else:
        return JsonResponse([], safe=False)

@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



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



