"""Main agent: NB-bigram + KB-grounded reply + policy router (stdlib only)."""
import json
from textutils import NB
from intents import HIGH_RISK, ESCALATE_KEYWORDS, URGENT_KEYWORDS

REPLY_TPL = {
 "flight_delay": "Sorry for the delay. Check live status in the American app; if 3+ hrs ask the gate for a meal voucher, overnight caused by us means hotel+transport at the gate/Admirals Club desk. Manage at aa.com/manage. DM your record locator and I can outline rebooking.",
 "cancellation": "Sorry AA cancelled this. Rebook free on the next available American flight at aa.com/manage or in the app (no change fee main-cabin+). DM your record locator + preferred time and I will give exact steps.",
 "booking_change": "You can change most main-cabin+ tickets at aa.com/manage (fare difference may apply). DM your record locator + new date and I will list the clicks/fees.",
 "baggage": "Sorry about your bag. File within 4 hrs at aa.com/baggage, track in the app, keep receipts (essentials up to $150/day x3 days). If 5+ days missing file at aa.com/baggageclaim. DM tag + record locator.",
 "refund_compensation": "If we cancelled: refund or trip credit at aa.com/refunds (refundable back in ~7 days). DM your record locator + ticket type and I will confirm which you qualify for.",
 "checkin_boarding": "Check in from 24 hrs in the app; gates close 15 min before departure. Refresh app / use kiosk with code. DM your record locator if still blocked and tell me the error text.",
 "loyalty_account": "Miles post within 48 hrs; claim missing at aa.com/missingmiles with ticket number. DM last name + AAdvantage number (never password).",
 "complaint_service": "I am sorry this happened. I am flagging for a human specialist who will reply with a case number. Please DM record locator + date/gate + what happened.",
 "praise_other": "Thanks for flying American — glad to hear it. Anything you need for your trip?",
}

class SupportAgent:
    name="main(nb-bigram+kb-grounded+policy-router)"
    def __init__(self):
        self.nb=NB(alpha=0.5, bigrams=True)
        with open("data/knowledge_base.json",encoding="utf-8") as f: self.kb=json.load(f)
    def fit(self, texts, labels, replies):
        self.nb.fit(texts, labels)
    def predict_intent(self, texts):
        return self.nb.predict(texts)
    def draft(self, text, intent):
        return REPLY_TPL.get(intent, REPLY_TPL["praise_other"])
    def route(self, text, intent, conf):
        tl=text.lower()
        if any(k in tl for k in ESCALATE_KEYWORDS): return ("human", "policy: high-risk keyword + intent="+intent)
        if intent in HIGH_RISK and any(k in tl for k in URGENT_KEYWORDS+["stranded","tonight","today","kid","minor","meds","medical"]):
            return ("human", "policy: high-risk intent "+intent+" with urgency")
        if intent=="complaint_service": return ("human", "policy: complaints need human specialist + case")
        if conf<0.55: return ("human", "policy: low confidence %.2f<0.55" % conf)
        if len(text.split())<4: return ("human", "policy: too short/ambiguous")
        return ("auto", "policy: routine %s conf=%.2f" % (intent, conf))
