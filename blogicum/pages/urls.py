from django.urls import path
from .views import AboutPage, RulesView
from . import views

app_name = 'pages'


urlpatterns = [
    path('about/', AboutPage.as_view(), name='about'),
    path('rules/', RulesView.as_view(), name='rules'),
]
