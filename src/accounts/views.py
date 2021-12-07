import math
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import (
    NewOrgForm, NewUserAdminForm, UserInviteForm, EditBudgetForm, RemoveMemberForm, UpdateUsernameForm,
    NewUserForm, SendInvoiceForm, CreateBudgetForm, AddCategoryForm, DeleteBudgetForm
)
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Account, OrgUser, InvoiceHistory, Budget, Category
from django.contrib.auth.decorators import login_required
import stripe
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

stripe.api_key = \
    "sk_test_51Jv695K2Lmw2gpPZOH9NhVSgKPXmIk1VxM3uk7Adp7g6fmPnlrepDybV9WE8lnc8S2vdXuMAdDTK8qpMITqm7kqF00prqvFU24"

pb_key = 'pk_test_51Jv695K2Lmw2gpPZocxZoNag8Z6pv9JU8VoQv7knF7gLxDfWp6n6CnCboOOVnLCVyXn8XwVSnYi9W9jM03EXmcla00CtSt0JBk'


# Create your views here.


def account_home_view(request):
    user = request.user
    if user.is_owner:
        if not user.has_stripe_account:
            new_account = stripe.Account.create(type="standard", email=user.email)
            user.stripe_account_id = new_account.id
            user.save()
            link = stripe.AccountLink.create(
                account=new_account.id,
                refresh_url="HTTP://127.0.0.1:8000",
                return_url="HTTP://127.0.0.1:8000/accounts/stripe_account_success/",
                type="account_onboarding",
            )
            return render(request, "owner/admin_home.html", {'link': link.url})
        return render(request, "owner/admin_home.html", {})
    else:
        return render(request, "member/member_home.html", {})


def stripe_success(request):
    user = request.user
    user.has_stripe_account = True
    user.save()
    return render(request, "owner/stripe_account_success.html", {})


def account_budget_view(request):
    user = request.user
    org = Account.objects.get(name=user.organization_name)
    expected_collected_amount = org.expected_amount - org.collected_amount
    if user.is_owner:
        return render(request, "owner/budget.html",
                      {'organization': org, 'expected_collected_amount': expected_collected_amount})
    else:
        return render(request, "member/member_budget.html",
                      {'organization': org, 'expected_collected_amount': expected_collected_amount})


def new_budget_view(request):
    user = request.user
    org = Account.objects.get(name=user.organization_name)
    if request.method == 'POST':
        form = CreateBudgetForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            budget = Budget(title=title, organization_name=org)
            budget.save()
            # return render(request, "owner/create_budget.html", {'organization': org, 'budget': budget})
            return redirect("../budget/")
    form = CreateBudgetForm()
    return render(request, "owner/set_budget.html", {'organization': org, 'form': form})


def new_category_view(request):
    user = request.user
    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            amount = form.cleaned_data['amount']
            budget = form.cleaned_data['budget']
            category = Category(title=title, amount=amount, budget=budget)
            category.save()
            return redirect("../create_budget/")
    form = AddCategoryForm()
    return render(request, "owner/add_category.html", {'form': form})


def edit_budget_view(request):
    user = request.user
    org = Account.objects.get(name=user.organization_name)
    query_results = Budget.objects.filter(organization_name=user.organization_name)
    choices = [(bud.title, str(bud.title)) for bud in query_results]
    if request.method == 'POST':
        form = EditBudgetForm(choices, request.POST)
        if form.is_valid():
            budget = form.cleaned_data['budget_list']
            category = form.cleaned_data['category']
            amount = form.cleaned_data['amount']
            for bud in budget:
                b = get_object_or_404(Budget, title=bud)
                b.total += amount
                b.save()
                c = Category(title=category, amount=amount, budget=bud, organization_name=org)
                c.save()
            return redirect("../budget_list/")
        else:
            messages.error(request, "Unsuccessfully Created Category")
            return render(
                request, 'owner/budget.html',
                {'organization': user.organization_name, 'budgets': query_results, 'form': form}
            )
    form = EditBudgetForm(choices, request.POST)
    return render(request, "owner/edit_budget.html", {'organization': org, 'budgets': query_results, 'form': form})


def show_budget_view(request):
    user = request.user
    org = Account.objects.get(name=user.organization_name)
    budgets = Budget.objects.filter(organization_name=user.organization_name)
    categories = Category.objects.filter(organization_name=org)
    total_amount = {}
    leftover = {}
    for cat in categories:
        total_amount[cat.budget] = 0
    for cat in categories:
        total_amount[cat.budget] += cat.amount
    for key in total_amount:
        leftover[key] = org.collected_amount - total_amount[key]
    return render(request, "owner/budget_list.html",
                  {'budgets': budgets, 'organization': org, 'user': user,
                   'categories': categories, 'total_amount': total_amount, 'leftover': leftover})


def delete_budget_view(request):
    user = request.user
    org = Account.objects.get(name=user.organization_name)
    budgets = Budget.objects.filter(organization_name=user.organization_name)
    categories = Category.objects.filter(organization_name=org)
    choices = [(bud.title, str(bud.title)) for bud in budgets]
    if request.method == "POST":
        form = DeleteBudgetForm(choices, request.POST)
        if form.is_valid():
            selected_budgets = form.cleaned_data['budget_list']
            for bud in selected_budgets:
                b = get_object_or_404(Budget, title=bud)
                for cat in categories:
                    print("inside for cat")
                    if cat.budget in selected_budgets:
                        print("inside if cat.budget")
                        c = get_object_or_404(Category, title=cat.title)
                        c.delete()
                b.delete()
            return redirect("../budget_list/")
    form = DeleteBudgetForm(choices, request.POST)
    return render(request, "owner/delete_budget.html", {'form': form})


