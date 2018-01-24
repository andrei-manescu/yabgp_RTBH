#!/usr/bin/python


from __future__ import print_function
import sys,os
import socket,struct
import subprocess
import json
import urllib2
import time
import os, getpass

#import smtplib
#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEText import MIMEText
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

print ('I\'m running as'+str(getpass.getuser()))
SPAM_DIR_MONITOR=['/var/home/vmail/domain.com/user/Maildir/.Junk/cur']
URL = 'http://%s:%s/v1/peer/%s/send/update'
USER = 'yabgp_api_user'
PASS = 'yabgp_api_pass'

bin_ls = os.popen("which ls").read().strip()
bin_egrep = os.popen("which egrep").read().strip()
bin_awk = os.popen("which awk").read().strip()
bin_xargs = os.popen("which xargs").read().strip()
bin_mv = os.popen("which mv").read().strip()


def get_api_opener_v1(url, username, password):
    """
    get the http api opener with base url and username,password

    :param url: http url
    :param username: username for api auth
    :param password: password for api auth
    """
    # create a password manager
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

    # Add the username and password.
    password_mgr.add_password(None, url, username, password)

    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    return opener

def send_email(list_of_ips):
	sendmail = os.popen("which sendmail").read().strip()
	msg = MIMEText('\n'.join(list_of_ips))
	msg["From"] = "changeme@gmail.com"
	msg["To"] = "changeme@gmail.com"
	msg["Subject"] = str(len(list_of_ips))+" New Spam IPs added"
	#p = Popen([sendmail, "-t", "-oi"], stdin=PIPE)
	p = Popen(['/usr/sbin/sendmail', "-t", "-oi", "-f changeme@gmail.com"], stdin=PIPE)
	p.communicate(msg.as_string())

def get_data_from_agent(url, username, password, method='GET', data=None):
    """
    HTTP interaction with yabgp rest api
    :param url:
    :param username:
    :param password:
    :param method:
    :param data:
    :return:
    :return:
    """
    # build request
    if data:
        data = json.dumps(data)
    request = urllib2.Request(url, data)
    request.add_header("Content-Type", 'application/json')
    request.get_method = lambda: method
    opener_v1 = get_api_opener_v1(url, username, password)
    try:
        res = json.loads(opener_v1.open(request).read())
        return True
    except Exception:
        return False
def interval():
    time.sleep(1)

def linecount(spammer_ips):
    return len(spammer_ips)

def send_update(spammer_ips):
    #print(spammer_ips)
    # get the message count
    message_count = float(linecount(spammer_ips))
    url = 'http://{bind_host}:{bind_port}/v1/peer/{peer_ip}/send/update'
    url = url.format(bind_host='10.0.0.1', bind_port='8801', peer_ip='<IP of BGP neighbor of yabgp>')
    bar_length = 50
    message_pass_send = 0
    send_success = 0
    send_failed = 0
    current_percent = 0.00
    percent_step = 0.01
    #with open(CONF.badhosts) as f:

    #sys.stdout.write("\rPercent: [%s] %.2f%%" % ('' + ' ' * bar_length, current_percent))
    current_percent += percent_step
    sys.stdout.flush()
    print ("")
    #for _subnet in f.xreadlines():
    new_spammer_ips = []
    for ip in spammer_ips:
        ip = ip+'/32'
        new_spammer_ips.append(ip)

    spammer_ips = new_spammer_ips
    #print(spammer_ips)
    attributes = {	'1' : 0,
    				'2' : [[2, [65531]]],
    				'3' : '192.0.2.101',
    				'8' : ['PLANNED_SHUT'],
    				}

    post_data = {
        'nlri': spammer_ips,
        'attr': attributes
    }
    res = get_data_from_agent(url, USER, PASS, 'POST', post_data)
    if res:
        send_success += 1
        interval()
    else:
        send_failed += 1
    while message_pass_send/message_count >= current_percent/100:
        hashes = '#' * int(message_pass_send/message_count * bar_length)
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\rPercent: [%s] %.2f%%" % (hashes + spaces, current_percent))
        sys.stdout.flush()
        current_percent += percent_step
    message_pass_send += 1
    hashes = '#' * bar_length
    spaces = ''
    sys.stdout.write("\rPercent: [%s] %.2f%%"%(hashes + spaces, 100.00))
    sys.stdout.flush()
    print('\nTotal messages:   %s' % int(message_count))
    print('Success send out: %s' % len(spammer_ips))
    print('Failed send out:  %s' % send_failed)


if __name__ == '__main__':
    try:
		for dir in SPAM_DIR_MONITOR:
			spam_files = os.popen(bin_ls+" -1 "+dir+"/1* | "+bin_egrep+" -v '.SPAM.' | "+bin_xargs+" -I '{}' "+bin_egrep+" '^Received: from [1-9][0-9.]{4,15} by mail.ivorde.ro' {} | "+bin_awk+" '{print $3}' | "+bin_egrep+" -vE '^10\.|^192\.168|^172\.16'").read()

			if len(spam_files.strip().splitlines()) > 0:
				send_email(spam_files.strip().splitlines())
				send_update(spam_files.strip().splitlines())
				#os.system(bin_ls+" "+dir+" | "+bin_egrep+" -v '^2_' | "+bin_xargs+" -I '{}' "+bin_mv+" "+dir+"/{} "+dir+"/2_{}")
				os.system(bin_ls+" "+dir+" | "+bin_egrep+" -v '.SPAM.' | while read file; do newfile=`echo $file | sed 's/hostname/SPAM.hostname/g'`; mv "+dir+"/$file "+dir+"/$newfile; done ")

    except KeyboardInterrupt:
        sys.exit()
