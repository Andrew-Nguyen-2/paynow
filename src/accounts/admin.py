from django.contrib import admin
from django.contrib.auth.models import User, Group
from organizations.models import Organization, OrganizationUser, OrganizationOwner
from .forms import AccountUserForm
from .models import Account, AccountUser, InvoiceHistory, OrgUser


class AccountUserAdmin(admin.ModelAdmin):
    form = AccountUserForm


class OrgUserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Personal Information',
         {'fields': ['first_name', 'last_name',
                     'email', 'username', 'password',
                     'amount_owed', 'amount_paid',
                     'stripe_account_id']}
         ),
        ('Organization Information', {'fields': ['organization_id', 'organization_name']}),
        ('User Information', {'fields': ['date_joined', 'last_login', 'is_owner', 'is_member', 'has_stripe_account']}),
        ('Permissions', {'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']})
    ]
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('has_stripe_account', 'stripe_account_id')


class AccountAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Organization Information',
         {'fields': ['name', 'slug', 'date_joined', 'collected_amount', 'expected_amount']}),
        ('Permissions', {'fields': ['is_active']}),
    ]
    readonly_fields = ('id', 'collected_amount', 'expected_amount')


class InvoiceHistoryAdmin(admin.ModelAdmin):
    fieldsets = [
        ('User Information', {'fields': ['username', 'organization_name']}),
        ('Invoice Information', {'fields': ['description', 'date_sent', 'invoice_amount']})
    ]
    readonly_fields = ('username', 'organization_name', 'description', 'date_sent', 'invoice_amount')


admin.site.unregister(Organization)
admin.site.unregister(OrganizationUser)
admin.site.unregister(OrganizationOwner)
admin.site.register(OrgUser, OrgUserAdmin)
admin.site.register(User)
admin.site.register(Account, AccountAdmin)
admin.site.register(AccountUser, AccountUserAdmin)
admin.site.register(InvoiceHistory, InvoiceHistoryAdmin)
