from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from gatepassapp.models import tbl_student
from adminapp.models import *

import openpyxl
from gatepassapp.serializers import *

#Login as student, tutor
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            role = serializer.validated_data['role']

            response_data = {
                "message": "Login successful",
                "role": role,
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
            }

            # Tutor Response
            if role == 'tutor':
                response_data.update({
                    "tutor_id": user.tutor_id,
                    "hod_id": user.hod.id,
                    "hod_name": user.hod.name,
                    "department_id": user.department.id,
                    "department": user.department.name,
                    'roles': user.roles,
                })

            # Student Response
            elif role == 'student':
                response_data.update({
                    "student_id": user.student_id,
                    "department_id": user.department.id,
                    "department": user.department.name,
                    "course_id": user.course.id,
                    "course": user.course.name,
                    'role': user.role,
                })

            # ⭐ Guard Response
            elif role == 'guard':
                response_data.update({
                    "guard_id": user.guard_id,
                    "gate_location": user.gate_location,
                    "gender": user.gender,
                    "phone": user.phone,
                    "photo": user.photo.url if user.photo else None,
                    "roles": user.roles,  # always 'guard'
                })

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#tutor

# tutor add student via excel

class StudentExcelUploadView(APIView):
    def post(self, request):
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({"error": "Excel file is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            # Skip header row
            for row in sheet.iter_rows(min_row=2, values_only=True):
                (
                    tutor_name, hod_name, student_name, gender, email, phone, address,
                    dob, dept_name, course_name, year, supply,
                    batch, student_id, reg_number, roll_number
                ) = row

                # Lookup related objects (case-insensitive)
                try:
                    tutor = tbl_tutor.objects.get(name__iexact=tutor_name.strip())
                except tbl_tutor.DoesNotExist:
                    return Response({"error": f"Tutor '{tutor_name}' not found"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    hod = tbl_hod.objects.get(name__iexact=hod_name.strip())
                except tbl_hod.DoesNotExist:
                    return Response({"error": f"HOD '{hod_name}' not found"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    dept = tbl_department.objects.get(name__iexact=dept_name.strip())
                except tbl_department.DoesNotExist:
                    return Response({"error": f"Department '{dept_name}' not found"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    course = tbl_course.objects.get(name__iexact=course_name.strip())
                except tbl_course.DoesNotExist:
                    return Response({"error": f"Course '{course_name}' not found"}, status=status.HTTP_400_BAD_REQUEST)

                #  Try to fetch matching image from request.FILES (image_<student_id>)
                student_image = request.FILES.get(f"image_{student_id}")

                student_data = {
                    "tutor": tutor.id,
                    "hod": hod.id,
                    "name": student_name,
                    "gender": gender,
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "dob": dob.date() if hasattr(dob, 'date') else dob,
                    "department": dept.id,
                    "course": course.id,
                    "year": year,
                    "supply": supply,
                    "batch": batch,
                    "student_id": student_id,
                    "register_number": reg_number,
                    "roll_number": roll_number,
                    "image": student_image,
                }

                serializer = StudentSerializer(data=student_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Student data uploaded successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentRequest
from .serializers import StudentRequestSerializer

class TutorStudentRequestsAPIView(APIView):
    """
    List all leave requests for students assigned to a specific tutor.
    Expects tutor_id as a URL parameter.
    """
    def get(self, request, tutor_id, *args, **kwargs):
        # Optionally, you can filter by status if needed
        status_filter = request.query_params.get("status")

        requests = StudentRequest.objects.filter(tutor_id=tutor_id).order_by("-created_at")

        if status_filter:
            requests = requests.filter(status=status_filter)

        serializer = StudentRequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentRequest
from .serializers import StudentRequestSerializer
#tutor approve a student leave request
class TutorApproveRequestAPIView(APIView):
    """
    Tutor approves a student leave request.
    """
    def post(self, request, tutor_id, request_id, *args, **kwargs):
        try:
            student_request = StudentRequest.objects.get(id=request_id, tutor_id=tutor_id)
        except StudentRequest.DoesNotExist:
            return Response({"detail": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        if student_request.category == "Urgent":
            return Response({"detail": "Tutor approval not required for urgent requests."}, status=status.HTTP_400_BAD_REQUEST)

        student_request.status = "Tutor Approved"
        student_request.forwarded_to_hod = True
        student_request.save()

        serializer = StudentRequestSerializer(student_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
#tutor reject a student leave request

class TutorRejectRequestAPIView(APIView):
    """
    Tutor rejects a student leave request.
    """
    def post(self, request, tutor_id, request_id, *args, **kwargs):
        try:
            student_request = StudentRequest.objects.get(id=request_id, tutor_id=tutor_id)
        except StudentRequest.DoesNotExist:
            return Response({"detail": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        if student_request.category == "Urgent":
            return Response({"detail": "Tutor cannot reject urgent requests."}, status=status.HTTP_400_BAD_REQUEST)

        student_request.status = "Rejected by Tutor"
        student_request.save()

        serializer = StudentRequestSerializer(student_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TutorViewJobsAPIView(APIView):
    """
    List all jobs for tutors.
    """
    def get(self, request, *args, **kwargs):
        jobs = Tbl_Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#view for list all job applications submitted by students under a given tutor.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import JobApplication, tbl_tutor
from .serializers import JobApplicationSerializer

class TutorViewAppliedStudentsAPIView(APIView):
    """
    List all job applications submitted by students under a given tutor.
    """

    def get(self, request, tutor_id, *args, **kwargs):
        try:
            tutor = tbl_tutor.objects.get(id=tutor_id)
        except tbl_tutor.DoesNotExist:
            return Response({"error": "Tutor not found"}, status=status.HTTP_404_NOT_FOUND)

        applications = JobApplication.objects.filter(student__tutor=tutor).order_by("-applied_at")
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import JobApplication

class TutorApproveApplicationAPIView(APIView):
    def post(self, request, tutor_id, application_id, *args, **kwargs):
        # Validate tutor
        try:
            tutor = tbl_tutor.objects.get(id=tutor_id)
        except tbl_tutor.DoesNotExist:
            return Response({"error": "Tutor not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate application
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

        # OPTIONAL: restrict tutor so they can only approve their own students
        if application.student.tutor.id != tutor.id:
            return Response(
                {"error": "Tutor is not assigned to this student"},
                status=status.HTTP_403_FORBIDDEN
            )

        application.status = "Approved"
        application.save()

        return Response(
            {"message": "Application approved successfully"},
            status=status.HTTP_200_OK
        )

class TutorRejectApplicationAPIView(APIView):
    def post(self, request, tutor_id, application_id, *args, **kwargs):
        # Validate tutor
        try:
            tutor = tbl_tutor.objects.get(id=tutor_id)
        except tbl_tutor.DoesNotExist:
            return Response({"error": "Tutor not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate application
        try:
            application = JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

        # OPTIONAL: restrict tutor so they can only reject their own students
        if application.student.tutor.id != tutor.id:
            return Response(
                {"error": "Tutor is not assigned to this student"},
                status=status.HTTP_403_FORBIDDEN
            )

        application.status = "Rejected"
        application.save()

        return Response(
            {"message": "Application rejected successfully"},
            status=status.HTTP_200_OK
        )


class TutorviewCompaniesView(APIView):
    """
    List all companies.
    """
    def get(self, request, *args, **kwargs):
        companies = Company.objects.all().order_by("name")
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TutorViewJobsByCompanyView(APIView):
    """
    List all jobs for a specific company.
    """
    def get(self, request, company_id, *args, **kwargs):
        jobs = Tbl_Job.objects.filter(company_id=company_id)
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MarkAttendance
from .serializers import MarkAttendanceSerializer
from gatepassapp.models import tbl_student

class TutorViewAttendanceAPIView(APIView):
    """
    Tutor views attendance of all students assigned to them
    """

    def get(self, request, tutor_id):
        # Get all students under the tutor
        students = tbl_student.objects.filter(tutor_id=tutor_id)

        # Get attendance for these students
        attendance_records = MarkAttendance.objects.filter(
            student__in=students
        ).order_by('-date', '-time')

        serializer = MarkAttendanceSerializer(attendance_records, many=True)

        return Response({
            "tutor_id": tutor_id,
            "total_records": attendance_records.count(),
            "attendance": serializer.data
        }, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MarkAttendance

class UpdateAttendanceStatusAPIView(APIView):
    """
    Tutor updates attendance status:
    {
        "status": "Present"
    }
    """

    def patch(self, request, attendance_id):
        try:
            attendance = MarkAttendance.objects.get(id=attendance_id)
        except MarkAttendance.DoesNotExist:
            return Response(
                {"error": "Attendance record not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")

        # Validate status
        allowed_statuses = ["Present", "Absent", "Not Marked"]
        if new_status not in allowed_statuses:
            return Response(
                {"error": "Invalid status. Allowed: Present, Absent, Not Marked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.status = new_status
        attendance.save()

        return Response(
            {"message": "Attendance status updated successfully", "new_status": new_status},
            status=status.HTTP_200_OK
        )



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .models import MarkAttendance
from .serializers import MarkAttendanceSerializer
from gatepassapp.models import tbl_student

class TutorTodayAttendanceAPIView(APIView):
    """
    Tutor views today's attendance for all assigned students
    """

    def get(self, request, tutor_id):
        today = now().date()

        # Get students under this tutor
        students = tbl_student.objects.filter(tutor_id=tutor_id)

        # Filter today's attendance
        attendance_records = MarkAttendance.objects.filter(
            student__in=students,
            date=today
        ).order_by('-time')

        serializer = MarkAttendanceSerializer(attendance_records, many=True)

        return Response({
            "tutor_id": tutor_id,
            "date": today.strftime("%d/%m/%Y"),
            "total_records": attendance_records.count(),
            "attendance": serializer.data
        }, status=status.HTTP_200_OK)


#today
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MarkAttendance

class UpdateAttendanceStatusAPIView(APIView):
    """
    Update attendance status:
    {
        "status": "Present"
    }
    """

    def patch(self, request, attendance_id):
        try:
            attendance = MarkAttendance.objects.get(id=attendance_id)
        except MarkAttendance.DoesNotExist:
            return Response(
                {"error": "Attendance record not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")

        allowed_status = ["Present", "Absent", "Not Marked"]

        # Validate incoming status
        if new_status not in allowed_status:
            return Response(
                {"error": "Invalid status. Allowed: Present, Absent, Not Marked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status
        attendance.status = new_status
        attendance.save()

        return Response(
            {
                "message": "Attendance status updated successfully",
                "attendance_id": attendance_id,
                "new_status": new_status
            },
            status=status.HTTP_200_OK
        )


















#Student
#  Student creates a leave request
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import StudentRequest
from .serializers import StudentRequestSerializer

class StudentRequestViewSet(viewsets.ModelViewSet):
    queryset = StudentRequest.objects.all()
    serializer_class = StudentRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            category = serializer.validated_data.get("category")
            
            # Urgent requests bypass Tutor
            if category == "Urgent":
                serializer.save(status="Pending", forwarded_to_hod=True)
            else:
                serializer.save(status="Pending")  # Wait for Tutor approval
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import tbl_student
from .serializers import StudentProfileSerializer

#View Student Profile
class StudentProfileView(APIView):
    def get(self, request, student_id):
        try:
            student = tbl_student.objects.get(id=student_id)
            serializer = StudentProfileSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except tbl_student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)


#Update Student Profile
class UpdateStudentProfileView(APIView):
    def put(self, request, student_id):
        try:
            student = tbl_student.objects.get(id=student_id)
        except tbl_student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentProfileSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, student_id):
        try:
            student = tbl_student.objects.get(id=student_id)
        except tbl_student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentProfileSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import tbl_student, MarkAttendance
from .serializers import MarkAttendanceSerializer
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from django.utils import timezone
import os
import numpy as np
import face_recognition
import cv2

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import tbl_student, MarkAttendance
from .serializers import MarkAttendanceSerializer


class AttendanceAPIView(APIView):
    """
    POST an image to /userapp/api/mark-attendance/

    Required fields:
    - student_id
    - image

    The API verifies whether the uploaded face matches the
    student's profile image before marking attendance.
    """

    def post(self, request, format=None):

        # 1️⃣ Get student_id
        student_id_from_request = request.data.get('student_id')

        if not student_id_from_request:
            return Response(
                {"error": "Student ID is missing from the request."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2️⃣ Find student
        try:
            student = tbl_student.objects.get(student_id=student_id_from_request)
        except tbl_student.DoesNotExist:
            return Response(
                {"error": "Student not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3️⃣ Check if student profile image exists
        if not student.image:
            return Response(
                {"error": "No profile image found for this student."},
                status=status.HTTP_400_BAD_REQUEST
            )

        img_path = student.image.path

        if not os.path.exists(img_path):
            return Response(
                {"error": "Student profile image file not found on server."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 4️⃣ Load student profile image
        try:
            known_image = face_recognition.load_image_file(img_path)
            known_encodings = face_recognition.face_encodings(known_image)
        except Exception as e:
            return Response(
                {"error": f"Error processing student image: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not known_encodings:
            return Response(
                {"error": "No face detected in student's profile image."},
                status=status.HTTP_400_BAD_REQUEST
            )

        known_encoding = known_encodings[0]

        # 5️⃣ Get uploaded image
        file_obj = request.FILES.get('image')

        if not file_obj:
            return Response(
                {"error": "No image uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            file_bytes = np.frombuffer(file_obj.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        except Exception as e:
            return Response(
                {"error": f"Invalid image format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if img is None:
            return Response(
                {"error": "Invalid image file."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert BGR → RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Ensure correct format
        img_rgb = np.ascontiguousarray(img_rgb)

        # 6️⃣ Detect faces
        face_locations = face_recognition.face_locations(img_rgb)
        face_encodings = face_recognition.face_encodings(img_rgb, face_locations)

        if not face_encodings:
            return Response(
                {"message": "No faces detected in the uploaded image. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 7️⃣ Compare faces
        match_found = False

        for face_encoding in face_encodings:

            matches = face_recognition.compare_faces([known_encoding], face_encoding)
            face_distance = face_recognition.face_distance([known_encoding], face_encoding)

            if matches[0]:

                # Mark attendance
                attendance_record, created = MarkAttendance.objects.get_or_create(
                    student=student,
                    date=timezone.now().date(),
                    defaults={"status": "Present"}
                )

                # If already exists update status
                if not created and attendance_record.status != "Present":
                    attendance_record.status = "Present"
                    attendance_record.save()

                match_found = True
                break

        # 8️⃣ Response
        if match_found:

            attendance_record = MarkAttendance.objects.get(
                student=student,
                date=timezone.now().date()
            )

            serializer = MarkAttendanceSerializer(attendance_record)

            return Response(
                {
                    "message": "Face detected and attendance marked successfully!",
                    "attendance": serializer.data
                },
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {
                    "message": "Face detected, but it does not match your profile picture. Please try again."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import JobApplication
from .serializers import JobApplicationSerializer
# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import JobApplication
from .serializers import JobApplicationSerializer

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(status="Pending")  # Always set status to Pending on apply
            return Response(
                {"message": "Job application submitted successfully!", "application": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentRequest
from .serializers import StudentRequestSerializer

class StudentRequestsByStudentAPIView(APIView):
    """
    List all leave requests for a specific student using student_id in URL
    """
    def get(self, request, student_id, *args, **kwargs):
        requests = StudentRequest.objects.filter(student_id=student_id).order_by("-created_at")
        serializer = StudentRequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import JobApplication
from .serializers import JobApplicationSerializer

class StudentJobApplicationsAPIView(APIView):
    """
    View all job applications submitted by a specific student
    """

    def get(self, request, student_id, *args, **kwargs):
        applications = JobApplication.objects.filter(student_id=student_id).order_by("-applied_at")

        serializer = JobApplicationSerializer(applications, many=True)

        return Response({
            "student_id": student_id,
            "applications": serializer.data
        }, status=status.HTTP_200_OK)




class TutorViewStudentsAPIView(APIView):
    """
    Tutor views all students assigned to them
    """

    def get(self, request, tutor_id, *args, **kwargs):
        students = tbl_student.objects.filter(tutor_id=tutor_id).order_by("name")
        serializer = StudentProfileSerializer(students, many=True)
        return Response({
            "tutor_id": tutor_id,
            "total_students": students.count(),
            "students": serializer.data
        }, status=status.HTTP_200_OK)



















#Gaurd
















#for fetch adminapp models
#api for view course by department
from adminapp.models import *

class ViewCoursesByDepartment(APIView):
    def get(self, request, department_id):
        try:
            department = tbl_department.objects.get(id=department_id)
            courses = tbl_course.objects.filter(department=department)
            course_data = [{
                "course_id": course.id,
                "course_name": course.name,
                "department_id": department.id,
                "department_name": department.name
                } for course in courses]
            return Response(course_data, status=status.HTTP_200_OK)
        except tbl_department.DoesNotExist:
            return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#api for view all departments
class ViewDepartments(APIView):
    def get(self, request):
        try:
            departments = tbl_department.objects.all()
            department_data = [{"department_id": dept.id, "department_name": dept.name} for dept in departments]
            return Response(department_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#api for view all courses
class ViewCourses(APIView):
    def get(self, request):
        try:
            courses = tbl_course.objects.all()
            course_data = [{"course_id": course.id, "course_name": course.name} for course in courses]
            return Response(course_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

from adminapp.models import Tbl_Job,Company
from .serializers import JobSerializer,CompanySerializer
class ViewJobs(APIView):
    def get(self, request):
        try:
            jobs = Tbl_Job.objects.all()
            serializer = JobSerializer(jobs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ViewCompanies(APIView):
    def get(self, request):
        try:
            companies = Company.objects.all()
            serializer = CompanySerializer(companies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminapp.models import Tbl_Job, Company
from .serializers import JobSerializer, CompanySerializer

class Job_View_by_CompanyView(APIView):
    def get(self, request, company_id):
        try:
            # get the company
            company = Company.objects.get(id=company_id)

            # filter jobs belonging to that company
            jobs = Tbl_Job.objects.filter(company=company)

            job_serializer = JobSerializer(jobs, many=True)
            company_serializer = CompanySerializer(company)

            return Response({
                "company": company_serializer.data,
                "jobs": job_serializer.data
            }, status=status.HTTP_200_OK)

        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class JobDetailView(APIView):
    def get(self, request, job_id):
        try:
            job = Tbl_Job.objects.get(id=job_id)
            company = job.company  

            job_data = {
                "job_id": job.id,
                "title": job.title,
                "description": job.description,
                "place": job.place,   # corrected field (not location)
                "date": job.date,     # corrected field (not posted_date)
                "salary": str(job.salary),
                "vacancy": job.vacancy,
                "job_type": job.job_type,
                "department": job.department_id.name,
                "responsibilities": job.responsibilities,
                "qualifications": job.qualifications,
                "company_id": company.id,
                "company_name": company.name,
                "company_logo": company.logo.url if company.logo else None,
            }

            return Response(job_data, status=status.HTTP_200_OK)

        except Tbl_Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import tbl_student
from .serializers import StudentSerializer

class StudentDetailView(APIView):
    def get(self, request, pk):
        try:
            student = tbl_student.objects.get(id=pk)   # <-- primary key lookup
        except tbl_student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)









#GUARD PART
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentRequest
from .serializers import StudentRequestSerializer

class GuardApprovedLeaveRequestsAPIView(APIView):
    """
    Guard can view all leave requests approved by HOD.
    """

    def get(self, request, *args, **kwargs):
        approved_requests = StudentRequest.objects.filter(
            status="HOD Approved"
        ).order_by("-created_at")

        serializer = StudentRequestSerializer(approved_requests, many=True)

        return Response({
            "count": approved_requests.count(),
            "approved_leaves": serializer.data
        }, status=status.HTTP_200_OK)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentRequest
class GuardUpdateLeaveStatusAPIView(APIView):
    """
    Guard updates leave status using JSON:
    {
        "status": "Leaved"
    }
    OR
    {
        "status": "Not Leaved"
    }
    """

    def patch(self, request, request_id):
        try:
            leave_request = StudentRequest.objects.get(id=request_id)
        except StudentRequest.DoesNotExist:
            return Response(
                {"error": "Leave request not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")

        # Only allow Leaved or Not Leaved
        if new_status not in ["Leaved", "Not Leaved"]:
            return Response(
                {"error": "Invalid status. Allowed: 'Leaved', 'Not Leaved'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Only HOD Approved requests can be updated by guard
        if leave_request.status != "HOD Approved":
            return Response(
                {"error": "Only HOD Approved requests can be updated by guard"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update record
        leave_request.status = new_status
        leave_request.is_leaved = (new_status == "Leaved")
        leave_request.save()

        return Response(
            {"message": f"Leave status updated to '{new_status}' successfully"},
            status=status.HTTP_200_OK
        )
