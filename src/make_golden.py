"""Build 200-item golden set: stratified, includes ambiguous/hard cases. Seed-fixed to be reproducible."""
import csv, random
random.seed(7)
from intents import INTENT_LIST

POOL = [
 ("@AmericanAir AA451 delayed 4hrs at DFW, miss connection to MIA, hotel?", "flight_delay", 0, "needs rebooking info, not safety"),
 ("AA451 delayed again 2nd day in a row, crew rude, want compensation now", "complaint_service", 1, "repeat + rude -> human"),
 ("@AmericanAir cancelled AA209 to JFK today, stranded with 2 kids tonight", "cancellation", 1, "same-day stranded family"),
 ("cancelled flight, need rebook tomorrow morning, flexible", "cancellation", 0, "non-urgent rebook can auto-handle"),
 ("need to change AA120 to Friday, what fare diff?", "booking_change", 0, "routine"),
 ("change name spelling SMITH/SMYTH on booking X7K2PQ", "booking_change", 0, "routine"),
 ("bag missing 3 days AA88 JFK tag 09123, meds inside!", "baggage", 1, "medication -> escalate"),
 ("suitcase wheel broken AA77, how claim?", "baggage", 0, "standard damaged-bag flow"),
 ("refund for AA99 you cancelled, nonrefundable ticket", "refund_compensation", 0, "standard refund flow"),
 ("refund denied twice, filing chargeback + DOT complaint AA99", "refund_compensation", 1, "legal/financial threat"),
 ("cant check in AA310 leaves in 2 hours app crashes", "checkin_boarding", 0, "urgent but solvable with steps"),
 ("wheelchair assistance not confirmed AA310 elderly mother", "baggage", 1, "care need -> human"),
 ("miles missing AA400 AAdvantage 12345, 3 days ago", "loyalty_account", 0, "standard"),
 ("locked out AAdvantage, reset email never arrives", "loyalty_account", 0, "standard"),
 ("crew humiliated me, discrimination at CLT gate, want supervisor", "complaint_service", 1, "discrimination -> human"),
 ("thanks AA crew 2142 great with my nervous kid!", "praise_other", 0, "no action"),
 ("do you fly direct DFW to Maui?", "praise_other", 0, "general question"),
 ("lawyer will contact you, lost bag with laptop + you ignore DMs", "complaint_service", 1, "legal threat"),
 ("unaccompanied minor stuck alone DFW AA77 delayed, help now", "flight_delay", 1, "minor safety"),
 ("app shows delayed but gate says on time AA512, which is true?", "flight_delay", 0, "info conflict, answerable"),
]
EXTRA_TPL = {
 "flight_delay": ["AA{n} {h}hr delay {c}, connection at risk", "stuck {c} delay, tonight hotel who pays AA{n}"],
 "cancellation": ["AA{n} cancelled, rebook to {c} asap", "why cancel AA{n}? need morning option"],
 "booking_change": ["move AA{n} to Sunday, cost?", "add checked bag booking {r} AA{n}"],
 "baggage": ["bag delayed AA{n} {c} tag {r}", "bag fee $75 wrong AA{n}"],
 "refund_compensation": ["voucher for {h}hr delay AA{n}?", "trip credit missing AA{n} {r}"],
 "checkin_boarding": ["checkin fails AA{n} 2hrs to go", "gate for AA{n} {c}? group 5"],
 "loyalty_account": ["miles missing AA{n}", "status not showing AA{n}"],
 "complaint_service": ["rude gate agent AA{n} {c}", "DOT complaint AA{n} worst ever"],
 "praise_other": ["great crew AA{n} thanks!", "wifi question AA{n}?"],
}
CITIES=["DFW","JFK","MIA","ORD","LAX","CLT"]

def build(out="eval/golden.csv"):
    rows=[]
    for i,(t,inte,esc,note) in enumerate(POOL):
        rows.append([f"g{i:03d}", t, inte, esc, "human" if esc else "auto", note])
    i=len(rows)
    intents=INTENT_LIST
    k=0
    while len(rows)<200:
        it=intents[k%len(intents)]
        import random as R
        tpl=R.choice(EXTRA_TPL[it])
        n=f"AA{R.randint(100,1999)}"; h=R.randint(1,6); c=R.choice(CITIES)
        r="".join(R.choices("ABCDEFGHJKMNPQRSTUVWXYZ23456789",k=6))
        t=tpl.format(n=n,h=h,c=c,r=r)
        if R.random()<0.15: t=t+" pls help stranded tonight"
        esc=0; why="auto: routine "+it
        if "stranded tonight" in t or "lawyer" in t.lower(): esc=1; why="human: urgent/safety marker"
        if it in ("complaint_service",) : esc=1; why="human: complaint needs specialist"
        if it=="cancellation" and "asap" in t: esc=1; why="human: same-day rebook risk"
        rows.append([f"g{i:03d}", "@AmericanAir "+t, it, esc, "human" if esc else "auto", why])
        i+=1; k+=1
    with open(out,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["id","text","true_intent","needs_escalation","suggested_action","label_note"])
        w.writerows(rows)
    print(f"wrote {len(rows)} -> {out} (sampling: stratified 9 intents + 20 curated edge cases, typos/short/urgent mix)")

if __name__=="__main__":
    build()
