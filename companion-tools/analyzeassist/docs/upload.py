# coding: UTF8
"""
Sign and upload the TagAssist installer

"""

import os
import subprocess
import paramiko
import jinja2 as jinja
import glob
import sys

REMOTEBASE = "/home/ginstrom/webapps/static/CountAnything/manual/%s"
CSSBASE = "/home/ginstrom/webapps/static/CountAnything/manual/css/%s"
IMGBASE = "/home/ginstrom/webapps/static/CountAnything/manual/img/%s"
HOST = "ginstrom.webfactional.com"
PORT = 22

USERNAME = "ginstrom"
PASSWORD = "2fd97195"


def main():
    print "creating transport..."
    transport = paramiko.Transport((HOST, PORT))

    print "Connecting..."
    transport.connect(username=USERNAME, password=PASSWORD)

    sftp = paramiko.SFTPClient.from_transport(transport)

    print "Uploading files..."
    for filename in glob.glob("output/*.html"):
        print " ... uploading", filename
        remotepath = REMOTEBASE % os.path.split(filename)[-1]
        sftp.put(filename, remotepath)
        sys.stdout.flush()

    for filename in glob.glob("output/css/*.*"):
        print " ... uploading", filename
        remotepath = CSSBASE % os.path.split(filename)[-1]
        sftp.put(filename, remotepath)
        sys.stdout.flush()

    for filename in glob.glob("output/img/*.png"):
        print " ... uploading", filename
        remotepath = IMGBASE % os.path.split(filename)[-1]
        sftp.put(filename, remotepath)
        sys.stdout.flush()

    print "Closing connections..."
    sftp.close()
    transport.close()


if __name__ == "__main__":
    main()
