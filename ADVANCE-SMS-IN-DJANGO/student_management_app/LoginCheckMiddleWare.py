from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, redirect
from django.urls import reverse


class LoginCheckMiddleWare(MiddlewareMixin):
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        # print(modulename)
        user = request.user

        public_paths = [
            reverse("login"), 
            reverse("doLogin"),
            reverse("home"),  # Assuming you have a URL name 'home' for your homepage
            # Add any other paths that should be public here
        ]

        # Check if the request path is one of the public paths
        if request.path in public_paths:
            return None

        #Check whether the user is logged in or not
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "student_management_app.HodViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return redirect("admin_home")
            
            elif user.user_type == "2":
                if modulename == "student_management_app.StaffViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return redirect("staff_home")
            
            elif user.user_type == "3":
                if modulename == "student_management_app.StudentViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return redirect("student_home")

            else:
                return redirect("login")

        else:
            if request.path == reverse("login") or request.path == reverse("doLogin"):
                pass
            else:
                return redirect("home")
