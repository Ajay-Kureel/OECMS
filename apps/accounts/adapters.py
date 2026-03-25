from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied
from django.contrib import messages

class CollegeDomainAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Extract the email Google sent us
        email = sociallogin.account.extra_data.get('email', '')
        
        # --- THE DOMAIN LOCK ---
        # Change '@mycollege.edu' to whatever domain you want to restrict it to.
        # For testing your project locally right now, you might want to leave this commented out, 
        # or change it to '@gmail.com' just so you can test it yourself!
        
        allowed_domain = '@gmail.com' 
        
        if not email.endswith(allowed_domain):
            messages.error(request, f"Access Denied: You must use an official {allowed_domain} email address to log in.")
            raise PermissionDenied("Invalid Email Domain")
            
        # If it passes, automatically set their role to 'student' if they are new
        if not sociallogin.is_existing:
            sociallogin.user.role = 'student'