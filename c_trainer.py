#!/usr/bin/env python
# coding: utf-8

import sys
from os import environ
from time import sleep, time
import django
import conf_django_location
environ['DJANGO_SETTINGS_MODULE'] = 'c_server.settings'
django.setup()
from c_client.models import school
from c_client.train_mod import train_once
from c_client.c_tools import djconf
from c_client.l_tools import ts2mysqltime

school_nr = djconf.getconfigint('last_school', 1)
while True:
  timestr = ts2mysqltime(time())
  print(timestr)
  if((djconf.getconfig('startworking', '00:00:00') < timestr)
      and (djconf.getconfig('stopworking', '24:00:00') > timestr)):
    schools = school.objects.filter(active=1)
    counter = 0
    while schools[counter].id != school_nr:
      counter += 1
    counter += 1
    if counter >= len(schools):
      counter = 0	
      sleep(60)
    myschool = schools[counter]
    if train_once(myschool):
      djconf.setconfigint('last_school', myschool.id)
      sys.exit()
    else:
      school_nr = myschool.id
  else:
    sleep(60)
