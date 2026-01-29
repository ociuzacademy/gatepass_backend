from django.db import models

# Create your models here.
class tbl_admin(models.Model):
    admin_email = models.EmailField()
    password = models.CharField(max_length=100)
    role=models.CharField(max_length=50, default='admin')


    def __str__(self):
        return self.admin_email


from django.db import models
from django.utils.text import slugify

class tbl_department(models.Model):
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=100, blank=True, null=True)  # Font Awesome class name
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.icon:
            icon_mapping = {
                "English": "fa-book",
                "Malayalam": "fa-book-open",
                "Mathematics": "fa-calculator",
                "Statistics": "fa-chart-line",
                "History": "fa-history",
                "Botany": "fa-leaf",
                "Computer Science": "fa-laptop-code",
                "Physics": "fa-atom",
                "Chemistry": "fa-flask",
                "Zoology": "fa-paw",
                "Social Work": "fa-users",
                "Home Science": "fa-utensils",
                "Psychology": "fa-brain",
                "Commerce": "fa-money-bill-wave",
                "Economics": "fa-chart-pie",
                "Sociology": "fa-users",
            }
            self.icon = icon_mapping.get(self.name, "fa-building")  # fallback default

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class tbl_course(models.Model):
    name = models.CharField(max_length=200)
    department = models.ForeignKey(tbl_department, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return f"{self.name} ({self.department.name})"
    
class tbl_hod(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    hod_id = models.CharField(max_length=50, unique=True)  # NEW FIELD
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='hod_images/', blank=True, null=True)
    department = models.ForeignKey(tbl_department, on_delete=models.CASCADE)
    roles = models.CharField(max_length=100, default='hod')

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/')
    description = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name
    
class Job(models.Model):
    company = models.CharField(max_length=255)  # NEW FIELD
    title = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/')
    job_type = models.CharField(
        max_length=10,
        choices=[('full-time', 'Full-Time'), ('part-time', 'Part-Time')],
        default='full-time',
    )
    description = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    department = models.ForeignKey(
        'tbl_department',
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    responsibilities = models.TextField(max_length=500)
    qualifications = models.TextField(max_length=500)
    vacancy = models.PositiveIntegerField(default=1)
    # passoutyear = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} at {self.company} - {self.department.name} - ${self.salary}"

 
class Tbl_Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # NEW FIELD
    title = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logo/')
    job_type = models.CharField(
        max_length=10,
        choices=[('full-time', 'Full-Time'), ('part-time', 'Part-Time')],
        default='full-time',
    )
    description = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    department_id = models.ForeignKey(
        'tbl_department',
        on_delete=models.CASCADE,
        related_name='job'
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    responsibilities = models.TextField(max_length=500)
    qualifications = models.TextField(max_length=500)
    vacancy = models.PositiveIntegerField(default=1)
    # passoutyear = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} at {self.company} - {self.department_id.name} - ${self.salary}"






class College(models.Model):
    name = models.CharField(max_length=255)
    langitude = models.FloatField()
    lotitude = models.FloatField()

    def __str__(self):
        return self.name
    
class tbl_tutor(models.Model):
    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    tutor_id = models.CharField(max_length=50, unique=True)  
    department = models.ForeignKey('adminapp.tbl_department', on_delete=models.CASCADE, related_name='tutors')
    course = models.ForeignKey('adminapp.tbl_course', on_delete=models.CASCADE, related_name='tutor_courses')
    hod = models.ForeignKey('adminapp.tbl_hod', on_delete=models.CASCADE, related_name='hods')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(upload_to='tutor_images/', blank=True, null=True)
    roles = models.CharField(max_length=100, default='tutor')
    experience = models.IntegerField(default=0)  
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])

    # ✅ changed year to IntegerField
    year = models.IntegerField(choices=YEAR_CHOICES, default=1)
    batch = models.CharField(max_length=20, help_text="Format: YYYY-YYYY", default="2025-2029")

    def __str__(self):
        return f"{self.name} (Year {self.year} - {self.batch})"






class GateGuard(models.Model):
    guard_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
    )
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    photo = models.ImageField(upload_to='guard_photos/', blank=True, null=True)
    gate_location = models.CharField(max_length=100)
    roles = models.CharField(max_length=50, default='guard')

    def __str__(self):
        return f"{self.guard_id} - {self.name}"
