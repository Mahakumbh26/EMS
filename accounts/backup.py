# from django.contrib.auth.models import BaseUserManager
# class EmployeeManager(BaseUserManager):
#         ...
#     def create_user(self, username, password, Role, **extrafields):
#         extrafields['is_staff']=True
#         if not username or not password or not Role:
#             raise ValueError("Users must have a unique username, password and Role")
#         if Role=="Admin":
#             extrafields["is_superuser"]=True
#         else:
#             extrafields["is_superuser"]=False
#         user = self.model(username=username, password=password,role=Role,**extrafields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, password, role):
#         return self.create_user(username, password, role)

# class Employee_login_details(AbstractBaseUser, PermissionsMixin):

#     username = models.CharField(max_length=150, unique=True,primary_key=True)
#     password=models.CharField(max_length=150,null=False,unique=True)
#     role=models.CharField(max_length=20,choices=[(r.value, r.name.title()) for r in Role],default=Role.none.value)

#     objects = EmployeeManager()
#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['password','role']
#     def __str__(self):
#         return self.username


#     class Teams(Enum):
#         Farmcore = "Farm Core"
#         Farmtech= "Farm Tech"
        # Infracore = "Infra Core"
#         Infratech= "Infra Tech"
#         none="None"


# class Roles(Enum):
#         Admin = "Admin"
#         Hr="Hr"
#         MD= "MD"
#         Employee="Employee"
#         Intern="Intern"
#         TeamLead="TeamLead"
#         other="others"
