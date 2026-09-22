from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("quotation/", views.quote_request, name="quote_request"),
    path("quotation/<uuid:reference>/", views.quote_success, name="quote_success"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/projects/<int:pk>/", views.staff_project_detail, name="staff_project_detail"),
]

