import os
import django
import conf_django_location
from argparse import ArgumentParser
os.environ['DJANGO_SETTINGS_MODULE'] = 'c_server.settings'
django.setup()
from c_client.c_tools import djconf
from c_client.models import event, event_frame

parser = ArgumentParser()
parser.add_argument("-x", "--execute", dest="execute", action="store_true")
args = parser.parse_args()

fileset = os.listdir(djconf.getconfig('recordingspath'))
fileset_c = [item for item in fileset if (item[0] == 'C') and (item[-4:] == '.mp4')]
fileset_jpg = {item[:14] for item in fileset if (item[:2] == 'E_') and (item[-4:] == '.jpg')}
fileset_webm = {item[:14] for item in fileset if (item[:2] == 'E_') and (item[-5:] == '.webm')}
fileset_mp4 = {item[:14] for item in fileset if (item[:2] == 'E_') and (item[-4:] == '.mp4')}
fileset = fileset_jpg & fileset_webm & fileset_mp4
fileset_all = fileset_jpg | fileset_webm | fileset_mp4
dbset = event.objects.all()
dbset = {item.videoclip for item in dbset if item.videoclip[:2] == 'E_'}
print('*** Checking'+djconf.getconfig('recordingspath')+': ***')
print(len(fileset_c), 'Temporary Files')
print(len(fileset_jpg), 'JPG Files')
print(len(fileset_webm), 'WEBM Files')
print(len(fileset_mp4), 'MP4 Files')
print('Correct Lines:')
print('---',len(fileset & dbset), '---')
print('Missing DB Lines:')
print(fileset_all - dbset)
print('---',len(fileset_all - dbset), '---')
print('Missing Files:')
print(dbset - fileset)
print('---', len(dbset - fileset), '---')
if args.execute:
  print('***  Cleaning up  ***')
  event.objects.filter(numframes=0).delete()
  for item in (fileset_c):
    filename = djconf.getconfig('recordingspath')+item
    print('Deleting file:', filename)
    os.remove(filename)
  for item in (fileset_all - dbset):
    for ext in ['jpg', 'webm', 'mp4']:
      filename = djconf.getconfig('recordingspath')+item+'.'+ext
      if os.path.exists(filename):
        print('Deleting file:', filename)
        os.remove(filename)
  for item in (dbset - fileset):
	  print('Removing video from DB line(s):', item)
	  event.objects.filter(videoclip=item).update(videoclip='')
print('')
print('*** Checking event table against event_frame table: ***')
eventset = event.objects.all()
eventset = {item.id for item in eventset}
eventframeset = event_frame.objects.all()
eventframeset = {item.event_id for item in eventframeset}
print('Correct Lines:')
print('---',len(eventset & eventframeset), '---')
print('Missing Events:')
print(eventframeset - eventset)
print('---',len(eventframeset - eventset), '---')
print('Missing Frames:')
print(eventset - eventframeset)
print('---',len(eventset - eventframeset), '---')
if args.execute:
  print('***  Cleaning up  ***')
  for item in (eventframeset - eventset):
    print('Removing event_frame line from DB:', item)
    event_frame.objects.filter(event_id=item).delete()
  for item in (eventset - eventframeset):
    myevent = event.objects.get(id=item)
    if len(myevent.videoclip) < 3: 
      print('Removing event line(s) from DB:', item)
      myevent.delete()
print('')
print('*** Checking'+djconf.getconfig('schoolframespath')+': ***')
fileset = set()
for t in os.walk(djconf.getconfig('schoolframespath')):
  for item in t[2]:
    mystring = t[0]+'/'+item
    fileset.add(mystring[len(djconf.getconfig('schoolframespath')):])
dbset = event_frame.objects.all()
dbset = {item.name for item in dbset}
print('Correct Lines:')
print('---',len(fileset & dbset), '---')
print('Missing DB Lines:')
print(fileset - dbset)
print('---',len(fileset - dbset), '---')
print('Missing Files:')
print(dbset - fileset)
print('---', len(dbset - fileset), '---')
if args.execute:
  print('***  Cleaning up  ***')

  for item in (fileset - dbset):
    os.remove(djconf.getconfig('schoolframespath')+item)
    mydir = item.split('/')
    mydir = djconf.getconfig('schoolframespath') + mydir[0] + '/' + mydir[1]
    count = len(os.listdir(mydir))
    print('Deleting file:', item, ',', count, 'files remaining')
    if count == 0:
      os.removedirs(mydir)
      print('Deleting directory:', mydir)
    

  for item in (dbset - fileset):
    print('Deleting DB line:', item)
    event_frame.objects.filter(name=item).delete()

