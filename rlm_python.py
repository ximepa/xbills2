#! /usr/bin/env python
#
# Python module

import radiusd
import MySQLdb
import sys
import os
sys.path.append(os.path.abspath("/home/ximepa/PycharmProjects/xbills/xbills"))
import settings_local
import rauth

def rpairstodict(p):
  return dict((x, y) for x, y in p)

def instantiate(p):
  radiusd.radlog(radiusd.L_INFO, '*** instantiate ***')
  print p
  # return 0 for success or -1 for failure

def authenticate(p):
  radiusd.radlog(radiusd.L_INFO, '*** authenticate ***')
  print p
  return radiusd.RLM_MODULE_OK

def authorize(p):
  value = rpairstodict(p)
  #print value
  for keys,values in value.items():
    print str(keys) + ':' + str(values)
  #print value['User-Name']
  #print '+++++++++++++++'
  #print settings_local.BILLSDB
  #print rauth.get_nas_info(1, 1)
  radiusd.radlog(radiusd.L_INFO, '*** radlog call in authorize ***')
  db = MySQLdb.connect(settings_local.RADHOST, settings_local.RADUSER, settings_local.RADPASSWD, settings_local.RADDB)
#  msql_ver_cur = db.cursor()
#  msql_ver_cur.execute("SELECT VERSION()")
#  mysql_version = msql_ver_cur.fetchone()[0]
#  print mysql_version
#  print '=========='
  cursor = db.cursor()
  cursor.execute('SELECT DECODE(password, "%s") FROM users WHERE id="%s"' % (settings_local.ENCRYPT_KEY, value['User-Name']))
  password = cursor.fetchone()[0]
#  cursor.close()
  db.close()
  reply = (('Acct-Interim-Interval', '300'), ('Framed-IP-Address', '192.168.3.1'), ('Framed-IP-Netmask', '255.255.255.255'))
  config = ( ('User-Name', '%s' % value['User-Name']), ('Cleartext-Password', password) )
#  print '--------------------------'
#  print rpairstodict(p)
#  print rauth.auth(rpairstodict(p))
#  print '--------------------------'
#  print
#  print radiusd.config
#  print
#  print "================"
#  print radiusd.RLM_MODULE_OK
#  print radiusd.RLM_MODULE_REJECT
#  return radiusd.RLM_MODULE_OK
  return (radiusd.RLM_MODULE_OK, reply, config)

def preacct(p):
  radiusd.radlog(radiusd.L_INFO, '*** preacct ***')
  print p
  return radiusd.RLM_MODULE_OK

def accounting(p):
  rpairs = rpairstodict(p)
  db = MySQLdb.connect(settings_local.RADHOST, settings_local.RADUSER, settings_local.RADPASSWD, settings_local.RADDB)
  cursor = db.cursor()
  cursor.execute('SELECT DECODE(password, "%s") FROM users WHERE id="%s"' % (settings_local.ENCRYPT_KEY, rpairs['User-Name']))
  password = cursor.fetchone()[0]
  radiusd.radlog(radiusd.L_INFO, '*** accounting ***')
  print "*** accounting ***"
  radiusd.radlog(radiusd.L_INFO, '*** radlog call in accounting (0) ***')
  print
  #print p
  reply = ( ('Reply-Message', 'Hello %s' % rpairs['User-Name']), )
  config = ( ('User-Name', '%s' % rpairs['User-Name']), ('Cleartext-Password', password), ('Framed-IP-Address', '192.168.3.1') )
  for keys,values in rpairs.items():
    print str(keys) + ':' + str(values)
  #return (radiusd.RLM_MODULE_OK, reply, config)
  return radiusd.RLM_MODULE_OK

def pre_proxy(p):
  print "*** pre_proxy ***"
  print p
  return radiusd.RLM_MODULE_OK

def post_proxy(p):
  print "*** post_proxy ***"
  print p
  return radiusd.RLM_MODULE_OK

def post_auth(p):
  print "*** post_auth ***"
  rpairs = rpairstodict(p)
  #print p
  for keys,values in rpairs.items():
    print str(keys) + ':' + str(values)
  return radiusd.RLM_MODULE_OK

def recv_coa(p):
  print "*** recv_coa ***"
  print p
  return radiusd.RLM_MODULE_OK

def send_coa(p):
  print "*** send_coa ***"
  print p
  return radiusd.RLM_MODULE_OK


def detach():
  print "*** goodbye from example.py ***"
  return radiusd.RLM_MODULE_OK

def dhcp(p):
  radiusd.radlog(radiusd.L_INFO, '*** DHCP radius ***')
  print p
