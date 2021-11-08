
from django.contrib.auth.decorators import login_required
from django.urls import include
from django.urls import path
from django.contrib.auth import views as auth_views

from organizations.views import base as views
from organizations.views import default as v
from .views import (
    organization_register,
    invite_new_users
)

# app_name = "orgs"

urlpatterns = [
    path(
        "",
        view=login_required(v.OrganizationList.as_view()),
        name="organization_list",
    ),
    path(
        "add/",
        organization_register,
        name="organization_add",
    ),
    path(
        "invite/",
        invite_new_users,
        name="organization_invite"
    ),
    path(
        "invite/sent",
        auth_views.PasswordResetDoneView.as_view(template_name='email/invitation_sent.html'),
        name="invitation_sent"
    ),
    path(
        "<int:organization_pk>/",
        include(
            [
                # path(
                #     "invite/",
                #     invite_new_users,
                #     name="organization_invite"
                # ),
                path(
                    "",
                    view=login_required(views.BaseOrganizationDetail.as_view()),
                    name="organization_detail",
                ),
                path(
                    "edit/",
                    view=login_required(views.BaseOrganizationUpdate.as_view()),
                    name="organization_edit",
                ),
                path(
                    "delete/",
                    view=login_required(views.BaseOrganizationDelete.as_view()),
                    name="organization_delete",
                ),
                path(
                    "people/",
                    include(
                        [
                            path(
                                "",
                                view=login_required(
                                    views.BaseOrganizationUserList.as_view()
                                ),
                                name="organization_user_list",
                            ),
                            path(
                                "add/",
                                view=login_required(
                                    views.BaseOrganizationUserCreate.as_view()
                                ),
                                name="organization_user_add",
                            ),
                            path(
                                "<int:user_pk>/remind/",
                                view=login_required(
                                    views.BaseOrganizationUserRemind.as_view()
                                ),
                                name="organization_user_remind",
                            ),
                            path(
                                "<int:user_pk>/",
                                view=login_required(
                                    views.BaseOrganizationUserDetail.as_view()
                                ),
                                name="organization_user_detail",
                            ),
                            path(
                                "<int:user_pk>/edit/",
                                view=login_required(
                                    views.BaseOrganizationUserUpdate.as_view()
                                ),
                                name="organization_user_edit",
                            ),
                            path(
                                "<int:user_pk>/delete/",
                                view=login_required(
                                    views.BaseOrganizationUserDelete.as_view()
                                ),
                                name="organization_user_delete",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
