from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from .models import *
from gatepassapp.models import *
# Create your views here.

def admin_hod_login(request):
    if request.method == "POST":
        role = request.POST.get("role")
        password = request.POST.get("password")
        hod_id = request.POST.get("hod_id")

        # Pick correct email field
        email = request.POST.get("admin_email") if role == "admin" else request.POST.get("hod_email")

        print("Form email:", repr(email))
        print("Form password:", repr(password))
        print("Form role:", repr(role))

        if role == "admin":
            try:
                admin = tbl_admin.objects.get(admin_email=email, password=password)
                request.session["admin_id"] = admin.id
                request.session["role"] = "admin"
                messages.success(request, "Admin login successful!")
                # redirect back to login page so template can show message, then JS will redirect to admin index
                return redirect(f"{reverse('admin_hod_login')}?next={reverse('index')}")
            except tbl_admin.DoesNotExist:
                messages.error(request, "Invalid admin credentials.")
                return redirect("admin_hod_login")

        elif role == "hod":
            try:
                hod = tbl_hod.objects.get(email=email, hod_id=hod_id)
                request.session["hod_id"] = hod.id
                request.session["role"] = "hod"
                messages.success(request, "HOD login successful!")
                # redirect back to login page so template can show message, then JS will redirect to HOD index
                return redirect(f"{reverse('admin_hod_login')}?next={reverse('hod_index')}")
            except tbl_hod.DoesNotExist:
                messages.error(request, "Invalid HOD credentials.")
                return redirect("admin_hod_login")

        else:
            messages.error(request, "Please select a role.")
            return redirect("admin_hod_login")

    return render(request, "login.html")

# adminapp/views.py
from django.shortcuts import render

def index(request):
    return render(request, "adminapp/index.html")



def logout(request):
    # Clear any custom session keys we use for auth
    for k in ("admin_id", "hod_id", "role", "id"):
        if k in request.session:
            del request.session[k]

    # Also call Django's auth logout to be safe
    try:
        auth_logout(request)
    except Exception:
        pass

    messages.success(request, "You have been logged out.")
    return redirect('admin_hod_login')


from django.shortcuts import render, redirect
from .models import tbl_department
from django.utils.text import slugify


