from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    #User-Related URLs
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^register', views.register_view, name='register'),
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^$', views.user_profile, name='user_profile'),
    url(r'^profile', views.user_profile, name='user_profile'),
    url(r'^home', views.home, name='home'),
    url(r'^new_petition', views.new_petition_view, name='new_petition')
]