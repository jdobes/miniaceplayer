#!/usr/bin/env python

# MiniAcePlayer
# Attempt to connect to the AceStream given on the command-line, open 
# the user's favourite movie player to play the stream

import pexpect,time,sys,urllib2,json,pprint,subprocess,socket

# holds our config
from miniaceconfig import MiniAceConfig

# mainly for testing
pp = pprint.PrettyPrinter()

# quit if there aren't enough arguments
if len(sys.argv) == 1:
   print "No arguments!"
   sys.exit(1)

# read and format the PID from command-line
pid = sys.argv[1]
if pid.startswith('acestream://'): pid = pid[12:]

print "Starting with PID " + pid + "..."

# try to connect to the AceStreamEngine

try:
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.settimeout(1)
   s.connect((MiniAceConfig.acehost, MiniAceConfig.aceport))
   s.close
except:
   # run the acestreamengine, if we can't connect
   print "AceStreamEngine not running!"
   print "Starting AceStreamEngine..."
   ace = subprocess.Popen(['/usr/bin/acestreamengine','--client-gtk'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   time.sleep(10)

print "AceStreamEngine running!"

# open a telnet session to the acestreamengine
child = pexpect.spawn ('telnet ' + MiniAceConfig.acehost + ' ' + str(MiniAceConfig.aceport))
child.logfile = sys.stdout
child.timeout = MiniAceConfig.aceconntimeout

# if we can't get a telnet session before the timeout just quit
conn = child.expect([pexpect.TIMEOUT, "Escape character.+"])
if conn == 0:
   print "Timeout connecting to AceStreamEngine!"
   sys.exit(1)

# give us a bit of time to send the next command
time.sleep(2)

# we don't bother sending the API version - it doesn't seem to mind!
child.sendline ('HELLOBG')

# expect the auth key, we extract it from the output and give back the
# valid output
child.expect ('key=.*')
# print child.before
key = child.after.strip()
key = key[4:]
# print "Key = " + key
rup = 'READY key=' + urllib2.urlopen("http://valdikss.org.ru/tv/key.php?key=" + key, timeout=10).read()
# print rup
child.sendline(rup)

# expect to be authorised, send our user data too
# TODO: authentication timeout
child.expect('AUTH.*')
child.sendline('USERDATA [{"gender": "' + str(MiniAceConfig.acesex) + '"}, {"age": "' + str(MiniAceConfig.aceage) + '"}]')

time.sleep(2)

# get the file info from the PID
# TODO: load PID timeout
child.sendline('LOAD PID ' + pid)
child.expect('"files.*infohash')

# we basically print the first file
# TODO: error checking here, check file exists
files = child.after.strip()
files = '{' + files[:-11] + '}'
# print files
afiles = json.loads(files)
# pp.pprint(afiles['files'][0][0])
file0 = afiles['files'][0][0]
print "Loading " + file0 + "..."

time.sleep(2)

# so now we attempt to start streaming the PID
child.sendline('START PID ' + pid + ' 0')
child.timeout = 99999999999999

#SPLIT STATUS main:prebuf
#SPLIT 93
#SPLIT 2147483648
#SPLIT 0
#SPLIT 0
#SPLIT 157
#SPLIT 0
#SPLIT 0
#SPLIT 8
#SPLIT 0
#SPLIT 1966080
#SPLIT 0
#SPLIT 0

# this loop determines the progress of the streaming

t = 0
lpcnt = 0
pcnt = 0
while True:
   # every 1 seconds we try to find the URL
   print "TIMER: " + str(t)
   print "LPCNT: " + str(lpcnt)
   print "PCNT:  " + str(pcnt)
   
   # the buffering has been taking too long, stop trying to stream and close process
   if t == MiniAceConfig.acebuffernoprogresstimeout:
      print "Buffering taking too long!"
      child.sendline ('STOP')
      time.sleep(2)
      child.sendline ('SHUTDOWN')
      time.sleep(2)
      sys.exit(1)
   
   child.timeout = 1
   i = child.expect([pexpect.TIMEOUT, 'START http.*'])
   if i == 0:
      # no URL found, we try to determine if the STATUS was sent instead
      # print child.before
      out = child.before
      astat = out.splitlines()
      last = astat[len(astat)-1]
      # we get the last line of buffered output, check if it is a STATUS
      if last.startswith('STATUS'):
         print "LAST: " + last
         astat = last.split(';')
         # pp.pprint(astat)
         if len(astat) == 13:
            # the percentage loaded is the 2nd element in the array
            # print "PCNT: " + astat[1]
            # if the percentage has changed update the variables and reset the timer
            if astat[1] != pcnt:
               lpcnt = pcnt
               pcnt = astat[1]
               t = 0
            #for e in astat:
            #   print "SPLIT " + str(e)
   else:
      # so the URL was found, print it here and stop the loop
      url = child.after.strip()
      url = url.split()[1]
      print "URL = " + url
      break
   t = t + 1

# call the media player to play the URL
subprocess.call([MiniAceConfig.aceplayer, url])

# the must have quit the media player, stop our session with acestreamengine

child.sendline ('SHUTDOWN')
