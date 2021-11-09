from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import NewOrgForm, NewUserAdminForm, UserInviteForm, NewUserForm, SendInvoiceForm
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import Account, OrgUser, InvoiceHistory

# Create your views here.


def account_home_view(request):
    user = request.user
    if user.is_owner:
        return render(request, "owner/admin_home.html", {})
    else:
        return render(request, "member/member_home.html", {})


def account_budget_view(request):
    user = request.user
    if user.is_owner:
        return render(request, "owner/budget.html", {})
    else:
        return render(request, "member/member_budget.html", {})


def account_history_view(request):
    user = request.user
    if user.is_owner:
        query_results = InvoiceHistory.objects.filter(organization_name=user.organization_name)
        return render(request, "owner/history.html", {'history': query_results})
    else:
        query_results = InvoiceHistory.objects.filter(username=user.username)
        return render(request, "member/member_history.html", {'history': query_results})


def account_settings_view(request):
    user = request.user
    if user.is_owner:
        return render(request, "owner/settings.html", {})
    else:
        return render(request, "member/member_settings.html", {})


def account_footer_view(request):
    user = request.user
    if user.is_owner:
        return render(request, "owner/admin_about.html", {})
    else:
        return render(request, "member/member_about.html", {})


def member_list(request):
    user = request.user
    query_results = OrgUser.objects.exclude(username=user.username).filter(organization_name=user.organization_name)
    return render(request, "owner/member_list.html", {'organization': user.organization_name, 'members': query_results})


def member_payment_view(request):
    return render(request, 'member/payment.html', {})


def send_invoice_view(request):
    user = request.user
    query_results = OrgUser.objects.exclude(username=user.username).filter(organization_name=user.organization_name)
    choices = [(mem.username, str(mem.username)) for mem in query_results]
    if request.method == "POST":
        form = SendInvoiceForm(choices, request.POST)
        if form.is_valid():
            selected_members = form.cleaned_data['member_list']
            invoice_amount = form.cleaned_data['amount']
            for memb in selected_members:
                member_user = OrgUser.objects.get(username=memb)
                member_user.amount_owed = member_user.amount_owed + invoice_amount
                member_user.save()
                name = memb
                description = form.cleaned_data['description']
                history = InvoiceHistory(
                    username=name, description=description,
                    invoice_amount=invoice_amount, organization_name=user.organization_name)
                history.save()
            return redirect("../members_list")
        else:
            messages.error(request, "Unsuccessfully Sent Invoice")
            return render(
                request, 'owner/invoice/send_invoice_form.html',
                {'organization': user.organization_name, 'members': query_results, 'form': form}
            )
    form = SendInvoiceForm(choices, request.POST)
    return render(
        request,
        'owner/invoice/send_invoice_form.html',
        {'organization': user.organization_name, 'members': query_results, 'form': form}
    )


def organization_register(request):
    if request.method == "POST":
        organization_form = NewOrgForm(request.POST)
        user_form = NewUserAdminForm(request.POST)
        if organization_form.is_valid() and user_form.is_valid():
            org = organization_form.save()
            user_form.instance.organization_id = org
            user_form.instance.organization_name = org.name
            user_form.instance.is_owner = True
            user = user_form.save()
            user_form.save()
            org.add_user(user)
            return redirect('../../accounts/login')
        else:
            messages.error(request, "Unsuccessful Registration.")
            return render(
                request,
                'organization_register.html',
                context={"organization_form": organization_form, "user_form": user_form}
            )
    organization_form = NewOrgForm(request.POST)
    user_form = NewUserAdminForm(request.POST)
    return render(
        request,
        'organization_register.html',
        context={"organization_form": organization_form, "user_form": user_form}
    )


def invite_new_users(request):
    user = request.user
    if request.method == "POST":
        form = UserInviteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['email']
            subject = "You've Been Invited!"
            email_template_name = "email/invitation_email"
            c = {
                "email": data,
                'domain': '127.0.0.1:8000',
                'site_name': 'PayNow',
                "oid": urlsafe_base64_encode(force_bytes(user.organization_id)),
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
                'organization': user.organization_name
            }
            email = render_to_string(email_template_name, c)
            try:
                send_mail(subject, email, 'paynow@gmail.com', [data], fail_silently=False, auth_password='')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect("../invite/sent")
    form = UserInviteForm(request.POST)
    org = user.organization_name
    return render(request, 'owner/invite_members.html', context={'form': form, 'organization': org})


def user_invite_register(request, name, uidb64, token):
    organization_name = name
    org = {
        'organization_name': organization_name,
    }
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            org = get_object_or_404(Account, name=organization_name)
            form.instance.organization_name = organization_name
            form.instance.organization_id = org
            form.instance.is_member = True
            form.save()
            return redirect('../../../accounts/login')
        else:
            form = NewUserForm(request.POST)
            messages.error(request, 'Unsuccessful Registration')
            return render(request, 'member_registration.html', context={'form': form, 'organization': org})
    form = NewUserForm()
    return render(request, 'member_registration.html', context={'form': form, 'organization': org})
