import re

def word_match_score(candidate: str, gt: str) -> int:
    # Clean the strings: keep only letters, digits, and spaces
    clean = lambda s: re.sub(r'[^a-zA-Z0-9\s]', '', s).lower().split()

    candidate_words = set(clean(candidate))
    gt_words = set(clean(gt))

    return len(candidate_words & gt_words)