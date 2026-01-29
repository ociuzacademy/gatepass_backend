from rest_framework import serializers
from adminapp.models import tbl_hod,tbl_tutor,GateGuard
from .models import tbl_student
#serializer for login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    login_id = serializers.CharField()  # tutor_id / hod_id / student_id / guard_id
    role = serializers.ChoiceField(choices=[
        ('tutor', 'Tutor'), 
        ('student', 'Student'),
        ('guard', 'Guard')
    ])

    def validate(self, data):
        email = data.get('email')
        login_id = data.get('login_id')
        role = data.get('role')

        # Tutor Login
        if role == 'tutor':
            try:
                tutor = tbl_tutor.objects.get(email=email, tutor_id=login_id)
            except tbl_tutor.DoesNotExist:
                raise serializers.ValidationError("Invalid Tutor credentials.")
            data['user'] = tutor

        # Student Login
        elif role == 'student':
            try:
                student = tbl_student.objects.get(email=email, student_id=login_id)
            except tbl_student.DoesNotExist:
                raise serializers.ValidationError("Invalid Student credentials.")
            data['user'] = student

        # Guard Login
        elif role == 'guard':
            try:
                guard = GateGuard.objects.get(email=email, guard_id=login_id)
            except GateGuard.DoesNotExist:
                raise serializers.ValidationError("Invalid Guard credentials.")
            data['user'] = guard

        data['role'] = role
        return data

#serializer for tutor
from adminapp.models import tbl_tutor
class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_tutor
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        return rep
    

#serializer for student
class StudentSerializer(serializers.ModelSerializer):
    tutor_name = serializers.CharField(source='tutor.name', read_only=True)
    hod_name = serializers.CharField(source='hod.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = tbl_student
        fields = [
            'id', 'name', 'gender', 'email', 'phone', 'address', 'dob', 'year',
            'supply', 'batch', 'student_id', 'register_number', 'roll_number',
            'role', 'image',
            'tutor', 'hod', 'department', 'course',

            # extra fields
            'tutor_name', 'hod_name', 'department_name', 'course_name'
        ]


#serializer for student request for a leave
from rest_framework import serializers
from .models import StudentRequest

from rest_framework import serializers
from .models import StudentRequest
# from datetime import datetime

class StudentRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    tutor_name = serializers.CharField(source="tutor.name", read_only=True)
    hod_name = serializers.CharField(source="hod.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)

    class Meta:
        model = StudentRequest
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Format request_date -> dd/mm/yyyy
        if instance.request_date:
            rep['request_date'] = instance.request_date.strftime("%d/%m/%Y")
        else:
            rep['request_date'] = None

        # Format created_at -> dd/mm/yyyy
        if instance.created_at:
            rep['created_at'] = instance.created_at.strftime("%d/%m/%Y %H:%M")
        else:
            rep['created_at'] = None

        # Add QR code URL if exists
        if instance.qr_code:
            rep['qr_code'] = instance.qr_code.url

        return rep

#serializer for student profile and update profile
from rest_framework import serializers
from .models import tbl_student,Attendance

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_student
        fields = '__all__'



#code for view departments and courses
from adminapp.models import tbl_department
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_department
        fields = '__all__'

from adminapp.models import tbl_course
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_course
        fields = '__all__'

# serializers.py
#serialzer for mark attendance
from rest_framework import serializers
from .models import MarkAttendance
class MarkAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)  # Custom ID from tbl_student

    class Meta:
        model = MarkAttendance
        fields = ['id', 'student', 'student_id', 'student_name', 'date', 'time']

#serialzer for jobs and company
from adminapp.models import Tbl_Job,Company
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__' 


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tbl_Job
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Format date -> dd/mm/yyyy
        if instance.date:
            rep['date'] = instance.date.strftime("%d/%m/%Y")
        else:
            rep['date'] = None

        return rep   # ⭐ You MUST return this!












# serializers.py
from rest_framework import serializers
from .models import JobApplication

class JobApplicationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company = serializers.CharField(source='job.company.name', read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'student', 'student_name', 'job', 'job_title', 'company', 'resume', 'status', 'applied_at']
        read_only_fields = ['company', 'status', 'applied_at']  # status is controlled by system
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.resume:
            rep['resume'] = instance.resume.url
        return rep
        