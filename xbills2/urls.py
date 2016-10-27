from django.conf.urls import include, url
from core.helpers import module_check

urlpatterns = [
    url(r'^api/', include('api.urls', 'api')),
    url(r'^admin/', include('core.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
if module_check('ipdhcp'):
    urlpatterns += url(r'^admin/dhcps/', include('ipdhcp.urls')),
