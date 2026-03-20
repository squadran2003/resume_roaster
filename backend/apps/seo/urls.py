from django.urls import path
from . import views

urlpatterns = [
    path("robots.txt", views.robots_txt),
    path("sitemap.xml", views.sitemap_xml),
    path("share/<str:token>/", views.share_scorecard, name="share-scorecard"),
]
