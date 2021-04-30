#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2021 Ludger Hellerhoff, ludger@booker-hellerhoff.de
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

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
