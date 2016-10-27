from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from core.models import num_to_ip, ip_to_num
from .models import Dhcphosts_networks, Dhcphosts_hosts, User, new_ip
from django.conf import settings
from .forms import Dhcphosts_hostsForm
from netaddr import *


def dhcps(request):
    print request.POST
    order_by = request.GET.get('order_by', 'id')
    net_dhcp = Dhcphosts_networks.objects.all().order_by(order_by)
    paginator = Paginator(net_dhcp, settings.FEES_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        dhcp_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        dhcp_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        dhcp_page = paginator.page(paginator.num_pages)
    if int(page) > 5:
        start = str(int(page)-5)
    else:
        start = 1
    if int(page) < paginator.num_pages-5:
        end = str(int(page)+5+1)
    else:
        end = paginator.num_pages+1
    print dhcp_page
    page_range = range(int(start), int(end)),
    for p in page_range:
        page_list = p
    pre_end = dhcp_page.paginator.num_pages - 2
    if 'edit_dhcp' in request.POST:
        edit_dhcp = Dhcphosts_networks.objects.get(id=request.POST['edit_dhcp'])
        print edit_dhcp
    return render(request, 'dhcp.html', locals())


def user_dhcp(request, uid, host_id=None):
    net_dhcp = Dhcphosts_networks.objects.all()
    client = User.objects.get(id=uid)
    hosts = Dhcphosts_hosts.objects.filter(uid=uid)
    if host_id:
        host = Dhcphosts_hosts.objects.get(pk=host_id)
        change_dhcp_host = True
        dhcphosts_hostsform = Dhcphosts_hostsForm(instance=host, initial={'ip': num_to_ip(host.ip)})
        if request.method == 'POST':
            print request.POST
            if 'action' in request.POST and request.POST['action'] == 'cancel':
                return redirect(reverse('core:user_dhcp', kwargs={'uid': uid}))
            else:
                dhcphosts_hostsform = Dhcphosts_hostsForm(request.POST, instance=host)
                print dhcphosts_hostsform
                if dhcphosts_hostsform.is_valid():
                    form = dhcphosts_hostsform.save(commit=False)
                    mac = str(request.POST['mac']).strip()
                    if valid_mac(mac):
                        mac = EUI(mac, dialect=mac_unix_expanded)
                    if 'auto_select' in request.POST:
                        form.ip = str(ip_to_num(new_ip(request.POST['network'])))
                    else:
                        form.ip = str(ip_to_num(request.POST['ip']))
                    form.mac = mac
                    print form
                    form.save()
                    return redirect(reverse('core:user_dhcp', kwargs={'uid': uid}))
        else:
            print dhcphosts_hostsform.errors
    else:
        if 'mac_test' in request.POST:
            mac = str(request.POST['mac_test']).strip()
            response = None
            if response is None:
                error = 1
            print response
        host = None
        parsed_list = []
        for host in hosts:
            hostnames = host.hostname.split('_')
            if hostnames[-1].isdigit():
                parsed_list.append(int(hostnames[-1]))
        if len(parsed_list) == 0:
            dhcphosts_hostsform = Dhcphosts_hostsForm(initial={
                'hostname': str(client.login) + '_' + str(100 + 1),
                'uid': client.id,
                'disable': 0
            })
        else:
            dhcphosts_hostsform = Dhcphosts_hostsForm(initial={
                'hostname': str(client.login) + '_' + str(max(parsed_list) + 1),
                'uid': client.id,
                'disable': 0
            })
        if 'action' in request.POST and request.POST['action'] == 'add':
            dhcphosts_hostsform = Dhcphosts_hostsForm(request.POST)
            if dhcphosts_hostsform.is_valid():
                form = dhcphosts_hostsform.save(commit=False)
                mac = str(request.POST['mac']).strip()
                if valid_mac(mac):
                    mac = EUI(mac, dialect=mac_unix_expanded)
                if 'auto_select' in request.POST:
                    form.ip = str(ip_to_num(new_ip(request.POST['network'])))
                else:
                    form.ip = str(ip_to_num(request.POST['ip']))
                form.mac = mac
                form.save()
                return redirect(reverse('core:user_dhcp', kwargs={'uid': uid}))
    if 'action' in request.GET and request.GET['action'] == 'remove':
        host = Dhcphosts_hosts.objects.get(pk=request.GET['host_id'])
        host.delete()
        return redirect(reverse('core:user_dhcp', kwargs={'uid': uid}))
    return render(request, 'user_dhcp.html', locals())
