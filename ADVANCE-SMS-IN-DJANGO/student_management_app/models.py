from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

import logging

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    user_type_data = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)


class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=50)
    profile_pic = models.FileField()
    address = models.TextField()
    class_id = models.ForeignKey('Classes', on_delete=models.DO_NOTHING)
    session_year_id = models.ForeignKey("SessionYearModel", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField()
    session_end_year = models.DateField()
    objects = models.Manager()
    description = models.CharField(max_length=255, null=True, blank=True)  # Optional description

    def __str__(self):
        return f"{self.session_start_year}-{self.session_end_year}"


class Classes(models.Model):
    LEVEL_CHOICES = (
        ('Nursery', 'Nursery'),
        ('Primary', 'Primary'),
        ('Junior', 'Junior'),
    )
    id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=255)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    class_teacher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_teacher')
    created_at = models.DateTimeField(auto_now_add=True, null = True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f" {self.class_name}"

# models.py

class SubClasses(models.Model):
    parent_class = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='subclasses')
    subclass_name = models.CharField(max_length=255)
    subclass_code = models.CharField(max_length=10)
    subclass_teacher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='subclass_teacher')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('subclass_name', 'subclass_code')

    def __str__(self):
        return f"{self.subclass_name} ({self.subclass_code})"



class Subject(models.Model):
    subject_name = models.CharField(max_length=255)
    class_id = models.ForeignKey(Classes, related_name='subjects', on_delete=models.CASCADE, null=True, blank=True)
    subclass_id = models.ForeignKey(SubClasses, related_name='subjects', on_delete=models.CASCADE, null=True, blank=True)
    staff_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank = True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank = True)



class Grade(models.Model):
    TERM_CHOICES = (
        (1, 'Term 1'),
        (2, 'Term 2'),
        (3, 'Term 3'),
    )
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.IntegerField(choices=TERM_CHOICES)
    session_year = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    test1 = models.DecimalField(max_digits=5, decimal_places=2, null= True, blank = True)
    test2 = models.DecimalField(max_digits=5, decimal_places=2, null= True, blank = True)
    test3 = models.DecimalField(max_digits=5, decimal_places=2, null= True, blank = True)
    exam = models.DecimalField(max_digits=5, decimal_places=2, null= True, blank = True)
    total_grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank = True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    approved = models.BooleanField(default=False)  # Only true when the admin approves the grades

    def clean(self):
        current_date = timezone.now().date()
        if self.session_year and self.subject and current_date > self.subject.deadline.deadline:
            raise ValidationError("Grades cannot be entered past the deadline.")

    def save(self, *args, **kwargs):
        self.final_grade = self.calculate_final_grade()
        super(Grade, self).save(*args, **kwargs)

    def calculate_final_grade(self):
        # Implement the logic for final grade calculation here
        return (self.test1 + self.test2 + self.test3 + self.exam)


class GradeDeadline(models.Model):
    term = models.IntegerField(choices=Grade.TERM_CHOICES)
    deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def clean(self):
        if self.deadline < timezone.now().date():
            raise ValidationError("Deadline must be set in the future.")

    @classmethod
    def is_open_for_grading(cls, term):
        try:
            deadline = cls.objects.get(term=term, is_active=True)
            return now() <= deadline.deadline
        except cls.DoesNotExist:
            return False

class StudentResult(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    subject_exam_marks = models.FloatField(default=0)
    subject_assignment_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Attendance(models.Model):
    # Subject Attendance
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class AttendanceReport(models.Model):
    # Individual Student Attendance
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    stafff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


# Django Signals
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user_type == 1:
                AdminHOD.objects.create(admin=instance)
            elif instance.user_type == 2:
                Staffs.objects.create(admin=instance)
            elif instance.user_type == 3:
                default_class = Classes.objects.first()  # Assumes at least one class exists
                default_session_year = SessionYearModel.objects.first()  # Assumes at least one session year exists

                if not default_class or not default_session_year:
                    raise ObjectDoesNotExist("Default Class or SessionYearModel does not exist.")

                Students.objects.create(
                    admin=instance,
                    class_id=default_class,
                    session_year_id=default_session_year,
                    address="", profile_pic="", gender=""
                )
        except ObjectDoesNotExist as e:
            logger.error(f"Failed to create user profile for {instance.username}: {e}")
            # Here you can also add additional actions like sending an email notification.
    else:
        if instance.user_type == 1:
            instance.adminhod.save()
        elif instance.user_type == 2:
            instance.staffs.save()
        elif instance.user_type == 3:
            instance.students.save()
