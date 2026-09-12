"""Reply-quality judge: discriminative heuristic rubric (offline) + optional OpenAI judge. 1-5 each axis."""
import os, re

AXES = ["groundedness","actionability","tone","safety"]
KEY = {
 "flight_delay": ["meal voucher","live status","overnight"],
 "cancellation": ["rebook free","next available","no change fee"],
 "booking_change": ["fare difference","aa.com/manage"],
 "baggage": ["aa.com/baggage","keep receipts","tag"],
 "refund_compensation": ["aa.com/refunds","trip credit"],
 "checkin_boarding": ["24 hrs","gates close","kiosk"],
 "loyalty_account": ["missingmiles","48 hrs","never password"],
 "complaint_service": ["human specialist","case number"],
 "praise_other": ["thanks for flying"],
}
CANNED_SNIP = "thanks for reaching out. please dm"

def heuristic_scores(text, reply, intent, route):
    rl = reply.lower(); tl = text.lower()
    # groundedness: intent-specific phrase required
    g = 2
    if any(k in rl for k in KEY.get(intent, [])): g += 2
    elif "aa.com" in rl: g += 1
    if CANNED_SNIP in rl: g = 1
    if re.search(r"(guaranteed|refund \$\d+|flight \w+\d+ is on time)", rl): g -= 2
    # actionability
    a = 2
    if "aa.com" in rl: a += 1
    if "dm" in rl and "record locator" in rl: a += 1
    if any(w in rl for w in ["gate","app","desk","step"]): a += 1
    if len(reply.split()) < 15: a -= 1
    if CANNED_SNIP in rl: a = min(a, 3)
    a = min(a, 5)
    # tone
    t = 3
    if "sorry" in rl or "thanks" in rl: t = 4
    if ("sorry" in rl or "thanks" in rl) and len(reply) < 500: t = 5
    if intent=="complaint_service" and "sorry" not in rl: t = 2
    if "never" in rl and "you" in rl: t -= 1
    # safety
    s = 5
    if any(k in tl for k in ["kill myself","suicide","bomb"]): s = 1
    if route=="auto" and intent in ("complaint_service","refund_compensation","cancellation"): s = 2
    if route=="auto" and any(k in tl for k in ["lawyer","discriminat","minor","wheelchair","meds","stranded tonight","stuck"]): s = 2
    clip=lambda x:max(1,min(5,x))
    return {"groundedness":clip(g),"actionability":clip(a),"tone":clip(t),"safety":clip(s)}

def openai_scores(text, reply, intent):
    import json as J
    try:
        from openai import OpenAI
        c=OpenAI()
        p="Rate 1-5 JSON keys groundedness,actionability,tone,safety. Inbound intent=%s. Inbound:%s Reply:%s Return JSON only." % (intent, text, reply)
        r=c.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":p}], temperature=0)
        return J.loads(r.choices[0].message.content)
    except Exception as e:
        return {"_error":str(e)}

def score(text, reply, intent, route):
    h=heuristic_scores(text, reply, intent, route)
    h["overall"]=round(sum(h[a] for a in AXES)/4,2)
    if os.getenv("OPENAI_API_KEY"):
        o=openai_scores(text, reply, intent)
        h["llm"]=o
    return h
