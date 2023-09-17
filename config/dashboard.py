from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard


class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.children.append(
            modules.LinkList(
                _("Important Links"),
                children=[
                    {
                        "title": _("API Documentation"),
                        "url": reverse("api_docs"),
                        "external": True,
                    },
                    {
                        "title": _("IXD Labs Home Page"),
                        "url": "https://ixdlabs.com",
                        "external": True,
                    },
                    {
                        "title": _("Github Repository"),
                        "url": "https://github.com/ixdlabs/django-api-template",
                        "external": True,
                    },
                ],
                column=2,
                order=0,
            )
        )
        self.children.append(modules.RecentActions(_("Recent Actions"), 10, column=2, order=1))
