# -*- encoding: utf-8 -*-
import csv
import json
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from dv.helpers import Hangup
from .auth_backend import AuthBackend
from .models import User, Payment, Fees, Dv, UserPi, Street, House, District, Dv_calls, Server, ErrorsLog, Dv_log, Admin, num_to_ip, AdminSettings, \
    AdminLog, ip_to_num, Group, Company
from .forms import AdministratorForm, SearchForm, SearchFeesForm, SearchPaymentsForm, ClientForm, DvForm, UserPiForm, AdministratorAddForm
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password
import helpers
import platform
import psutil
import datetime
from django.core import serializers


def custom_redirect(url_name, *args, **kwargs):
    from django.core.urlresolvers import reverse
    import urllib
    url = reverse(url_name, args=args)
    params = urllib.urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


@login_required()
def index(request, settings=settings):
    ip_list_r = []
    ip_list_db = []
    sys = platform.platform()
    cpu_load_list = psutil.cpu_percent(interval=1, percpu=True)
    root_disk_usage = psutil.disk_usage('/')
    for cpu in cpu_load_list:
        print cpu
    return render(request, 'index.html', locals())

@login_required()
def servers(request):
    if 'sessions' in request.GET:
        sessions = request.GET['sessions']
        session_list = Dv_calls.objects.filter(nas=request.GET['sessions'])
        all = session_list.count()
        guest = session_list.filter(guest=1).count()
        paginator = Paginator(session_list, 20)
        page = request.GET.get('page', 1)
        try:
            sespage = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            sespage = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            sespage = paginator.page(paginator.num_pages)
        if int(page) > 5:
            start = str(int(page)-5)
        else:
            start = 1
        if int(page) < paginator.num_pages-5:
            end = str(int(page)+5+1)
        else:
            end = paginator.num_pages+1
        page_range = range(int(start), int(end)),
        for p in page_range:
            page_list = p
        pre_end = sespage.paginator.num_pages - 2
    servers = Server.objects.all()
    return render(request, 'servers.html', locals())

