"""Trivial + simple baselines (stdlib only)."""
from collections import Counter
from textutils import NB, jaccard

CANNED = "Thanks for reaching out. Please DM your record locator and flight details so we can help. See aa.com/manage for self-serve options."

class TrivialBaseline:
    name="trivial(majority+canned+always-escalate)"
    def fit(self, texts, labels, replies=None):
        self.maj = Counter(labels).most_common(1)[0][0]
    def predict_intent(self, texts):
        return [self.maj]*len(texts), [1.0]*len(texts)
    def draft(self, text, intent):
        return CANNED
    def route(self, text, intent, conf):
        return ("human", "trivial policy: always escalate for safety")

class SimpleBaseline:
    name="simple(nb-unigram+nearest-reply)"
    def __init__(self):
        self.nb=NB(alpha=1.0, bigrams=False)
        self.train_texts=[]; self.train_replies=[]
    def fit(self, texts, labels, replies):
        self.nb.fit(texts, labels)
        self.train_texts=texts; self.train_replies=replies
    def predict_intent(self, texts):
        return self.nb.predict(texts)
    def draft(self, text, intent):
        best=0; bi=0
        for i,t in enumerate(self.train_texts):
            s=jaccard(text, t)
            if s>best: best=s; bi=i
        return self.train_replies[bi]
    def route(self, text, intent, conf):
        t=text.lower()
        if any(k in t for k in ["lawyer","sue","discriminat","dot complaint","medical","minor","wheelchair"]):
            return ("human","keyword: high-risk")
        return ("auto","simple: default auto") if conf>=0.5 else ("human","simple: low confidence")
