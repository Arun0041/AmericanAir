"""Intent taxonomy for AmericanAir support agent. Derived from Twitter data patterns."""
INTENTS = {
    "flight_delay": {"desc": "Flight delayed, late departure/arrival, missed connection due to delay", "risk": "medium"},
    "cancellation": {"desc": "Flight cancelled, need rebooking", "risk": "high"},
    "booking_change": {"desc": "Change date/time/seat/name, add bag, upgrade, check fare rules", "risk": "low"},
    "baggage": {"desc": "Lost, delayed, damaged bag, baggage fee, carry-on issue", "risk": "medium"},
    "refund_compensation": {"desc": "Refund, voucher, credit, compensation for disruption", "risk": "high"},
    "checkin_boarding": {"desc": "Check-in, boarding pass, gate, boarding group, ID docs", "risk": "low"},
    "loyalty_account": {"desc": "AAdvantage miles, account login, status, points missing", "risk": "low"},
    "complaint_service": {"desc": "Rude crew, complaint, threat, legal, discrimination, safety", "risk": "high"},
    "praise_other": {"desc": "Thanks, praise, general question, off-topic, unclear", "risk": "low"},
}
INTENT_LIST = list(INTENTS.keys())
HIGH_RISK = {"cancellation", "refund_compensation", "complaint_service"}
ESCALATE_KEYWORDS = ["lawyer", "sued", "sue", "discriminat", "racist", "rude", "medical", "emergency", "stranded overnight", "wheelchair", "unaccompanied minor", "refund denied", "chargeback", "dot complaint", "faa"]
URGENT_KEYWORDS = ["today", "right now", "asap", "stuck", "stranded", "tonight", "morning flight", "in 2 hours", "gate now"]
