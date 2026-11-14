from collections import Counter
from .data import UPOS

def evaluate(gold, predicted, frequencies, long_threshold):
    if len(gold) != len(predicted):
        raise ValueError('sentence count mismatch')
    counts, confusion = {}, Counter()
    def add(key, correct):
        counts.setdefault(key, [0, 0])
        counts[key][0] += int(correct); counts[key][1] += 1
    for g, p in zip(gold, predicted):
        if g['tokens'] != p['tokens'] or len(g['tokens']) != len(p['upos']):
            raise ValueError('token alignment mismatch')
        if 'sent_id' in p and p['sent_id'] != g['sent_id']:
            raise ValueError('sentence ID mismatch')
        size = len(g['tokens'])
        size_group = '1-10' if size <= 10 else '11-20' if size <= 20 else '21-40' if size <= 40 else '41+'
        for word, true, guess in zip(g['tokens'], g['upos'], p['upos']):
            if guess not in UPOS: raise ValueError('invalid predicted UPOS')
            good = true == guess
            freq = frequencies.get(word, 0)
            freq_group = '0' if freq == 0 else '1' if freq == 1 else '2-5' if freq <= 5 else '6+'
            groups = ['overall', 'oov' if freq == 0 else 'seen', f'frequency:{freq_group}',
                      'long' if len(word) >= long_threshold else 'short', f'sentence_length:{size_group}']
            if true != 'PUNCT': groups.append('nonpunct')
            for key in groups: add(key, good)
            confusion[true, guess] += 1
    labels = {}
    for label in UPOS:
        tp = confusion[label, label]
        support = sum(v for (t, _), v in confusion.items() if t == label)
        predicted_count = sum(v for (_, p), v in confusion.items() if p == label)
        precision = tp / predicted_count if predicted_count else 0.
        recall = tp / support if support else None
        f1 = 2 * tp / (support + predicted_count) if support + predicted_count else None
        labels[label] = dict(precision=precision, recall=recall, f1=f1, support=support)
    scores = {k:dict(correct=a, n=b, accuracy=a/b if b else None) for k,(a,b) in counts.items()}
    for k in ['overall','nonpunct','oov','seen']:
        scores.setdefault(k, dict(correct=0, n=0, accuracy=None))
    f1s = [v['f1'] or 0. for v in labels.values() if v['support']]
    return dict(groups=scores, labels=labels, macro_f1=sum(f1s)/len(f1s) if f1s else None)
