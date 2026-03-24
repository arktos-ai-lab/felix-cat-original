__author__ = 'Ryan'

from TerminologyAligner import tokenize
from TerminologyAligner import stats

def get_strong_associations(segments):
    source_associations = stats.Associations()
    target_associations = stats.Associations()
    for source, target in segments:
        source_tokens = tokenize.tokenize(source)
        target_tokens = tokenize.tokenize(target)
        source_associations.add_associations(source_tokens, target_tokens)
        target_associations.add_associations(target_tokens, source_tokens)

    source_strong = source_associations.get_strong()
    target_strong = target_associations.get_strong()

    strong = []
    targets = set()
    for target, source, count in target_strong:
        targets.add((source, target))
    for source, target, count in source_strong:
        if (source, target) in targets:
            print source.encode("utf-8"), target.encode("utf-8"), count
            strong.append((source, target, count))

    return strong
