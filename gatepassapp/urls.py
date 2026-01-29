# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


from .views import *
schema_view = get_schema_view(
   openapi.Info(
      title="Gatepass App API",
      default_version='v1',
      description="API documentation for your project",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Define the router and register the viewset
router = DefaultRouter()

#router for manage student requests
router.register(r'student-requests', StudentRequestViewSet, basename='studentrequest')
router.register(r'job-applications', JobApplicationViewSet, basename='job-application')


urlpatterns = [
   path('', include(router.urls)),  # Now /api/register/ will work
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


   #url for login
   path('login/', LoginView.as_view(), name='login'),
   #url for student upload via an excel
   path('student/upload/', StudentExcelUploadView.as_view(), name='upload_students'),
   
   #url student view and update their profile
   path("student/<int:student_id>/profile/", StudentProfileView.as_view(), name="student_profile"),
   path("student/<int:student_id>/update/", UpdateStudentProfileView.as_view(), name="update_student_profile"),
   #url for view departments
   path('view_departments/',ViewDepartments.as_view(),name='view_departments'),
   #url for view courses
   path('view_courses/',ViewCourses.as_view(),name='view_courses'),
   #url for view courses by department
   path('view_courses/<int:department_id>/',ViewCoursesByDepartment.as_view(),name='view_courses_by_department'),
   #url for view jobs
   path('jobs/', ViewJobs.as_view(), name='ViewJobs'),
   #url for view companies
   path('companies/', ViewCompanies.as_view(), name='ViewCompanies'),
   #url for view jobs by company id
   path('job_by_company/<int:company_id>/', Job_View_by_CompanyView.as_view(), name='Job_By_Company'),
   #url for view job details by job id
   path('job/<int:job_id>/', JobDetailView.as_view(), name='job-detail'),
   #url for leave requests by student id
   path('list-student-requests/<int:student_id>/', StudentRequestsByStudentAPIView.as_view(), name='student-requests-by-student'),
   #url for mark attendance
   path('api/mark-attendance/', AttendanceAPIView.as_view(), name='mark-attendance'),
   #url for tutor to view student requests assigned to them
   path('tutor-requests/<int:tutor_id>/', TutorStudentRequestsAPIView.as_view(), name='tutor-requests'),
   #url for tutor approve a request
   path('tutor-requests/<int:tutor_id>/approve/<int:request_id>/', TutorApproveRequestAPIView.as_view(), name='tutor-approve-request'),
   #url for tutor reject a leave request
   path('tutor-requests/<int:tutor_id>/reject/<int:request_id>/', TutorRejectRequestAPIView.as_view(), name='tutor-reject-request'),
   #url for tutor view jobs
   path('tutor/jobs/', TutorViewJobsAPIView.as_view(), name='tutor_view_jobs'),
   #url for tutor view,approve,reject applied students for a job
   path('tutor/<int:tutor_id>/applied-students/', TutorViewAppliedStudentsAPIView.as_view(), name='tutor_view_applied_students'),
   path('tutor/<int:tutor_id>/application/<int:application_id>/approve/',TutorApproveApplicationAPIView.as_view(),name='tutor_approve_application'),
   path('tutor/<int:tutor_id>/application/<int:application_id>/reject/',TutorRejectApplicationAPIView.as_view(),name='tutor_reject_application'),

   #url for tutor view companies
   path('tutor/companies/', TutorviewCompaniesView.as_view(), name='tutor_view_companies'),
   #url for tutor view jobs by company
   path('tutor/companies/<int:company_id>/jobs/', TutorViewJobsByCompanyView.as_view(), name='tutor_view_jobs_by_company'),
   #student job applications by student id
   path("student/<int:student_id>/job-applications/", StudentJobApplicationsAPIView.as_view(),name="student-job-applications"),
   #tutor view attendance of students
   path("tutor/<int:tutor_id>/attendance/", TutorViewAttendanceAPIView.as_view(), name="tutor_view_attendance"),
   # attendance update status
   path("attendance/update/<int:attendance_id>/", UpdateAttendanceStatusAPIView.as_view(), name="update-attendance-status"),
   #view attendance by today's date
   path("tutor/<int:tutor_id>/attendance/today/", TutorTodayAttendanceAPIView.as_view(), name="tutor-today-attendance"),
   # attendance update status today
   path("attendance/update/<int:attendance_id>/",UpdateAttendanceStatusAPIView.as_view(),name="update-attendance-status"),



   #guard
   #guard view approved leave requests
   path("guard/approved-leaves/", GuardApprovedLeaveRequestsAPIView.as_view(),name="guard-approved-leaves"),
   #guard update leave status to 'Leaved'
   path("guard/leave/update/<int:request_id>/", GuardUpdateLeaveStatusAPIView.as_view(),name="guard-update-leave"),

   # view student details
   path('student/<int:pk>/', StudentDetailView.as_view(), name='view_student'),
]