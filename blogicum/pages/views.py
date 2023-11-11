from django.shortcuts import render
from django.views.generic import TemplateView


handler404 = 'pages.views.page_not_found'
handler403 = 'pages.views.csrf_failure'
handler500 = 'pages.views.server_error'

class RulesView(TemplateView):
    template_name = 'pages/rules.html'

class AboutPage(TemplateView):
    template_name = 'pages/about.html'

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request, reason=''):
    return render(request, 'pages/500.html', status=500)