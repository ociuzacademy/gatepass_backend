from django.db import models
from datetime import datetime, date, time

def get_current_ist_date():
    return date.today()

def get_current_ist_time():
    return datetime.now().time()

def get_current_ist_datetime():
    return datetime.now()


#model for student
class tbl_student(models.Model):
    tutor = models.ForeignKey('adminapp.tbl_tutor', on_delete=models.CASCADE)
    hod = models.ForeignKey('adminapp.tbl_hod', on_delete=models.CASCADE)
    department = models.ForeignKey('adminapp.tbl_department', on_delete=models.CASCADE)
    course = models.ForeignKey('adminapp.tbl_course', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField()
    year = models.IntegerField(blank=True, null=True)
    supply = models.CharField(max_length=100, blank=True, null=True)
    batch = models.CharField(max_length=100, blank=True, null=True)
    student_id = models.CharField(max_length=50, unique=True)
    register_number = models.CharField(max_length=50)
    roll_number = models.CharField(max_length=50)
    role = models.CharField(max_length=100, default='student')
    image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    

    def __str__(self):
        return self.name
    
#model for student request for a leave
from django.db import models
from adminapp.models import tbl_tutor, tbl_hod, tbl_department, tbl_course
from gatepassapp.models import tbl_student

class StudentRequest(models.Model):
    CATEGORY_CHOICES = [
        ("Urgent", "Urgent"),
        ("Not Urgent", "Not Urgent"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Rejected by Tutor", "Rejected by Tutor"),
        ("Tutor Approved", "Tutor Approved"),
        ("HOD Rejected", "HOD Rejected"),
        ("HOD Approved", "HOD Approved"),
        ("Leaved", "Leaved"),
        ("Not Leaved", "Not Leaved"),
    ]

    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE, related_name="leave_requests")
    tutor = models.ForeignKey(tbl_tutor, on_delete=models.CASCADE, related_name="student_requests", null=True, blank=True)
    hod = models.ForeignKey(tbl_hod, on_delete=models.CASCADE, related_name="student_requests")
    department = models.ForeignKey(tbl_department, on_delete=models.CASCADE)
    course = models.ForeignKey(tbl_course, on_delete=models.CASCADE)
    request_date = models.DateField(null=True, blank=True)
    request_time = models.TimeField(null=True, blank=True)
    reason = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    forwarded_to_hod = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to="qr_codes/", null=True, blank=True)
    is_leaved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=get_current_ist_datetime)


    def __str__(self):
        return f"{self.student.name} - {self.reason[:20]} ({self.status})"


#model for mark attendance
from django.db import models
class MarkAttendance(models.Model):
    student = models.ForeignKey('tbl_student', on_delete=models.CASCADE)
    date = models.DateField(default=get_current_ist_date)
    time = models.TimeField(default=get_current_ist_time)

    status = models.CharField(
        max_length=15,
        choices=[
            ('Present', 'Present'),
            ('Absent', 'Absent'),
            ('Not Marked', 'Not Marked')  # 👈 new choice
        ],
        default='Not Marked'  # 👈 default before detection
    )

    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.status})"



#model for apply job
class JobApplication(models.Model):
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    job = models.ForeignKey('adminapp.Tbl_Job', on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Company Reviewed', 'Company Reviewed'),
        ('Company Approved', 'Company Approved'),
        ('Company Rejected', 'Company Rejected'),
    ]
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending'
    )
    applied_at = models.DateTimeField(default=get_current_ist_datetime)


    def __str__(self):
        return f"{self.student.name} applied for {self.job.title}"




class Attendance(models.Model):
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    date = models.DateField(default=get_current_ist_date)
    time = models.TimeField(default=get_current_ist_time)


    class Meta:
        unique_together = ('student', 'date')  # Prevent duplicate attendance per day

    def __str__(self):
        return f"{self.student.name} - {self.date}"