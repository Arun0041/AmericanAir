"""Shared tokenizer + Naive Bayes + metrics (stdlib only)."""
import re, math
from collections import Counter, defaultdict

TOK = re.compile(r"[a-z0-9]+")
def tokenize(s, bigrams=False):
    t = TOK.findall(s.lower())
    if not bigrams: return t
    return t + [a+"_"+b for a,b in zip(t, t[1:])]

class NB:
    def __init__(self, alpha=1.0, bigrams=False):
        self.alpha=alpha; self.bigrams=bigrams
        self.cls_counts=Counter(); self.word_counts={}; self.vocab=set(); self.total_docs=0
    def fit(self, texts, labels):
        for t,l in zip(texts, labels):
            self.cls_counts[l]+=1; self.total_docs+=1
            c=self.word_counts.setdefault(l, Counter())
            for w in tokenize(t, self.bigrams):
                c[w]+=1; self.vocab.add(w)
        self.denom={l: sum(c.values())+self.alpha*len(self.vocab) for l,c in self.word_counts.items()}
    def predict(self, texts):
        preds=[]; confs=[]
        V=len(self.vocab)
        for t in texts:
            ws=tokenize(t, self.bigrams)
            best=None; scores={}
            for l in self.cls_counts:
                s=math.log(self.cls_counts[l]/self.total_docs)
                wc=self.word_counts[l]; d=self.denom[l]
                for w in ws:
                    s+=math.log(((wc.get(w,0))+self.alpha)/d)
                scores[l]=s
            m=max(scores.values())
            ex={l: math.exp(s-m) for l,s in scores.items()}
            z=sum(ex.values())
            pred=max(scores, key=scores.get)
            preds.append(pred); confs.append(ex[pred]/z)
        return preds, confs

def jaccard(a, b):
    A=set(tokenize(a)); B=set(tokenize(b))
    if not A or not B: return 0.0
    return len(A&B)/len(A|B)

def prf(y_true, y_pred, labels):
    out={}
    for l in labels:
        tp=sum(1 for a,b in zip(y_true,y_pred) if a==l and b==l)
        fp=sum(1 for a,b in zip(y_true,y_pred) if a!=l and b==l)
        fn=sum(1 for a,b in zip(y_true,y_pred) if a==l and b!=l)
        p=tp/(tp+fp) if tp+fp else 0; r=tp/(tp+fn) if tp+fn else 0
        f=2*p*r/(p+r) if p+r else 0
        out[l]=(p,r,f)
    return out

def cohen_kappa(a, b, labels):
    n=len(a)
    po=sum(1 for x,y in zip(a,b) if x==y)/n
    from collections import Counter
    ca=Counter(a); cb=Counter(b)
    pe=sum((ca[l]/n)*(cb[l]/n) for l in labels)
    return (po-pe)/(1-pe) if pe<1 else 0.0
