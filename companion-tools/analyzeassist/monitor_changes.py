"""
Monitor changes in docs, and rebuild when a py or rst file changes
"""

import os
import subprocess
import time
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def get_now():
    "Get the current date and time as a string"
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def run_tests():
    print "Running unit tests at %s" % get_now()
    sys.stdout.flush()
    os.chdir(BASEDIR)
    subprocess.call("nosetests --with-doctest --with-coverage")


class ChangeWatcher(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            run_tests()


def main():
    """
    called when run as main
    """
    global event_handler, observer
    run_tests()
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


if __name__ == "__main__":
    main()
