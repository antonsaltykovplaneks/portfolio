from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings


admin.site.site_header = "porfolio | Admin console"
# admin.site.enable_nav_sidebar = False


urlpatterns = [
    path("superadmin/doc/", include("django.contrib.admindocs.urls")),
    path("superadmin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("core.urls")),
]

# For debug mode only
if settings.CONFIGURATION == "dev":
    # Turn on debug toolbar
    import debug_toolbar

    urlpatterns += [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
    ]
