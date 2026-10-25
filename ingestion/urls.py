from django.urls import path

from . import views

# Each app keeps its own list of URLs. The project's config/urls.py
# "includes" this list under a prefix (we use "api/").
urlpatterns = [
    # path(<url pattern>, <view to call>, name=<label for reverse lookups>)
    path("health/", views.health_check, name="health-check"),
    path("ping/", views.ping_req, name="ping-check"),

]
