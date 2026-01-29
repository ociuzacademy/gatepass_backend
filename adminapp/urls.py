from django.urls import path
from . import views
from .views import *
urlpatterns=[
    path('', views.admin_hod_login, name='admin_hod_login'),  # Login page

    # Admin URLs
    path('index/', views.index, name='index'),      # Admin dashboard
    path('logout/', views.logout, name='logout'),  # Logout page
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/', views.list_departments, name='list_departments'),
    path('departments/edit/<int:id>/', views.edit_department, name='edit_department'),
    path('departments/delete/<int:id>/', views.delete_department, name='delete_department'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/', views.list_courses, name='list_courses'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('hod/add/', views.add_hod, name='add_hod'),
    path('hod/list/', views.list_hods, name='list_hods'),
    path('hod/edit/<int:hod_id>/', views.edit_hod, name='edit_hod'),
    path('hod/delete/<int:hod_id>/', views.delete_hod, name='delete_hod'),
    path('tutors/', views.list_tutors, name='list_tutors'),
    path('tutors/delete/<int:tutor_id>/', views.delete_tutor, name='delete_tutor'),
    path("add-job/", views.add_job, name="add_job"),
    path("jobs/", views.view_jobs, name="view_jobs"),
    path("edit-job/<int:job_id>/", views.edit_job, name="edit_job"),
    path("delete-job/<int:job_id>/", views.delete_job, name="delete_job"),
    path("college/", views.manage_college, name="manage_college"),
    path('company/add/', add_company, name='company-add'),
    path('companies/', views.company_list, name='company-list'),
    path('companies/edit/<int:pk>/', views.edit_company, name='company-edit'),
    path('companies/delete/<int:pk>/', views.delete_company, name='company-delete'),
    path("admin_view_applicants/", views.admin_view_applicants, name="admin_view_applicants"),
    path("manage-guard/", manage_guard, name="manage_guard"),
    path("hod/update-application-status/<int:application_id>/",update_application_status,name="update_application_status"),




    # HOD URLs
    path('hod_index/', views.hod_index, name='hod_index'),  # HOD dashboard
    path("add-tutor/", views.add_tutor, name="add_tutor"),
    path("view-tutors/", views.view_tutors, name="view_tutors"),
    path("tutors/edit/<int:tutor_id>/", views.edit_tutor, name="edit_tutor"),
    path("tutors/delete/<int:tutor_id>/", views.delete_tutor, name="delete_tutor"),
    # path('view_requests/', views.view_requests, name='view_requests'),
    path('hod_jobs/', views.hod_view_jobs, name='hod_view_jobs'),
    path('applicants/', views.view_applicants, name='view_applicants'),
    path('hod/requests/', hod_view_requests, name='hod-view-requests'),
    path('hod/requests/approve/<int:request_id>/', hod_approve_request, name='hod-approve-request'),
    path('hod/requests/reject/<int:request_id>/', hod_reject_request, name='hod-reject-request'),
    path("hod/jobs/", views.hod_view_jobs, name="hod_view_jobs"),
    path("hod/applicants/", views.hod_view_applicants, name="hod_view_applicants"),
    path('hod/profile/<int:hod_id>/', views.hod_profile, name='hod_profile'),
    # urls.py
    path('hod/profile/update/<int:hod_id>/', views.edit_hod_profile, name='edit_hod_profile'),


]