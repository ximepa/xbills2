import random
import csv
from xml.dom.minidom import Document

from django.conf import settings
import os
from django.shortcuts import HttpResponse
from .models import Admin
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.cache import cache
from django.core import serializers
from django.shortcuts import render


def randomDigits(digits):
    lower = 10**(digits-1)
    upper = 10**digits - 1
    return random.randint(lower, upper)


def module_check(module):
    modules = settings.INSTALLED_APPS
    module_path = os.path.join(settings.BASE_DIR,  module)
    if module in modules and os.path.exists(module_path):
        return True
    else:
        return False


def export_to_csv(request, queryset, fields, name):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=%s.csv' % name
    # opts = queryset.model._meta
    # field_names = [field.name for field in opts.fields]
    writer = csv.writer(response)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])
    return response


def export_to_xml(request, queryset):
    xml_data = serializers.serialize("xml", queryset)
    print xml_data
    return render(request, 'base.xml', {'data': xml_data}, content_type="text/xml")


def get_online():
    ids = cache.get('online-now')
    return Admin.objects.filter(id__in=ids)