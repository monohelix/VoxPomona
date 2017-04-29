from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
	url(r'^$', RedirectView.as_view(pattern_name='home', permanent=False)),

    # user-releated urls
    url(r'^login', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^register', views.register_view, name='register'),
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^profile', views.user_profile, name='user_profile'),

    url(r'^accounts/', include('registration.backends.hmac.urls')),

    # general purpose urls
    url(r'^home', views.home, name='home'),
    url(r'^petition/([0-9]+)/$', views.display_petition),
    url(r'^search', views.search_results),

    # petition/clause modification url
    url(r'^new_petition', views.new_petition_view, name='new_petition'),
    url(r'^view_petition/([0-9]+)/$', views.view_petition_view, name='view_petition'),
    url(r'^finalize_petition', views.finalize_petition),
    url(r'^delete_clause', views.delete_clause),

    # change-related urls
    url(r'^add_change', views.add_change),
    url(r'^accept_change', views.accept_change),
    url(r'^reject_change', views.reject_change),
    url(r'^upvote_change', views.upvote_change),
    url(r'^downvote_change', views.downvote_change),

    # comment-related urls
    url(r'^add_comment', views.add_comment),
    url(r'^delete_comment', views.delete_comment),
]