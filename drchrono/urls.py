from django.conf.urls import include, url
from django.views.generic import TemplateView

import views
guid_pattern = '(?P<instance_guid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'

urlpatterns = [
    url(r'^$', views.main, name='home'),

    url(r'^admin$', views.settings, name='admin'),
    # kiosk views
    url(r'^%s/kiosk$' %guid_pattern, views.kiosk, name='kiosk'),
    # confirm registered information
    url(r'^%s/checkin$' %guid_pattern, views.checkin, name='checkin'),
    # Update personal infor
    url(r'^%s/update$' %guid_pattern, views.update, name='update'),
    # handle demographic update and check in
    url(r'^%s/complete$' %guid_pattern, views.complete, name='complete'),

    # doctor url
    url(r'^doctor$', views.doctor, name='doctor'),
    url(r'^internal$', views.internal, name='internal'),

    url(r'^about$', views.about, name='about'),
    url(r'^logout$', views.leave, name='logout'),
    url(r'^%s/error$' % guid_pattern, views.error, name='error'),

    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
