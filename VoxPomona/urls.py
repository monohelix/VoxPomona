from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
	url(r'^$', RedirectView.as_view(pattern_name='home', permanent=False)),

    #User-Related URLs
    url(r'^login', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^register', views.register_view, name='register'),
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^profile', views.user_profile, name='user_profile'),
    url(r'^home', views.home, name='home'),
    url(r'^new_petition', views.new_petition_view, name='new_petition'),
    url(r'^view_petition/([0-9]+)/$', views.view_petition_view, name='view_petition'),
    url(r'^petition/([0-9]+)/$', views.display_petition),
    url(r'^search', views.search_petition),
    url(r'^delete_clause', views.delete_clause),
    url(r'^add_comment', views.add_comment),
]