@login_required()
def client_errors(request, uid):
    try:
        client = User.objects.get(id=uid)
    except User.DoesNotExist:
        return render(request, '404.html', locals())
    order_by = request.GET.get('order_by', '-date')
    user_errors = ErrorsLog.objects.filter(user=client.login).order_by(order_by)
    paginator = Paginator(user_errors, settings.USER_ERRORS_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        errors = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        errors = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        errors = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = errors.paginator.num_pages - 2
    if 'xml' in request.GET:
        xml_data = serializers.serialize("xml", errors)
        return render(request, 'base.xml', {'data': xml_data}, content_type="text/xml")
    if 'csv' in request.GET:
        return helpers.export_to_csv(request, errors, fields=('id', 'login'), name='login')
    return render(request, 'user_errors.html', locals())

@login_required()
def client_statistics(request, uid):
    try:
        client = User.objects.get(id=uid)
    except User.DoesNotExist:
        return render(request, '404.html', locals())
    order_by = request.GET.get('order_by', '-start')
    user_statistics = Dv_log.objects.filter(uid=uid).order_by(order_by)
    paginator = Paginator(user_statistics, settings.USER_ERRORS_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        statistics = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        statistics = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        statistics = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = statistics.paginator.num_pages - 2
    if 'xml' in request.GET:
        xml_data = serializers.serialize("xml", statistics)
        return render(request, 'base.xml', {'data': xml_data}, content_type="text/xml")
    if 'csv' in request.GET:
        return helpers.export_to_csv(request, statistics, fields=('id', 'login'), name='login')
    return render(request, 'user_statistics.html', locals())


@login_required()
# @permission_required('users.can_vote')
def search(request):

    all_table_choices = [
        'user_id__id',
        'user_id__login',
        'fio',
        'user_id__bill__deposit',
        'district',
        'street',
        'location',
        'kv',
        'user_id__credit',
        'user_id__disable',
        'user_id__deleted',
    ]
    default_table_choices = [
        'user_id__login',
        'fio',
        'user_id__bill__deposit',
        'user_id__credit',
        'user_id__disable',
        'user_id__deleted',
    ]
    search_form = SearchForm()
    search_fees_form = SearchFeesForm()
    search_payments_form = SearchPaymentsForm()
    districts = District.objects.all()
    filter_params = {}
    includes = []
    # try:
    #     admin_settings = AdminSettings.objects.get(admin_id=request.user.id, object='USERS_LIST')
    #     default_table_choices = admin_settings.setting.lower().replace(' ', '').split(',')
    # except AdminSettings.DoesNotExist:
    #     admin_settings = AdminSettings.objects.create(
    #         admin_id=request.user.id,
    #         object='USERS_LIST',
    #         setting=', '.join(default_table_choices)
    #     )

    if request.method == 'POST':
        includes = [', '.join(request.POST.getlist('includes'))]
        if any('user_id__login' in s for s in includes):
            pass
        else:
            includes.append('user_id__login')
        if any('user_id__deleted' in s for s in includes):
            pass
        else:
            includes.append('user_id__deleted')
        # admin_settings.setting = ', '.join(includes)
        # admin_settings.admin_id = request.user.id
        # admin_settings.save()
        return redirect(request.get_full_path())
    try:
        search = request.GET.get('search')
    except:
        search = None
    search_type = request.GET.get('search_type', '1')
    if search_type == '1':
        search_form = SearchForm(request.GET, initial=request.GET)
        if request.GET.get('search'):
            print request.GET
            order_by = request.GET.get('order_by', 'user_id__login')
            if 'uid' in request.GET and request.GET['uid'] != '':
                try:
                    user = User.objects.get(id=request.GET['uid'])
                    return redirect('core:client', uid=user.id)
                except User.DoesNotExist:
                    error = 'User not found'
                    return render(request, 'search.html', locals())
            else:
                if 'login' in request.GET and request.GET['login'] != '':
                    filter_params.update({'user_id__login__contains': request.GET['login']})
                if 'district' in request.GET and request.GET['district'] != '':
                    city = District.objects.get(id=request.GET['district'])
                    if 'street' not in request.GET or request.GET['street'] == '0' or request.GET['street'] == '':
                        city_street = Street.objects.values('id').filter(district_id=request.GET['district'])
                        filter_params['street_id__in'] = city_street
                    else:
                        street = Street.objects.values_list('id').get(id=request.GET['street'])
                        filter_params.update({'street_id': street})
                        if 'house' in request.GET and request.GET['house'] != '' and request.GET['house'] != '0':
                            house = House.objects.values_list('id').get(id=request.GET['house'])
                            filter_params.update({'location_id': house})
                if 'flat' in request.GET and request.GET['flat'] != '':
                    filter_params.update({'kv': request.GET['flat']})
                if 'disabled' in request.GET and request.GET['disabled'] != '':
                    filter_params.update({'user_id__disable': 1})
                try:
                    userpi = UserPi.objects.filter(**filter_params).order_by(order_by)
                    if userpi.count() == 0:
                        error = 'User not found'
                    elif userpi.count() == 1:
                        for u in userpi:
                            return redirect('core:client', uid=u.user_id.id)
                    else:
                        all = userpi.count()
                        disabled = userpi.filter(user_id__disable=1).count()
                        not_active = userpi.filter(user_id__disable=2).count()
                        deleted = userpi.filter(user_id__deleted=1).count()
                        paginator = Paginator(userpi, 100)
                        page = request.GET.get('page', 1)
                        try:
                            users = paginator.page(page)
                        except PageNotAnInteger:
                            users = paginator.page(1)
                        except EmptyPage:
                            users = paginator.page(paginator.num_pages)
                        if int(page) > 5:
                            start = str(int(page)-5)
                        else:
                            start = 1
                        if int(page) < paginator.num_pages-5:
                            end = str(int(page)+5+1)
                        else:
                            end = paginator.num_pages+1
                        page_range = range(int(start), int(end)),
                        for p in page_range:
                            page_list = p
                        pre_end = users.paginator.num_pages - 2
                        print locals()
                    return render(request, 'search.html', locals())
                except User.DoesNotExist:
                    error = 'User not found'
                    return render(request, 'search.html', locals())
    elif search_type == '2':
        print 'company search'
    elif search_type == '3':
        search_fees_form = SearchFeesForm(request.GET, initial=request.GET)
        if request.GET.get('search'):
            order_by = request.GET.get('order_by', 'uid__login')
            if 'login' in request.GET and request.GET['login'] != '':
                filter_params.update({'uid__login__contains': request.GET['login']})
            if 'group' in request.GET and request.GET['group'] != '':
                filter_params.update({'uid__gid__id': request.GET['group']})
            print filter_params
            try:
                fees_list = Fees.objects.filter(**filter_params).order_by(order_by)
                if fees_list.count() == 0:
                    error = 'Fees not found'
                # elif userpi.count() == 1:
                #     for u in userpi:
                #         return redirect('core:client', uid=u['user_id'])
                else:
                    all = fees_list.count()
                    disabled = fees_list.filter(uid__disabled=1).count()
                    not_active = fees_list.filter(uid__disabled=2).count()
                    deleted = fees_list.filter(uid__deleted=1).count()
                    paginator = Paginator(fees_list, settings.FEES_PER_PAGE)
                    page = request.GET.get('page', 1)
                    try:
                        fees = paginator.page(page)
                    except PageNotAnInteger:
                        fees = paginator.page(1)
                    except EmptyPage:
                        fees = paginator.page(paginator.num_pages)
                    if int(page) > 5:
                        start = str(int(page)-5)
                    else:
                        start = 1
                    if int(page) < paginator.num_pages-5:
                        end = str(int(page)+5+1)
                    else:
                        end = paginator.num_pages+1
                    page_range = range(int(start), int(end)),
                    for p in page_range:
                        page_list = p
                    pre_end = fees.paginator.num_pages - 2
                return render(request, 'search.html', locals())
            except Fees.DoesNotExist:
                error = 'User not found'
                return render(request, 'search.html', locals())
    elif search_type == '4':
        search_payments_form = SearchPaymentsForm(request.GET, initial=request.GET)
        order_by = request.GET.get('order_by', 'uid__login')
        if 'login' in request.GET and request.GET['login'] != '':
            filter_params.update({'uid__login__contains': request.GET['login']})
        if 'group' in request.GET and request.GET['group'] != '':
            filter_params.update({'uid__gid__id': request.GET['group']})
        try:
            payments_list = Payment.objects.filter(**filter_params).order_by(order_by)
            if payments_list.count() == 0:
                error = 'Payments not found'
            # elif userpi.count() == 1:
            #     for u in userpi:
            #         return redirect('core:client', uid=u['user_id'])
            else:
                all = payments_list.count()
                disabled = payments_list.filter(uid__disable=1).count()
                not_active = payments_list.filter(uid__disable=2).count()
                deleted = payments_list.filter(uid__deleted=1).count()
                paginator = Paginator(payments_list, settings.PAYMENTS_PER_PAGE)
                page = request.GET.get('page', 1)
                try:
                    payments = paginator.page(page)
                except PageNotAnInteger:
                    payments = paginator.page(1)
                except EmptyPage:
                    payments = paginator.page(paginator.num_pages)
                if int(page) > 5:
                    start = str(int(page)-5)
                else:
                    start = 1
                if int(page) < paginator.num_pages-5:
                    end = str(int(page)+5+1)
                else:
                    end = paginator.num_pages+1
                page_range = range(int(start), int(end)),
                for p in page_range:
                    page_list = p
                pre_end = payments.paginator.num_pages - 2
            return render(request, 'search.html', locals())
        except Payment.DoesNotExist:
            error = 'Payments not found'
            return render(request, 'search.html', locals())
    if 'global_search' in request.GET:
        print request.GET['global_search']
        search = 1
        try:
            userpi = UserPi.objects.filter(Q(user_id=request.GET['global_search']) | Q(phone2__icontains=request.GET['global_search']))
            print userpi
        except:
            userpi = UserPi.objects.filter(Q(user_id__login__icontains=request.GET['global_search']) |
                                           Q(street__name__icontains=request.GET['global_search']) |
                                           Q(city__icontains=request.GET['global_search']) |
                                           Q(fio__icontains=request.GET['global_search']))
        if userpi.count() == 0:
            error = 'User not found'
        elif userpi.count() == 1:
            for u in userpi:
                return redirect('core:client', uid=u.user_id.id)
        else:
            all = userpi.count()
            disabled = userpi.filter(user_id__disable=1).count()
            not_active = userpi.filter(user_id__disable=2).count()
            deleted = userpi.filter(user_id__deleted=1).count()
            paginator = Paginator(userpi, 100)
            page = request.GET.get('page', 1)
            try:
                users = paginator.page(page)
            except PageNotAnInteger:
                users = paginator.page(1)
            except EmptyPage:
                users = paginator.page(paginator.num_pages)
            if int(page) > 5:
                start = str(int(page) - 5)
            else:
                start = 1
            if int(page) < paginator.num_pages - 5:
                end = str(int(page) + 5 + 1)
            else:
                end = paginator.num_pages + 1
            page_range = range(int(start), int(end)),
            for p in page_range:
                page_list = p
            pre_end = users.paginator.num_pages - 2
        return render(request, 'search.html', locals())
    return render(request, 'search.html', locals())


@login_required()
def client(request, uid):
    if 'hangup' in request.GET:
        hangup = Hangup(request.GET['nas_id'], request.GET['port_id'], request.GET['acct_session_id'], request.GET['user_name'])
    try:
        client = User.objects.get(id=uid)
    except User.DoesNotExist:
        return render(request, '404.html', locals())
    if client.disable == 1:
        disable = 0
    else:
        disable = 1
    client_form = ClientForm(instance=client)
    if 'client_form' in request.POST:
        client_form = ClientForm(request.POST, instance=client)
        print client_form
        if client_form.is_valid():
            print 'oky'
        print client_form.errors
    dv = Dv.objects.get(user=uid)
    dv_form = DvForm(instance=dv, initial={'ip': num_to_ip(dv.ip), 'netmask': num_to_ip(dv.netmask)})
    user_pi = UserPi.objects.get(user_id=uid)
    user_pi_form = UserPiForm(instance=user_pi, initial={'district': user_pi.street.district_id})
    if 'user_pi' in request.POST:
        user_pi_form = UserPiForm(request.POST, instance=user_pi)
        print user_pi_form
    # streets = Street.objects.all()
    # houses = House.objects.all()
    # group = Group.objects.all()
    # if helpers.module_check('olltv'):
        # from olltv.models import Iptv, IptvDevice, IptvDeviceType
        # from olltv.api import oll_user_info, oll_check_bundle, olltv_auth
        # try:
        #     user_olltv = Iptv.objects.get(uid=uid)
        #     olltv_exist = True
        #     user_olltv_dev = IptvDevice.objects.filter(uid=uid)
        #     try:
        #         auth = olltv_auth()
        #     except:
        #         auth = None
        #     if auth != None:
        #         user_info = oll_user_info(account=uid, hash=auth['hash'])
        #         get_user_info = user_info['data']
        #         tp_list_dict = user_info['data']['bought_subs']
        #         tp_count = user_info['tp_count']
        #         tp_list = []
        #         if tp_count < 1:
        #             tp_list = None
        #         else:
        #             for tp in tp_list_dict:
        #                 # check_bundle
        #                 check_bundle = oll_check_bundle(account=client.id, tp=tp['sub_id'], hash=auth['hash'])
        #                 if check_bundle['mess'] == 'Error':
        #                     messages.warning(request, check_bundle)
        #                 else:
        #                     get_bundle_status = check_bundle['data']
        #                     tp.update({'status': get_bundle_status})
        #                     tp_list.append(tp)
        # except Iptv.DoesNotExist:
        #     olltv_exist = False
    if 'show_password' in request.GET:
        user_password = client.get_hash_password
    else:
        user_password = ''
    # if helpers.module_check('claims'):
    #     from claims.models import Claims
    #     claims = Claims.objects.filter(uid=uid, state=1)
    return render(request, 'user_edit.html', locals())


@login_required()
def client_payments(request, uid):
    out_sum = 0
    order_by = request.GET.get('order_by', '-date')
    try:
        client = User.objects.get(id=uid)
    except User.DoesNotExist:
        return render(request, '404.html', locals())
    payments_list = Payment.objects.values('id', 'uid__login', 'uid__id', 'date', 'dsc', 'sum', 'last_deposit', 'aid__login', 'method').filter(uid=client.id).order_by(order_by)
    for payment in payments_list:
        out_sum += payment['sum']
    paginator = Paginator(payments_list, settings.PAYMENTS_PER_PAGE)
    page = request.GET.get('page', 1)
    if helpers.module_check('olltv'):
        olltv_module = True
    else:
        olltv_module = False
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        payments = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        payments = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = payments.paginator.num_pages - 2
    if 'del' in request.GET:
        del_payment = Payment.objects.get(id=request.GET['del'])
        print request.GET
        log = AdminLog(
            actions='test',
            datetime=datetime.datetime.now(),
            ip=ip_to_num('127.0.0.1'),
            user_id=uid,
            admin_id=40,
        )
        #log.save()
        #print log.admin
        #del_payment.delete()
    if 'xml' in request.GET:
        xml_data = serializers.serialize("xml", payments)
        return render(request, 'base.xml', {'data': xml_data}, content_type="text/xml")
    if 'csv' in request.GET:
        return helpers.export_to_csv(request, payments, fields=('id', 'uid'), name='login')
    return render(request, 'user_payments.html', locals())


@login_required()
def client_fees(request, uid):
    out_sum = 0
    order_by = request.GET.get('order_by', '-date')
    try:
        client = User.objects.get(id=uid)
    except User.DoesNotExist:
        return render(request, '404.html', locals())
    fees_list = Fees.objects.filter(uid=client.id).order_by(order_by)
    for ex_fees in fees_list:
        out_sum = out_sum + ex_fees.sum
    paginator = Paginator(fees_list, settings.FEES_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        fees = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        fees = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        fees = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = fees.paginator.num_pages - 2
    if 'del' in request.GET:
        return redirect(request.GET['return_url'])
    if 'export_submit' in request.POST:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
        writer = csv.writer(response)
        writer.writerow(['Service', 'Sum'])
        for ex_fees in fees_list.filter(uid=uid, date__range=(request.POST['Last'], request.POST['First'])):
            writer.writerow([ex_fees.dsc.encode('utf-8'), ex_fees.sum])
            out_sum = out_sum + ex_fees.sum
        writer.writerow(['', out_sum])
        return response
    if 'xml' in request.GET:
        xml_data = serializers.serialize("xml", fees)
        return render(request, 'base.xml', {'data': xml_data}, content_type="text/xml")
    if 'csv' in request.GET:
        return helpers.export_to_csv(request, fees, fields=('id', 'uid'), name='login')
    return render(request, 'user_fees.html', locals())


def clients(request):
    filter_by = request.GET.get('users_status', '0')
    order_by = request.GET.get('order_by', 'login')
    # users_list = User.objects.all().order_by(order_by)
    users_list = User.objects.values('id', 'login', 'user_pi__fio', 'bill__deposit', 'credit', 'disable', 'deleted').order_by(order_by)
    if filter_by == '1':
        users_list = users_list.filter(bill__deposit__gte=0, disable=False, deleted=False,)
    if filter_by == '2':
        users_list = users_list.filter(bill__deposit__lt=0, credit=0)
    if filter_by == '3':
        users_list = users_list.filter(disable=True, deleted=False)
    if filter_by == '4':
        users_list = users_list.filter(deleted=True)
    if filter_by == '5':
        users_list = users_list.filter(credit__gt=0)
    all = users_list.count()
    end = users_list.filter(deleted=1).count()
    disabled = users_list.filter(disable=1).count()
    deleted = users_list.filter(deleted=1).count()
    paginator = Paginator(users_list, 100)
    page = request.GET.get('page', 1)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = users.paginator.num_pages - 2
    if 'xml' in request.GET:
        xml_data = serializers.serialize("xml", users)
        return render(request, 'base.xml', {'data': xml_data}, content_type="text/xml")
    if 'csv' in request.GET:
        return helpers.export_to_csv(request, users, fields=('id', 'login'), name='login')
    return render(request, 'users.html', locals())


@login_required()
def payments(request):
    order_by = request.GET.get('order_by', '-date')
    payments_list = Payment.objects.values('id', 'uid__login', 'uid__id', 'date', 'dsc', 'sum', 'last_deposit', 'aid__login', 'method').order_by(order_by)
    paginator = Paginator(payments_list, settings.PAYMENTS_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        payments = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        payments = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = payments.paginator.num_pages - 2
    if 'xml' in request.GET:
        xml_data = serializers.serialize("xml", payments)
        return render(request, 'base.xml', {'data': xml_data}, content_type="text/xml")
    if 'csv' in request.GET:
        return helpers.export_to_csv(request, payments, fields=('id', 'sum'), name='payments')
    return render(request, 'payments.html', locals())


@login_required()
def fees(request):
    out_sum = 0
    order_by = request.GET.get('order_by', '-date')
    fees_list = Fees.objects.values('id', 'uid__id', 'uid__login', 'date', 'dsc', 'sum', 'last_deposit', 'method__name', 'aid__login', ).order_by(order_by)
    paginator = Paginator(fees_list, settings.FEES_PER_PAGE)
    page = request.GET.get('page', 1)
    # for ex_fees in fees_list:
    #     out_sum += ex_fees.sum
    try:
        fees = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        fees = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        fees = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = fees.paginator.num_pages - 2
    return render(request, 'fees.html', locals())


@login_required()
def company(request):
    r_company = 1
    order_by = request.GET.get('order_by', 'name')
    m_company = Company.objects.values('id', 'name', 'bill__deposit', 'credit', 'registration', 'disable').annotate(clients=Count('clients')).order_by(order_by)
    paginator = Paginator(m_company, 50)
    page = request.GET.get('page', 1)
    try:
        company = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        company = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        company = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = company.paginator.num_pages - 2
    if 'xml' in request.GET:
        xml_data = serializers.serialize("xml", company)
        return render(request, 'base.xml', {'data': xml_data}, content_type="text/xml")
    if 'csv' in request.GET:
        return helpers.export_to_csv(request, company, fields=('id', 'bill'), name='bill')
    if 'change' in request.GET:
        r_company = 2
        if request.GET['change'] !='':
            edit_company= Company.objects.get(id=request.GET['change'])
    if 'company_id' in request.GET:
        user = User.objects.filter(company_id=request.GET['company_id'])
        user_js = serializers.serialize('json', user)
        return HttpResponse(user_js)
    return render(request, 'company.html', locals())


@login_required()
def group(request):
    order_by = request.GET.get('order_by', 'id')
    group = Group.objects.values('id', 'name', 'descr').annotate(user_group=Count('user_group')).order_by(order_by)
    paginator = Paginator(group, 50)
    page = request.GET.get('page', 1)
    print request.GET
    try:
        group = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        group = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        group = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = group.paginator.num_pages - 2
    if 'xml' in request.GET:
        xml_data = serializers.serialize("xml", company)
        return render(request, 'base.xml', {'data': xml_data}, content_type="text/xml")
    if 'csv' in request.GET:
        return helpers.export_to_csv(request, company, fields=('id', 'bill'), name='bill')
    if 'user_list' in request.GET:
        user = User.objects.filter(gid_id=request.GET['user_list'])
        return render(request, 'table_user_liset.html', locals())
    return render(request, 'group.html', locals())

def user_login(request):
    context = RequestContext(request)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = AuthBackend().authenticate(username=username, password=password)
        if user is None:
            error = u'Ім’я користувача або пароль введені невірно'
            return render(request, 'login.html', locals())
        elif user is not None:
            if not user.disable:
                user.backend = 'core.auth_backend.AuthBackend'
                login(request, user)
                # message = RedisMessage('<span style="color: blue; opacity: 0.5;">%s: %s is logged in</span>' % (datetime.datetime.now().strftime("%H:%M:%S"), username))  # create a welcome message to be sent to everybody
                # RedisPublisher(facility='global_chat', broadcast=True).publish_message(message)
                return HttpResponseRedirect(request.GET['next'])
            else:
                error = u'Account is locked'
                return render(request, 'login.html', locals())
        else:
            # Bad login details were provided. So we can't log the user in.
            error = "Invalid login details: {0}, {1}".format(username, password)
            return render(request, 'login.html', locals())
    else:
        return render(request, 'login.html', locals())


@login_required()
def logout_view(request):
    # message = RedisMessage('<span style="color: red; opacity: 0.5;">%s: %s is logged out</span>' % (datetime.datetime.now().strftime("%H:%M:%S"), request.user.login))  # create a welcome message to be sent to everybody
    # RedisPublisher(facility='global_chat', broadcast=True).publish_message(message)
    logout(request)
    return redirect('core:index')


@login_required()
def user_group(request, uid):
    user = User.objects.get(id=uid)
    return render(request, 'user_payments.html', locals())


@login_required()
def user_company(request, uid):
    user = User.objects.get(id=uid)
    return render(request, 'user_payments.html', locals())


@login_required()
def administrators(request):
    admins = Admin.objects.all()
    admin_form = AdministratorForm()
    if request.method == 'POST':
        if 'admin_remove' in request.POST:
            admin = Admin.objects.get(id=request.POST['uid'])
            # admin.delete()
        elif 'admin_add' in request.POST:
            print 'admin_add'
            print request.POST
            admin_form = AdministratorForm(request.POST)
            if admin_form.is_valid():
                print 'valid'
                # admin_form.save()
    return render(request, 'administrators.html', locals())


@login_required()
def administrator_edit(request, uid):
    try:
        admin = Admin.objects.get(pk=uid)
    except Admin.DoesNotExist:
        return render(request, '404.html', locals())
    else:
        admin_form = AdministratorForm(instance=admin)
        if request.method == 'POST':
            admin_form = AdministratorForm(request.POST, instance=admin)
            if admin_form.is_valid():
                print admin_form
                # admin_form.save()
                return redirect('core:administrators')
        return render(request, 'admin_edit.html', locals())


@login_required()
def administrators_add(request):
    # admins = Admin.objects.all()
    admin_form = AdministratorAddForm()
    if request.method == 'POST':
        print request.POST
        admin_form = AdministratorAddForm(request.POST)
        if admin_form.is_valid():
            # admin_form = admin_form.save(commit=False)
            # admin_form.password = make_password(request.POST['password'])
            # admin_form.save()
            return redirect(reverse('core:administrators'))
    return render(request, 'administrators_add.html', locals())


def test(request, template=".html"):
    """
    Show a room.
    """
    # context = {"room": get_object_or_404(ChatRoom, slug=slug)}
    return render(request, template, locals())


@csrf_exempt
def chat(request):
    admins = helpers.get_online()
    if request.method == 'POST' and request.POST != '':
        print request.POST
        if request.POST['message']:
            pass
            # message = RedisMessage('<span style="">%s(%s): %s</span>' % (request.user.login, datetime.datetime.now().strftime("%H:%M:%S"), request.POST['message']))  # create a welcome message to be sent to everybody
            # RedisPublisher(facility=request.POST['room'], broadcast=True).publish_message(message)
        else:
            print 'no message'
    return render(request, 'chat.html', locals())


def monitoring_servers(request):
    servers_list = []
    servers = Server.objects.filter(disable=0)
    for s in servers:
        servers_list.append({'server': s.name, 'id': s.id, 'clients_count': Dv_calls.objects.filter(nas_id=s.id).count()})
    if 'order_by' in request.GET:
        servers_list = sorted(servers_list, key=lambda k: k['id'], reverse=True)
    if 'list' in request.GET:
        dv = Dv_calls.objects.filter(nas_id=request.GET['list'])
        print dv
    return render(request, 'monitoring_servers.html', locals())

