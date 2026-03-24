# coding: UTF8
"""
Build the installer program

Calls buildinstaller.bat to get the job done.

"""
import os
import subprocess
import sys
import make_setup
import model
from datetime import date
import glob
from jinja2 import Template
import faqify


def run_command(command):
    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
    )

    for line in proc.stdout:
        print line.strip().decode("sjis").encode("utf-8")
        sys.stdout.flush()

    for line in proc.stderr:
        print line.strip().decode("sjis").encode("utf-8")
        sys.stderr.flush()

    assert not proc.returncode


def gen_docs_sub(src, dst, data):
    filenames = glob.glob(src)
    for filename in filenames:
        template = Template(open(filename).read().decode("utf-8"))
        base = os.path.split(filename)[-1]
        out = open(os.path.join(dst, base), "w")
        out.write(template.render(data).encode("utf-8"))
        out.close()


def generate_docs(data):
    faqtext = open("website-templates/faq.txt").read()
    data["faq"] = faqify.faqify(faqtext)
    gen_docs_sub("templates/*.*", "res", data)
    gen_docs_sub("website-templates/*.html", "website", data)


def make_version_file(data):
    out = open("version.txt", "w")
    for pair in data.items():
        print >> out, "%s=%s" % pair
    out.close()


def make_setup_script(data):
    text = open("AnalyzeAssist.tpl").read()
    out = open("AnalyzeAssist.iss", "w")
    print >> out, text % dict(version=model.VERSION)
    out.close()


def get_data():
    return dict(version=model.VERSION,
                filename="AnalyzeAssist_Setup_%s.exe" % model.VERSION,
                build_date=str(date.today()))


def buildInstaller():
    """Builds the installer by calling a .bat file"""

    data = get_data()

    make_version_file(data)
    make_setup_script(data)
    generate_docs(data)

    make_setup.setup_main()

    os.chdir(os.path.dirname(__file__))

    command = "buildinstaller.bat"
    print "command =", command
    print
    print "*" * 30
    print "Building setup file..."
    run_command(command)
    print "Finished building setup file!"
    print "*" * 30
    print


if __name__ == '__main__':
    buildInstaller()
