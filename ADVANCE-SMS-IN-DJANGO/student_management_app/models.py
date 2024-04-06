from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver


class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField()
    session_end_year = models.DateField()
    objects = models.Manager()


class CustomUser(models.Model):
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

class Classes(models.Model):
    LEVEL_CHOICES = (
        ('Nursery', 'Nursery'),
        ('Primary', 'Primary'),
        ('Junior', 'Junior'),
    )
    id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=255)
    class_code = models.CharField(max_length=10, unique=True)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=50)
    profile_pic = models.FileField()
    address = models.TextField()
    class_id = models.ForeignKey(Classes, on_delete=models.DO_NOTHING)
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    class_id = models.ForeignKey(Classes, on_delete=models.CASCADE)


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
    test1 = models.DecimalField(max_digits=5, decimal_places=2)
    test2 = models.DecimalField(max_digits=5, decimal_places=2)
    test3 = models.DecimalField(max_digits=5, decimal_places=2)
    exam = models.DecimalField(max_digits=5, decimal_places=2)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    approved = models.BooleanField(default=False)  # Only true when the admin approves the grades

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

    @classmethod
    def is_open_for_grading(cls, term):
        try:
            deadline = cls.objects.get(term=term, is_active=True)
            return now() <= deadline.deadline
        except cls.DoesNotExist:
            return False


# Django Signals
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            AdminHOD.objects.create(admin=instance)
        elif instance.user_type == 2:
            Staffs.objects.create(admin=instance)
        elif instance.user_type == 3:
            Students.objects.create(admin=instance, class_id=Classes.objects.get(id=1), session_year_id=SessionYearModel.objects.get(id=1), address="", profile_pic="", gender="")


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.adminhod.save()
    elif instance.user_type == 2:
        instance.staffs.save()
    elif instance.user_type == 3:
        instance.students.save()