def add_department(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            slug = slugify(name)
            # Prevent duplicates
            if not tbl_department.objects.filter(slug=slug).exists():
                dept = tbl_department(name=name, slug=slug)
                dept.save()
                return redirect('add_department')
    return render(request, 'adminapp/add_department.html')

def list_departments(request):
    departments = tbl_department.objects.all()
    return render(request, 'adminapp/list_departments.html', {'departments': departments})

def edit_department(request, id):
    department = get_object_or_404(tbl_department, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            department.name = name
            department.slug = slugify(name)
            department.icon = None  # Reset icon so it auto-assigns again
            department.save()
            return redirect('list_departments')
    return render(request, 'adminapp/edit_department.html', {'department': department})

def delete_department(request, id):
    department = get_object_or_404(tbl_department, id=id)
    department.delete()
    return redirect('list_departments')

from django.shortcuts import render, redirect
from .models import tbl_course, tbl_department
def add_course(request):
    departments = tbl_department.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        department = tbl_department.objects.get(id=department_id)

        tbl_course.objects.create(name=name, department=department)
        return redirect('list_courses')

    return render(request, 'adminapp/add_course.html', {'departments': departments})

# Edit Course
def edit_course(request, course_id):
    course = tbl_course.objects.get(id=course_id)
    departments = tbl_department.objects.all()

    if request.method == 'POST':
        course.name = request.POST.get('name')
        dept_id = request.POST.get('department')
        course.department = tbl_department.objects.get(id=dept_id)
        course.save()
        return redirect('list_courses')

    return render(request, 'adminapp/edit_course.html', {
        'course': course,
        'departments': departments
    })


# Delete Course
def delete_course(request, course_id):
    course = tbl_course.objects.get(id=course_id)
    course.delete()
    return redirect('list_courses')


# Filtered Course List
def list_courses(request):
    department_id = request.GET.get('department')
    departments = tbl_department.objects.all()

    if department_id:
        courses = tbl_course.objects.filter(department_id=department_id)
    else:
        courses = tbl_course.objects.select_related('department').all()

    return render(request, 'adminapp/list_courses.html', {
        'courses': courses,
        'departments': departments,
        'selected_dept': department_id
    })




from django.shortcuts import render, redirect, get_object_or_404
from .models import tbl_hod, tbl_department
def add_hod(request):
    departments = tbl_department.objects.all()

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        hod_id = request.POST['hod_id']
        gender = request.POST['gender']
        phone = request.POST['phone']
        dept_id = request.POST['department']
        image = request.FILES.get('image')

        department = tbl_department.objects.get(id=dept_id)

        tbl_hod.objects.create(
            name=name,
            email=email,
            hod_id=hod_id,
            gender=gender,
            phone_number=phone,
            image=image,
            department=department
        )
        return redirect('list_hods')

    return render(request, 'adminapp/hod_add.html', {'departments': departments})


def list_hods(request):
    hods = tbl_hod.objects.all()
    return render(request, 'adminapp/hod_list.html', {'hods': hods})


def edit_hod(request, hod_id):
    hod = get_object_or_404(tbl_hod, id=hod_id)
    departments = tbl_department.objects.all()

    if request.method == 'POST':
        hod.name = request.POST['name']
        hod.email = request.POST['email']
        hod.hod_id = request.POST['hod_id']
        hod.gender = request.POST['gender']
        hod.phone_number = request.POST['phone']
        hod.department = tbl_department.objects.get(id=request.POST['department'])

        if 'image' in request.FILES:
            hod.image = request.FILES['image']

        hod.save()
        return redirect('list_hods')

    return render(request, 'adminapp/hod_edit.html', {'hod': hod, 'departments': departments})


def delete_hod(request, hod_id):
    hod = get_object_or_404(tbl_hod, id=hod_id)
    hod.delete()
    return redirect('list_hods')

from django.shortcuts import render, get_object_or_404, redirect
from adminapp.models import tbl_tutor
from django.core.paginator import Paginator
# from gatepassapp.models import tbl_tutor
from adminapp.models import tbl_department

def list_tutors(request):
    department_id = request.GET.get('department')
    departments = tbl_department.objects.all()

    tutors = tbl_tutor.objects.all()
    if department_id:
        tutors = tutors.filter(department_id=department_id)

    # Pagination (show 15 tutors per page)
    paginator = Paginator(tutors, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminapp/list_tutors.html', {
        'tutors': page_obj,
        'departments': departments,
        'selected_dept': department_id,
        'page_obj': page_obj,
    })


def delete_tutor(request, tutor_id):
    tutor = get_object_or_404(tbl_tutor, id=tutor_id)
    tutor.delete()
    return redirect('list_tutors')




from django.shortcuts import render, redirect, get_object_or_404
from .models import Job,Tbl_Job
from adminapp.models import tbl_department

def add_job(request):
    if request.method == "POST":
        title = request.POST.get("title")
        company_id = request.POST.get("company")
        logo = request.FILES.get("logo")
        job_type = request.POST.get("job_type")
        description = request.POST.get("description")
        place = request.POST.get("place")
        department_id = request.POST.get("department")  # ✅ fix key
        salary = request.POST.get("salary")
        responsibilities = request.POST.get("responsibilities")
        qualifications = request.POST.get("qualifications")
        vacancy = request.POST.get("vacancy")

        company = Company.objects.get(id=company_id)
        department = tbl_department.objects.get(id=department_id)  # ✅ fix variable name

        Tbl_Job.objects.create(
            title=title,
            logo=logo,
            company=company,
            job_type=job_type,
            description=description,
            place=place,
            department_id=department,   # ✅ assign the object
            salary=salary,
            responsibilities=responsibilities,
            qualifications=qualifications,
            vacancy=vacancy,
        )
        return redirect("view_jobs")

    companies = Company.objects.all()
    departments = tbl_department.objects.all()
    return render(
        request,
        "adminapp/add_job.html",
        {"departments": departments, "companies": companies},
    )


# View Jobs
def view_jobs(request):
    jobs = Tbl_Job.objects.all().order_by("-date")
    return render(request, "adminapp/view_jobs.html", {"jobs": jobs})


def edit_job(request, job_id):
    job = get_object_or_404(Tbl_Job, id=job_id)
    departments = tbl_department.objects.all()
    companies = Company.objects.all()

    if request.method == "POST":
        company_id = request.POST.get("company")
        dept_id = request.POST.get("department")   # ✅ match form field name

        job.company = Company.objects.get(id=company_id)
        job.department_id = tbl_department.objects.get(id=dept_id)  # ✅ set object

        job.title = request.POST.get("title")
        job.job_type = request.POST.get("job_type")
        job.description = request.POST.get("description")
        job.place = request.POST.get("place")
        job.salary = request.POST.get("salary")
        job.responsibilities = request.POST.get("responsibilities")
        job.qualifications = request.POST.get("qualifications")
        job.vacancy = request.POST.get("vacancy")

        if "logo" in request.FILES:
            job.logo = request.FILES["logo"]

        job.save()
        messages.success(request, "Job updated successfully!")
        return redirect("view_jobs")

    return render(
        request,
        "adminapp/edit_job.html",
        {"job": job, "departments": departments, "companies": companies},
    )

# Delete Job
def delete_job(request, job_id):
    job = get_object_or_404(Tbl_Job, id=job_id)
    job.delete()
    return redirect("view_jobs")



from django.shortcuts import render, redirect
from .models import College

def manage_college(request):
    # Try to get the only college record (if it exists)
    college = College.objects.first()

    if request.method == "POST":
        name = request.POST.get("name")
        langitude = request.POST.get("langitude")
        lotitude = request.POST.get("lotitude")

        if college:  # Update existing
            college.name = name
            college.langitude = langitude
            college.lotitude = lotitude
            college.save()
        else:  # Create new
            College.objects.create(
                name=name,
                langitude=langitude,
                lotitude=lotitude
            )
        return redirect("manage_college")  # reload same page

    return render(request, "adminapp/manage_college.html", {"college": college})


# views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Company

def add_company(request):
    """
    Show form and handle POST to create a Company.
    No forms.py used; minimal validation performed here.
    """
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        logo = request.FILES.get('logo')

        # Basic validation
        errors = []
        if not name:
            errors.append("Name is required.")
        if not logo:
            errors.append("Logo file is required.")

        # Optional: validate file content type or extension
        if logo:
            # example: allow common image types
            allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
            if hasattr(logo, 'content_type') and logo.content_type not in allowed:
                errors.append("Unsupported logo type. Allowed: jpeg, png, webp, gif.")

        if errors:
            # re-render with errors and previously entered data
            return render(request, 'adminapp/add_company.html', {
                'errors': errors,
                'name': name,
                'description': description,
            })

        # Create and save Company
        company = Company.objects.create(
            name=name,
            description=description,
            logo=logo
        )
        messages.success(request, f"Company '{company.name}' added.")
        return redirect(reverse('company-list'))

    # GET
    return render(request, 'adminapp/add_company.html')
    

def company_list(request):
    companies = Company.objects.all().order_by('name')
    return render(request, 'adminapp/company_list.html', {'companies': companies})

# views.py
from django.shortcuts import get_object_or_404

def edit_company(request, pk):
    company = get_object_or_404(Company, pk=pk)

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        logo = request.FILES.get('logo')

        if not name:
            return render(request, 'company/edit_company.html', {
                'company': company,
                'error': "Name is required."
            })

        company.name = name
        company.description = description
        if logo:  # update only if new file uploaded
            company.logo = logo
        company.save()

        return redirect('company-list')

    return render(request, 'adminapp/edit_company.html', {'company': company})
from django.shortcuts import render, get_object_or_404, redirect
from .models import Company

def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)

    if request.method == "POST":
        company.delete()
        return redirect('company-list')

    # No need for confirmation template
    return redirect('company-list')



