from django.conf.urls import include, url
from core.helpers import module_check
from django.conf import settings

urlpatterns = [
    url(r'^api/', include('api.urls', 'api')),
    url(r'^admin/', include('core.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

if module_check('ipdhcp'):
    urlpatterns += url(r'^admin/dhcps/', include('ipdhcp.urls')),
