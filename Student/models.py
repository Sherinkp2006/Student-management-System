from django.db import models

# Create your models here.
class Student(models.Model):
    rollno = models.CharField(unique=True)
    student_name = models.CharField(max_length=100)
    year = models.IntegerField()
    dept = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return self.student_name