def account_history_view(request):
    user = request.user
    if user.is_owner:
        query_results = InvoiceHistory.objects.filter(organization_name=user.organization_name)
        return render(request, "owner/history.html", {'history': query_results})
    else:
        query_results = InvoiceHistory.objects.filter(username=user.username)
        return render(request, "member/member_history.html", {'history': query_results})


@login_required
def account_settings_view(request):
    user = request.user
    if user.is_owner:
        return render(request, "owner/settings.html", {})
    else:
        return render(request, "member/member_settings.html", {})


def update_password_view(request):
    log = request.user
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return render(request, "owner/change_password_success.html", {})
    form = PasswordChangeForm(request.user)
    if log.is_owner:
        return render(request, "owner/change_password.html", {'form': form})
    else:
        return render(request, "member/change_password.html", {'form': form})


def update_password_success(request):
    user = request.user
    if user.is_owner:
        return render(request, "owner/change_password_success.html", {})
    else:
        return render(request, "member/change_password_success.html", {})


def update_username_view(request):
    user = request.user
    if request.method == "POST":
        form = UpdateUsernameForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['new_username']
            user.username = name
            user.save()
            update_session_auth_hash(request, user)
            return redirect("../accounts/update_username_success/")
    form = UpdateUsernameForm()
    if user.is_owner:
        return render(request, "owner/change_username.html", {'form': form})
    else:
        return render(request, "member/change_username.html", {'form': form})


def update_username_success(request):
    user = request.user
    if user.is_owner:
        return render(request, "owner/change_username_success.html", {})
    else:
        return render(request, "member/change_username_success.html", {})


def account_footer_view(request):
    user = request.user
    if user.is_owner:
        return render(request, "owner/admin_about.html", {})
    else:
        return render(request, "member/member_about.html", {})


def member_list(request):
    user = request.user
    query_results = OrgUser.objects.exclude(username=user.username).filter(organization_name=user.organization_name)
    return render(request, "owner/member_list.html",
                  {'organization': user.organization_name,
                   'members': query_results, 'total_members': query_results.count()})


def remove_member_view(request):
    user = request.user
    org = Account.objects.get(name=user.organization_name)
    members = OrgUser.objects.exclude(username=user.username).filter(organization_name=user.organization_name)
    choices = [(mem.username, str(mem.username)) for mem in members]
    if request.method == "POST":
        form = RemoveMemberForm(choices, request.POST)
        if form.is_valid():
            selected_members = form.cleaned_data['member_list']
            for memb in selected_members:
                u = get_object_or_404(OrgUser, username=memb)
                if u.amount_owed > 0:
                    org.expected_amount = org.expected_amount - u.amount_owed
                    org.save()
                u.delete()
            return redirect("../members_list/")
    form = RemoveMemberForm(choices, request.POST)
    return render(request, "owner/remove_member.html", {'members': members, 'form': form})


def member_payment_view(request):
    user = request.user
    amount_owed = user.amount_owed
    return render(request, 'member/payment.html', {'amount': amount_owed})


def make_a_payment(request):
    user = request.user
    amount_owed = user.amount_owed
    return render(request, 'member/make_payment.html', {'amount': amount_owed})


def stripe_credit_debit(request):
    user = request.user
    admin = OrgUser.objects.filter(organization_name=user.organization_name, is_owner=True)
    acc_id = str(admin[0].stripe_account_id)
    return render(request, 'member/card_payment.html', {'amount': user.amount_owed, 'data': acc_id})


@method_decorator(csrf_exempt, name='dispatch')
class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        admin = OrgUser.objects.filter(organization_name=user.organization_name, is_owner=True)
        try:
            intent = stripe.PaymentIntent.create(
                amount=math.trunc(user.amount_owed * 100),
                currency='usd',
            )
            return JsonResponse({'clientSecret': intent['client_secret']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


def card_payment_success(request):
    user = request.user
    org = Account.objects.get(name=user.organization_name)
    history = InvoiceHistory(
        username=user.username, description='Paid',
        invoice_amount=user.amount_owed, organization_name=user.organization_name
    )
    org.collected_amount = org.collected_amount + user.amount_owed
    user.amount_paid = user.amount_paid + user.amount_owed
    user.amount_owed = 0
    org.save()
    user.save()
    history.save()
    return render(request, 'member/card_payment_success.html', {})


def send_invoice_view(request):
    user = request.user
    org = Account.objects.get(name=user.organization_name)
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
                org.expected_amount = org.expected_amount + invoice_amount
                org.save()
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


def create_stripe_account(request):
    user_username = request.user.username
    link = stripe.AccountLink.create(
        account=user_username,
        refresh_url="http://127.0.0.1:8000/",
        return_url="http://127.0.0.1:8000/accounts/login/",
        type="account_onboarding",
    )
    return link["url"]


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
