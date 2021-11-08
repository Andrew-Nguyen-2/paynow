from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
# from django.contrib.auth.models import User
from accounts.models import OrgUser
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.db.models.query_utils import Q
from django.template.loader import render_to_string

# Create your views here.
from paynow.forms import ContactForm, NewUserForm


def home_view(request, *args, **kwargs):  # *args, **kwargs
    print(args, kwargs)
    print(request.user)
    # return HttpResponse("<h1>Hello World</h1>")  # string of HTML code
    return render(request, "home.html", {})


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Contact From PayNow"
            body = {
                'first': form.cleaned_data['first'],
                'last': form.cleaned_data['last'],
                'email': form.cleaned_data['email'],
                'message': form.cleaned_data['message']
            }
            message = "\n".join(body.values())

            try:
                send_mail(subject, message, body['email'], ['andrew.nguyen.18@cnu.edu'])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
    form = ContactForm()
    return render(request, "contact.html", context={'form': form})


def features_view(request, *args, **kwargs):
    return render(request, "features.html", {})


def register(request, name, uidb64, token):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('../')
        else:
            messages.error(request, "Unsuccessful Registration.")
            return render(request=request, template_name='register.html', context={'form': form})
    form = NewUserForm()
    return render(request=request, template_name="register.html", context={"form": form})


def login_view(request, *args, **kwargs):
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('../')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return render(request, 'home.html', {})


def about_view(request):
    return render(request, 'about.html', {})


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = OrgUser.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'PayNow',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'andrew.nguyen.18@cnu.edu', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html",
                  context={"password_reset_form": password_reset_form})
