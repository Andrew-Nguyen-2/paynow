"""paynow URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from organizations.backends import invitation_backend

from pages.views import (
    home_view,
    features_view,
    contact_view,
    about_view,
    login_view,
    logout_request,
    password_reset_request
)

from accounts.views import (
    account_home_view,
    account_budget_view,
    new_budget_view,
    show_budget_view,
    edit_budget_view,
    delete_budget_view,
    new_category_view,
    account_history_view,
    account_settings_view,
    update_password_view,
    update_password_success,
    update_username_view,
    update_username_success,
    account_footer_view,
    user_invite_register,
    member_payment_view,
    member_list,
    remove_member_view,
    send_invoice_view,
    make_a_payment,
    stripe_success,
    card_payment_success,
    stripe_credit_debit,
    StripeIntentView,
)

from accounts.export import (
    export_member_list_csv,
    export_member_list_excel,
    export_admin_history_csv,
    export_admin_history_excel,
    export_member_history_csv,
    export_member_history_excel,
)


urlpatterns = [
    path('', home_view, name='home'),
    path('features/', features_view, name='features'),
    path('contact/', contact_view, name='contact'),
    path('about/', about_view, name='about'),

    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_request, name='logout'),
    path(r'register/<str:name>/<uidb64>/<token>', user_invite_register, name='register'),

    # account urls
    path('accounts/', account_home_view, name='account_home'),
    path('accounts/history/', account_history_view, name='account_history'),
    path('accounts/payment/', member_payment_view, name='payment'),
    path('accounts/settings/', account_settings_view, name='account_settings'),
    path('accounts/about/', account_footer_view, name='account_about'),
    path('accounts/members_list/', member_list, name='member_list'),
    path('accounts/remove_members/', remove_member_view, name='remove_member'),
    path('accounts/send_invoice/', send_invoice_view, name='send_invoice'),
    path('accounts/make_payment/', make_a_payment, name='make_payment'),

    # account update urls
    path('accounts/update_password', update_password_view, name='update_password'),
    path('accounts/update_password_success/', update_password_success, name='update_password_success'),
    path('accounts/update_username', update_username_view, name='update_username'),
    path('accounts/update_username_success/', update_username_success, name='update_username_success'),

    # account budget urls
    path('accounts/budget/', account_budget_view, name='budget'),
    path('accounts/create_budget/', new_budget_view, name='create_budget'),
    path('accounts/edit_budget/', edit_budget_view, name='edit_budget'),
    path('accounts/add_category/', new_category_view, name='add_category'),
    path('accounts/budget_list/', show_budget_view, name='budget_list'),
    path('accounts/member_budget_list/', show_budget_view, name='member_budget_list'),
    path('accounts/delete_budget/', delete_budget_view, name='delete_budget'),

    # Stripe urls
    path('accounts/stripe_account_success/', stripe_success, name='stripe_account_success'),
    path('accounts/make_payment_card/', stripe_credit_debit, name='make_payment_card'),
    path('accounts/card_payment_success/', card_payment_success, name='card_payment_success'),
    path('accounts/create-payment-intent/', StripeIntentView.as_view()),

    # password reset urls
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'),
         name='password_reset_complete'),
    path("password_reset/", password_reset_request, name="password_reset"),

    # organization urls
    url(r'^invite/', include(invitation_backend().get_urls())),
    url(r'^organizations/', include('accounts.urls')),

    # admin export urls
    url(r'^export/members/csv/$', export_member_list_csv, name='export_members_csv'),
    url(r'^export/members/xls/$', export_member_list_excel, name='export_members_excel'),
    url(r'^export/history/csv/$', export_admin_history_csv, name='export_history_csv'),
    url(r'^export/history/xls/$', export_admin_history_excel, name='export_history_excel'),

    # member export urls
    url(r'^export/member/history/csv/$', export_member_history_csv, name='export_member_history_csv'),
    url(r'^export/member/history/xls/$', export_member_history_excel, name='export_member_history_excel'),

    path('admin/', admin.site.urls),
]