from django.shortcuts import render
from gatepassapp.models import JobApplication
from adminapp.models import tbl_department, tbl_course, tbl_tutor, Company

def admin_view_applicants(request):
    # Get query params
    department_id = request.GET.get("department")
    course_id = request.GET.get("course")
    tutor_id = request.GET.get("tutor")
    company_id = request.GET.get("company")

    # Start with all applications
    applications = JobApplication.objects.all().order_by("-applied_at")

    # Apply filters if provided
    if department_id:
        applications = applications.filter(student__department__id=department_id)
    if course_id:
        applications = applications.filter(student__course__id=course_id)
    if tutor_id:
        applications = applications.filter(student__tutor__id=tutor_id)
    if company_id:
        applications = applications.filter(job__company__id=company_id)

    # Filter options
    departments = tbl_department.objects.all()
    courses = tbl_course.objects.all()
    tutors = tbl_tutor.objects.all()
    companies = Company.objects.all()

    context = {
        "applications": applications,
        "departments": departments,
        "courses": courses,
        "tutors": tutors,
        "companies": companies,
    }
    return render(request, "adminapp/admin_view_applicants.html", context)

from django.shortcuts import render, redirect, get_object_or_404
from .models import GateGuard

def manage_guard(request):
    # CREATE OR UPDATE
    if request.method == "POST":
        guard_id = request.POST.get("guard_id")
        name = request.POST.get("name")
        gender = request.POST.get("gender")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        gate_location = request.POST.get("gate_location")
        photo = request.FILES.get("photo")

        edit_id = request.POST.get("edit_id")  # Hidden field for editing

        if edit_id:  
            guard = get_object_or_404(GateGuard, id=edit_id)
        else:
            guard = GateGuard()

        guard.guard_id = guard_id
        guard.name = name
        guard.gender = gender
        guard.phone = phone
        guard.email = email
        guard.gate_location = gate_location

        if photo:
            guard.photo = photo

        guard.save()
        return redirect("manage_guard")

    # DELETE
    delete_id = request.GET.get("delete")
    if delete_id:
        GateGuard.objects.filter(id=delete_id).delete()
        return redirect("manage_guard")

    # EDIT (pre-fill form)
    edit_data = None
    edit_id = request.GET.get("edit")
    if edit_id:
        edit_data = get_object_or_404(GateGuard, id=edit_id)

    # LIST
    guards = GateGuard.objects.all()

    return render(request, "adminapp/manage_guard.html", {
        "guards": guards,
        "edit_data": edit_data
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from gatepassapp.models import JobApplication

def update_application_status(request, application_id):
    if request.method == "POST":
        new_status = request.POST.get("status")

        allowed_status = ["Company Approved", "Company Rejected"]
        if new_status not in allowed_status:
            messages.error(request, "Invalid status")
            return redirect('admin_view_applicants')

        application = get_object_or_404(JobApplication, id=application_id)
        application.status = new_status
        application.save()

        messages.success(request, f"Status updated to {new_status}")
        return redirect('admin_view_applicants')







#Hod ##

from django.shortcuts import render, redirect
from adminapp.models import tbl_hod
from django.shortcuts import render, redirect
from adminapp.models import tbl_hod

def hod_index(request):
    if "hod_id" not in request.session:  # check login
        return redirect("admin_hod_login")

    # fetch the logged-in HOD
    hod_id = request.session["hod_id"]
    hod = tbl_hod.objects.get(id=hod_id)

    return render(request, "hodapp/hod_index.html", {"hod": hod})



from django.shortcuts import render, redirect
from django.contrib import messages
from adminapp.models import tbl_tutor, tbl_department, tbl_course, tbl_hod
def add_tutor(request):
    # Ensure only HOD can add
    if request.session.get("role") != "hod":
        messages.error(request, "Access denied. Only HODs can add tutors.")
        return redirect("admin_hod_login")

    if request.method == "POST":
        try:
            # Get form data
            name = request.POST.get("name")
            email = request.POST.get("email")
            tutor_id = request.POST.get("tutor_id")
            department_id = request.POST.get("department")
            course_id = request.POST.get("course")
            phone = request.POST.get("phone")
            gender = request.POST.get("gender")
            experience = request.POST.get("experience", 0)
            image = request.FILES.get("image")
            year = int(request.POST.get("year"))          # convert to integer
            batch = request.POST.get("batch")

            # Convert numeric fields safely
            experience = int(experience) if experience else 0

            # Fetch related objects
            department = tbl_department.objects.get(id=department_id)
            course = tbl_course.objects.get(id=course_id)
            hod = tbl_hod.objects.get(id=request.session.get("hod_id"))

            # Create tutor
            tutor = tbl_tutor.objects.create(
                name=name,
                email=email,
                tutor_id=tutor_id,
                department=department,
                course=course,
                hod=hod,
                phone_number=phone,
                gender=gender,
                experience=experience,
                image=image,
                year=year,
                batch=batch,
            )

            messages.success(request, f"Tutor {tutor.name} added successfully!")
            return redirect("view_tutors")

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("add_tutor")

    # GET request, render form
    departments = tbl_department.objects.all()
    courses = tbl_course.objects.all()
    return render(request, "hodapp/add_tutor.html", {
        "departments": departments,
        "courses": courses
    })

# def view_tutors(request):
#     if request.session.get("role") != "hod":
#         messages.error(request, "Access denied.")
#         return redirect("admin_hod_login")

#     hod_id = request.session.get("hod_id")
#     tutors = tbl_tutor.objects.filter(hod_id=hod_id)
#     return render(request, "hodapp/view_tutors.html", {"tutors": tutors})

from django.shortcuts import render, redirect, get_object_or_404
from adminapp.models import tbl_department, tbl_course, tbl_hod
from .models import tbl_tutor

# View tutors
def view_tutors(request):
    hod_id = request.session.get("hod_id")   # assuming you store hod_id in session
    tutors = tbl_tutor.objects.filter(hod_id=hod_id)
    return render(request, "hodapp/view_tutors.html", {"tutors": tutors})

# Edit tutor
def edit_tutor(request, tutor_id):
    tutor = get_object_or_404(tbl_tutor, id=tutor_id)

    if request.method == "POST":
        tutor.name = request.POST.get("name")
        tutor.email = request.POST.get("email")
        tutor.tutor_id = request.POST.get("tutor_id")
        tutor.department_id = request.POST.get("department")
        tutor.course_id = request.POST.get("course")
        tutor.phone_number = request.POST.get("phone_number")
        tutor.gender = request.POST.get("gender")
        tutor.experience = request.POST.get("experience")
        tutor.year = request.POST.get("year")
        tutor.batch = request.POST.get("batch")


        if "image" in request.FILES:
            tutor.image = request.FILES["image"]

        tutor.save()
        return redirect("view_tutors")

    departments = tbl_department.objects.all()
    courses = tbl_course.objects.all()
    return render(request, "hodapp/edit_tutor.html", {
        "tutor": tutor,
        "departments": departments,
        "courses": courses
    })

# Delete tutor
def delete_tutor(request, tutor_id):
    tutor = get_object_or_404(tbl_tutor, id=tutor_id)
    tutor.delete()
    return redirect("view_tutors")
from django.shortcuts import render, redirect, get_object_or_404
from gatepassapp.models import StudentRequest
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def hod_view_requests(request):
    """
    Display leave requests for the logged-in HOD.
    """
    # Get logged-in HOD ID (assuming stored in session)
    hod_id = request.session.get("hod_id")
    if not hod_id:
        return redirect("admin_hod_login")  # redirect if not logged in

    # Filter requests forwarded to this HOD only
    requests = StudentRequest.objects.filter(forwarded_to_hod=True, hod_id=hod_id)

    # Optional: filter by category (Urgent / Not Urgent)
    category_filter = request.GET.get("category")
    if category_filter in ["Urgent", "Not Urgent"]:
        requests = requests.filter(category=category_filter)

    # Group requests by (course, tutor)
    grouped_requests = {}
    for req in requests:
        key = (req.course.name, req.tutor.name if req.tutor else "N/A")
        if key not in grouped_requests:
            grouped_requests[key] = []
        grouped_requests[key].append(req)

    context = {
        "grouped_requests": grouped_requests,
        "selected_category": category_filter
    }
    return render(request, "hodapp/hod_requests.html", context)


import json
from io import BytesIO
from django.core.files.base import ContentFile
import qrcode

def hod_approve_request(request, request_id):
    student_request = get_object_or_404(StudentRequest, id=request_id)

    # Ensure only the HOD assigned can approve
    hod_id = request.session.get("hod_id")
    if student_request.hod_id != hod_id:
        return redirect("hod-view-requests")

    student_request.status = "HOD Approved"

    # ★ Create JSON data for QR
    qr_payload = {
        "leave_id": student_request.id,
        "student_name": student_request.student.name,
        "tutor_name": student_request.tutor.name if student_request.tutor else "N/A",
        "hod_name": student_request.hod.name,
        "department_name": student_request.department.name,
        "course_name": student_request.course.name,
        "request_date": student_request.request_date.strftime("%d/%m/%Y") if student_request.request_date else "",
        "request_time": str(student_request.request_time) if student_request.request_time else "",
        "reason": student_request.reason,
        "category": student_request.category,
        "status": student_request.status,
    }

    qr_text = json.dumps(qr_payload)   # Convert to JSON string

    qr_img = qrcode.make(qr_text)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")

    file_name = f"qr_{student_request.id}.png"
    student_request.qr_code.save(file_name, ContentFile(buffer.getvalue()))

    student_request.save()
    return redirect("hod-view-requests")

def hod_reject_request(request, request_id):
    student_request = get_object_or_404(StudentRequest, id=request_id)

    # Ensure only the HOD assigned can reject
    hod_id = request.session.get("hod_id")
    if student_request.hod_id != hod_id:
        return redirect("hod-view-requests")

    student_request.status = "HOD Rejected"
    student_request.save()
    return redirect("hod-view-requests")




def view_applicants(request):
    return render(request, "hodapp/applicants.html")



from django.shortcuts import render
from adminapp.models import Tbl_Job, tbl_department, Company

def hod_view_jobs(request):
    # filter based on query params
    department_id = request.GET.get("department")
    company_id = request.GET.get("company")

    jobs = Tbl_Job.objects.all().order_by("-date")

    if department_id:
        jobs = jobs.filter(department_id=department_id)
    if company_id:
        jobs = jobs.filter(company__id=company_id)

    departments = tbl_department.objects.all()
    companies = Company.objects.all()

    context = {
        "jobs": jobs,
        "departments": departments,
        "companies": companies,
    }
    return render(request, "hodapp/hod_view_jobs.html", context)


from gatepassapp.models import JobApplication
# views.py
from django.shortcuts import render
from adminapp.models import  tbl_department, tbl_course, tbl_tutor, Company

def hod_view_applicants(request):
    hod = request.session.get("hod_id") 
     # assuming HOD is logged in; adjust if you store HOD differently
    hod = tbl_hod.objects.get(id=hod)
    # Get query params
    course_id = request.GET.get("course")
    tutor_id = request.GET.get("tutor")
    company_id = request.GET.get("company")

    # Filter applications by HOD department only
    applications = JobApplication.objects.filter(student__department=hod.department).order_by("-applied_at")

    if course_id:
        applications = applications.filter(student__course__id=course_id)
    if tutor_id:
        applications = applications.filter(student__tutor__id=tutor_id)
    if company_id:
        applications = applications.filter(job__company__id=company_id)

    # Filters: courses and tutors from HOD department, companies all
    courses = tbl_course.objects.filter(department=hod.department)
    tutors = tbl_tutor.objects.filter(department=hod.department)
    companies = Company.objects.all()

    context = {
        "applications": applications,
        "courses": courses,
        "tutors": tutors,
        "companies": companies,
        "department": hod.department.name,
    }
    return render(request, "hodapp/hod_view_applicants.html", context)



def hod_profile(request, hod_id):
    try:
        hod = tbl_hod.objects.get(id=hod_id)
    except tbl_hod.DoesNotExist:
        return render(request, 'hodapp/error.html', {'message': 'HOD not found.'})

    return render(request, 'hodapp/hod_profile.html', {'hod': hod})



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from adminapp.models import tbl_hod, tbl_department
from django.contrib import messages

def edit_hod_profile(request, hod_id):
    hod = get_object_or_404(tbl_hod, id=hod_id)
    departments = tbl_department.objects.all()

    if request.method == "POST":
        hod.name = request.POST.get("name")
        hod.email = request.POST.get("email")
        hod.phone_number = request.POST.get("phone")
        hod.gender = request.POST.get("gender")
        
        department_id = request.POST.get("department")
        if department_id:
            hod.department = tbl_department.objects.get(id=department_id)
        
        if request.FILES.get("image"):
            hod.image = request.FILES["image"]
        
        hod.save()
        messages.success(request, "HOD profile updated successfully!")
        return redirect('hod_profile', hod_id=hod.id)

    context = {
        "hod": hod,
        "departments": departments
    }
    return render(request, "hodapp/hod_edit_profile.html", context)
