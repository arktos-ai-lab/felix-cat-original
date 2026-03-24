__author__ = 'Ryan'

from collections import defaultdict

THRESHOLD = 5

class Associations(object):
    """
    Stores associations between tokens
    """
    def __init__(self):
        self._associations = defaultdict(lambda : defaultdict(int))
        self._counts = defaultdict(int)

    def add_associations(self, source_tokens, target_tokens):
        for source in source_tokens:
            self._counts[source] += 1
            for target in target_tokens:
                self._associations[source][target] += 1

    def get_count(self, source):
        return self._counts[source]

    def get_association(self, source, target):
        return self._associations[source][target]

    def get_associations(self, source):
        return self._associations[source]

    def get_strong(self):
        strong = []
        for source, targets in self._associations.iteritems():
            source_count = self.get_count(source)
            for target, hits in targets.iteritems():
                if hits == source_count and hits > THRESHOLD:
                    strong.append((source, target, source_count))

        return strong
