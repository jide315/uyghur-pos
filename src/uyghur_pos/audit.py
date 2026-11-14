"""Content-only token sequence overlap audit; does not evaluate predictions."""
from collections import Counter,defaultdict
from difflib import SequenceMatcher

def near_duplicates(left,right,threshold=.9):
    postings=defaultdict(list)
    for j,row in enumerate(right):
        for word,count in Counter(row['tokens']).items():postings[word].append((j,count))
    results=[]
    for a in left:
        shared=Counter()
        for word,count in Counter(a['tokens']).items():
            for j,other_count in postings[word]:shared[j]+=min(count,other_count)
        for j,overlap in shared.items():
            b=right[j]; total=len(a['tokens'])+len(b['tokens'])
            if 2*overlap/total < threshold:continue
            ratio=SequenceMatcher(None,a['tokens'],b['tokens'],autojunk=False).ratio()
            if ratio>=threshold:
                results.append(dict(left=a['sent_id'],right=b['sent_id'],ratio=ratio,
                                    exact=a['tokens']==b['tokens'],left_words=len(a['tokens']),right_words=len(b['tokens'])))
    return results
