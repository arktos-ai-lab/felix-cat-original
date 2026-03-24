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
import faqify

REMOTEBASE = "/home/ginstrom/webapps/static/AnalyzeAssist/%s"


def run_command(command):
    """Run the specified command using subprocess module"""

    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
    )

    for line in proc.stdout:
        print line.strip()
        sys.stdout.flush()

    for line in proc.stderr:
        print line.strip()
        sys.stdout.flush()

    assert not proc.returncode


def text2data(filename):
    lines = open(filename)
    keyvalpairs = (line.split("=") for line in lines if line)
    return dict((key.strip(), val.strip()) for key, val in keyvalpairs)


def getdata():
    versionfile = r"version.txt"
    assert os.path.exists(versionfile)

    return text2data(versionfile)


def main():
    versionfile = r"version.txt"
    assert os.path.exists(versionfile)

    versiondata = text2data(versionfile)

    installer = os.path.join("Setup", versiondata["filename"])
    print "Installer:", installer
    assert os.path.exists(installer)
    sys.stdout.flush()

    print "Signing setup file..."
    run_command(["sign.bat", installer])
    sys.stdout.flush()

    host = "ginstrom.webfactional.com"
    port = 22
    print "creating transport..."
    transport = paramiko.Transport((host, port))
    sys.stdout.flush()

    username = "ginstrom"
    password = "2fd97195"
    print "Connecting..."
    transport.connect(username=username, password=password)
    sys.stdout.flush()

    sftp = paramiko.SFTPClient.from_transport(transport)

    print "Uploading Analyze Assist setup..."
    sys.stdout.flush()
    remotepath = REMOTEBASE % versiondata["filename"]
    sftp.put(installer, remotepath)

    print "Uploading version file..."
    remotepath = REMOTEBASE % "version.txt"
    sftp.put(versionfile, remotepath)
    sys.stdout.flush()

    print "Uploading website files..."
    for filename in glob.glob("website/*.*"):
        print " ... uploading", filename
        sys.stdout.flush()
        remotepath = REMOTEBASE % os.path.split(filename)[-1]
        sftp.put(filename, remotepath)

    print "Closing connections..."
    sftp.close()
    transport.close()


if __name__ == "__main__":
    main()