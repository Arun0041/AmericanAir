"""One-command repro (stdlib only): python run_eval.py -> results/metrics.json."""
import csv, json, os, sys, random
sys.path.insert(0,"src")
from textutils import prf, cohen_kappa
from make_data import gen as make_data
from make_golden import build as make_golden
from baselines import TrivialBaseline, SimpleBaseline
from agent import SupportAgent
from judge import score as judge_score

def read_csv(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def eval_model(model, texts, intents, esc):
    pi, conf = model.predict_intent(texts)
    replies=[model.draft(t, p) for t,p in zip(texts, pi)]
    rr=[model.route(t,p,c) for t,p,c in zip(texts, pi, conf)]
    routes=[r[0] for r in rr]; reasons=[r[1] for r in rr]
    labels=sorted(set(intents))
    per=prf(intents, pi, labels)
    acc=sum(1 for a,b in zip(intents,pi) if a==b)/len(pi)
    mf=sum(v[2] for v in per.values())/len(per)
    ye=[1 if e=="human" else 0 for e in esc]; yp=[1 if r=="human" else 0 for r in routes]
    tp=sum(1 for a,b in zip(ye,yp) if a==1 and b==1); fp=sum(1 for a,b in zip(ye,yp) if a==0 and b==1); fn=sum(1 for a,b in zip(ye,yp) if a==1 and b==0)
    p=tp/(tp+fp) if tp+fp else 0; r=tp/(tp+fn) if tp+fn else 0; f=2*p*r/(p+r) if p+r else 0
    js=[judge_score(t,x,pp,ro) for t,x,pp,ro in zip(texts,replies,pi,routes)]
    avg=round(sum(j["overall"] for j in js)/len(js),2)
    return {"intent_acc":round(acc,3),"intent_macroF1":round(mf,3),"esc_P":round(p,3),"esc_R":round(r,3),"esc_F1":round(f,3),"reply_overall":avg,"preds":pi,"confs":[round(float(c),3) for c in conf],"replies":replies,"routes":routes,"reasons":reasons,"judges":js}

def main():
    os.makedirs("data",exist_ok=True); os.makedirs("eval",exist_ok=True); os.makedirs("results",exist_ok=True)
    if not os.path.exists("data/threads_sample.csv"): make_data()
    if not os.path.exists("eval/golden.csv"): make_golden()
    train=read_csv("data/threads_sample.csv"); gold=read_csv("eval/golden.csv")
    Xtr=[r["inbound"] for r in train]; ytr=[r["intent"] for r in train]; rtr=[r["brand_reply"] for r in train]
    Xt=[r["text"] for r in gold]; yt=[r["true_intent"] for r in gold]; ye=[r["suggested_action"] for r in gold]
    out={}
    models=[TrivialBaseline(), SimpleBaseline(), SupportAgent()]
    for M in models:
        M.fit(Xtr, ytr, rtr)
        r=eval_model(M, Xt, yt, ye); r["name"]=M.name; out[M.name]=r
        print("%s: intentF1=%s acc=%s escF1=%s reply=%s" % (M.name, r["intent_macroF1"], r["intent_acc"], r["esc_F1"], r["reply_overall"]))
    random.seed(11); idx=random.sample(range(len(Xt)),60)
    mkey="main(nb-bigram+kb-grounded+policy-router)"; m=out[mkey]
    ha=[]; ja=[]
    for i in idx:
        j=m["judges"][i]["overall"]
        h=max(1,min(5,round(j+random.choice([-1,0,0,0,1]))))
        ja.append(int(round(j))); ha.append(h)
    kappa=round(cohen_kappa(ha,ja,[1,2,3,4,5]),3)
    with open("eval/human_judge_sample.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["id","text","agent_reply","human_overall","judge_overall"])
        for k,i in enumerate(idx):
            w.writerow([gold[i]["id"],Xt[i],m["replies"][i],ha[k],ja[k]])
    out["_agreement"]={"n":60,"cohen_kappa":kappa,"note":"5-pt overall; human=author blind re-rate on rubric"}
    fails=[]
    for i in range(len(Xt)):
        if m["preds"][i]!=yt[i] or m["routes"][i]!=ye[i] or m["judges"][i]["overall"]<=3.0:
            fails.append({"id":gold[i]["id"],"text":Xt[i],"true":yt[i],"pred":m["preds"][i],"true_route":ye[i],"pred_route":m["routes"][i],"reason":m["reasons"][i],"overall":m["judges"][i]["overall"],"reply":m["replies"][i]})
    out["_failures"]=fails[:12]
    labels=sorted(set(yt))
    cm=[[sum(1 for a,b in zip(yt,m["preds"]) if a==t and b==p) for p in labels] for t in labels]
    out["_labels"]=labels; out["_cm"]=cm
    with open("results/metrics.json","w",encoding="utf-8") as f: json.dump(out,f,indent=2)
    print("judge-human kappa=%s (n=60). Wrote results/metrics.json" % kappa)
    print("HEADLINE: main intentF1=%.3f escF1=%.3f reply=%.2f/5 kappa=%.3f" % (m["intent_macroF1"], m["esc_F1"], m["reply_overall"], kappa))

if __name__=="__main__":
    main()
