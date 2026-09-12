"""Generate realistic subsample mimicking Customer Support on Twitter for AmericanAir."""
import random, csv, json
random.seed(42)

T = {
 "flight_delay": ["@AmericanAir flight {n} delayed {h}hrs, will I miss my connection in {c}?", "@AmericanAir stuck at {c}, delay again, crew says {h}hr wait, what now?", "AA {n} delayed, need hotel tonight in {c}, who pays?"],
 "cancellation": ["@AmericanAir you cancelled flight {n} to {c} today, need rebook ASAP", "@AmericanAir cancelled on me at gate {c}, rebook options?", "flight {n} cancelled, stranded in {c} tonight, help"],
 "booking_change": ["@AmericanAir need to change flight {n} to tomorrow, fare difference?", "@AmericanAir can I switch seat / add bag on booking {r}?", "change name spelling on reservation {r}, how?"],
 "baggage": ["@AmericanAir bag missing since yesterday flight {n} at {c}, tag {r}", "@AmericanAir damaged suitcase on {n}, claim process?", "charged $75 bag fee but told free, flight {n}, refund?"],
 "refund_compensation": ["@AmericanAir refund for cancelled {n}? nonrefundable but you cancelled", "@AmericanAir want voucher for 5hr delay {n} in {c}", "trip credit not received for {n}, booking {r}"],
 "checkin_boarding": ["@AmericanAir cant check in flight {n}, app error, leaves in 2 hours", "@AmericanAir boarding pass wont load, gate {g} at {c}", "what gate for {n} at {c}? boarding group 4 when?"],
 "loyalty_account": ["@AmericanAir miles missing for flight {n}, AAdvantage {r}", "@AmericanAir cant login AAdvantage, reset not working", "gold status not showing, flight {n} tomorrow"],
 "complaint_service": ["@AmericanAir crew on {n} was rude to my mother, unacceptable", "@AmericanAir discriminated at gate {c}, want supervisor + case", "never flying again, worst service {n}, filing DOT complaint"],
 "praise_other": ["@AmericanAir thanks crew on {n}, great landing in {c}!", "@AmericanAir love the new app, smooth checkin", "do you fly to {c} direct from DFW?"],
}
CITIES = ["DFW","JFK","MIA","ORD","LAX","CLT","PHX","DCA"]
BR = {
 "flight_delay": "Sorry for the delay on {n}. Please check live status in the American app and speak to the gate agent about rebooking/meal voucher if 3+ hrs (aa.com/manage). DM your record locator and I can walk you through options.",
 "cancellation": "Sorry your flight {n} was cancelled. You can rebook free on the next available American flight at aa.com/manage or in the app. DM your record locator for help.",
 "booking_change": "You can change most main-cabin+ tickets at aa.com/manage (fare difference may apply). DM your record locator and new date and I will outline exact steps.",
 "baggage": "Sorry about your bag. Please file a report at aa.com/baggage within 4 hrs and track in the app; keep receipts for essentials. DM your tag/record locator.",
 "refund_compensation": "If we cancelled, you may choose refund or trip credit at aa.com/refunds (refundable to original payment within 7 days). DM your record locator.",
 "checkin_boarding": "Check in from 24 hrs in the app; gates close 15 min before departure. Try app refresh, or kiosk with confirmation code. DM your record locator if still blocked.",
 "loyalty_account": "Miles post within 48 hrs; request missing miles at aa.com/missingmiles with ticket number. DM details (never share password).",
 "complaint_service": "I am sorry you experienced this on {n}. I am escalating to a human specialist with a case number. Please DM your record locator + details.",
 "praise_other": "Thanks for flying with us! Let us know if you need anything on {n}.",
}

def gen(n=3000, out="data/threads_sample.csv"):
    rows=[]
    intents=list(T.keys())
    for i in range(n):
        it = random.choice(intents)
        tpl = random.choice(T[it])
        n1 = f"AA{random.randint(100,2999)}"
        r = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
        text = tpl.format(n=n1, h=random.randint(1,6), c=random.choice(CITIES), r=r, g=random.randint(1,60))
        if random.random()<0.12:
            text = text.lower().replace("@americanair ","").replace(",","") + " pls help asap"
        breply = BR[it].format(n=n1)
        rows.append([f"t{i}", it.replace("_"," "), it, "@customer: "+text, breply])
    with open(out,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["thread_id","topic","intent","inbound","brand_reply"])
        w.writerows(rows)
    print(f"wrote {len(rows)} -> {out}")

if __name__=="__main__":
    gen()
