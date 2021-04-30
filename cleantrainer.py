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

import os
import django
import conf_django_location
from argparse import ArgumentParser

os.environ['DJANGO_SETTINGS_MODULE'] = 'c_server.settings'
django.setup()
from c_client.models import school, trainframe

parser = ArgumentParser()
parser.add_argument("-s", "--school", dest="school", default = "0", type=int)
parser.add_argument("-x", "--execute", dest="execute", action="store_true")
args = parser.parse_args()

myschool = school.objects.get(id=args.school)

fileset = os.listdir(myschool.dir+'frames')
fileset = set(fileset)
dbset = trainframe.objects.filter(school=myschool.id)
dbset = {item.name[7:] for item in dbset}
print('*** Correct Lines: ***')
print('---',len(fileset & dbset), '---')
print('*** Missing DB Lines:')
print(fileset - dbset)
print('---',len(fileset - dbset), '---')
print('*** Missing Files:')
print(dbset - fileset)
print('---', len(dbset - fileset), '---')
if args.execute:
	print('***  Cleaning up  ***')

	for item in (fileset - dbset):
		print('Deleting file:', item)
		os.remove(myschool.dir+'frames/'+item)

	for item in (dbset - fileset):
		print('Deleting DB line:', item)
		trainframe.objects.filter(name='frames/'+item).delete()

