'''
Monitor changes in docs, and rebuild when a py or rst file changes
'''

import os
import subprocess
import time
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Keep track of how much time elapses between calls to unit tests.
# This is to avoid running tests several times for a single change (set).
ELAPSED = time.clock()
DELAY = 2 # seconds

BASEDIR = os.path.abspath(os.path.dirname(__file__))

def get_now():
    """
    Get the current date and time
"""
    return datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

def build_docs():
    print "Building docs at", get_now()
    os.chdir(os.path.join(BASEDIR, "docs"))
    subprocess.call("make.bat html")

def run_tests():
    """
    Run unit tests.
    Keep track of last call, so that we don't run tests many times in succession.
    """
    global ELAPSED
    current = time.clock()
    if current > ELAPSED + DELAY:
        print "Running unit tests at", get_now()
        os.chdir(BASEDIR)
        subprocess.call("nosetests --with-coverage --cover-package=TerminologyAligner")
        subprocess.call("coverage html")
        ELAPSED = current

class ChangeWatcher(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith(".rst"):
            build_docs()
        elif event.src_path.endswith(".py"):
            run_tests()

if __name__ == "__main__":
    event_handler = ChangeWatcher()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
