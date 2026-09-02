"""NLP helpers for crime-behaviour and digital-evidence triage.

This module is intentionally deterministic. It does not identify suspects and
it does not claim forensic proof; it produces explainable research features that
can be audited in a paper.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, asdict


TOKEN_RE = re.compile(r"[\w@.:/+%-]+", re.UNICODE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s,;]+|www\.[^\s,;]+", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+91[-\s]?)?[6-9]\d{9}\b")
UPI_RE = re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
HASH_RE = re.compile(r"\b[a-fA-F0-9]{32,64}\b")


CRIME_PATTERNS = {
    "financial_cyber_fraud": ["upi", "otp", "bank", "wallet", "kyc", "loan", "refund", "investment", "crypto", "payment"],
    "identity_social_engineering": ["impersonation", "fake profile", "phishing", "spoof", "sim swap", "credential", "password"],
    "sexual_extortion_abuse": ["sextortion", "blackmail", "morphed", "intimate", "harassment", "stalking"],
    "property_crime": ["burglary", "theft", "vehicle", "gold", "entry", "lock", "stolen"],
    "violent_threat": ["weapon", "knife", "gun", "assault", "threat", "murder", "kidnap"],
}


INDIAN_LANGUAGE_HINTS = {
    "hindi_or_hinglish": ["paisa", "paise", "dhokha", "fraud hua", "otp", "phonepe", "paytm", "gpay", "dhamki"],
    "legal_india": ["fir", "police station", "cyber cell", "it act", "bns", "bnss", "bsa", "ncrp", "cctns"],
}


EVIDENCE_KEYWORDS = {
    "device": ["mobile", "phone", "laptop", "desktop", "router", "cctv", "dvr", "sim"],
    "network": ["ip", "domain", "url", "email header", "login", "geolocation", "cell id"],
    "financial": ["utr", "upi", "account", "ifsc", "wallet", "transaction", "statement"],
    "content": ["chat", "screenshot", "audio", "video", "image", "post", "message"],
    "chain_of_custody": ["hash", "seizure", "panchnama", "seal", "clone", "image", "write blocker"],
}


STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "have", "has", "was", "were", "are", "not", "but",
    "you", "your", "his", "her", "our", "their", "then", "than", "into", "over", "under", "after", "before",
}


@dataclass
class TriageResult:
    language_hints: list[str]
    extracted_indicators: dict[str, list[str]]
    crime_categories: list[dict[str, object]]
    evidence_coverage: list[dict[str, object]]
    top_terms: list[dict[str, object]]
    risk_score: int
    risk_factors: list[str]
    llm_review_prompt: str
    limitations: list[str]


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if len(token) > 2 and token.lower() not in STOPWORDS]


def unique_matches(pattern: re.Pattern[str], text: str) -> list[str]:
    return sorted(set(match.group(0).strip(".,;") for match in pattern.finditer(text)))


def score_patterns(tokens: list[str], text_lower: str, patterns: dict[str, list[str]]) -> list[dict[str, object]]:
    results = []
    token_set = set(tokens)
    for label, terms in patterns.items():
        hits = []
        for term in terms:
            if " " in term:
                if term in text_lower:
                    hits.append(term)
            elif term in token_set:
                hits.append(term)
        if hits:
            results.append({"label": label, "score": min(1.0, round(len(hits) / max(3, len(terms)), 2)), "signals": hits})
    return sorted(results, key=lambda row: row["score"], reverse=True)


def detect_language_hints(text_lower: str) -> list[str]:
    hints = []
    for label, phrases in INDIAN_LANGUAGE_HINTS.items():
        if any(phrase in text_lower for phrase in phrases):
            hints.append(label)
    if re.search(r"[\u0900-\u097F]", text_lower):
        hints.append("devanagari_script")
    return sorted(set(hints))


def evidence_coverage(tokens: list[str], text_lower: str) -> list[dict[str, object]]:
    token_set = set(tokens)
    coverage = []
    for label, terms in EVIDENCE_KEYWORDS.items():
        hits = [term for term in terms if (" " in term and term in text_lower) or term in token_set]
        coverage.append({"area": label, "present": bool(hits), "signals": hits})
    return coverage


def analyze_text(text: str) -> dict[str, object]:
    text = text.strip()
    text_lower = text.lower()
    tokens = tokenize(text)
    indicators = {
        "emails": unique_matches(EMAIL_RE, text),
        "urls": unique_matches(URL_RE, text),
        "phones_india": unique_matches(PHONE_RE, text),
        "upi_or_handles": unique_matches(UPI_RE, text),
        "ip_addresses": unique_matches(IP_RE, text),
        "hashes": unique_matches(HASH_RE, text),
    }
    categories = score_patterns(tokens, text_lower, CRIME_PATTERNS)
    coverage = evidence_coverage(tokens, text_lower)
    term_counts = Counter(tokens)
    risk_factors = []
    if categories:
        risk_factors.append("crime-pattern language matched known category dictionaries")
    if sum(len(v) for v in indicators.values()) >= 3:
        risk_factors.append("multiple digital identifiers were present")
    if any(item["area"] == "chain_of_custody" and item["present"] for item in coverage):
        risk_factors.append("chain-of-custody or hashing terms were present")
    if any(item["label"] in {"violent_threat", "sexual_extortion_abuse"} for item in categories):
        risk_factors.append("high-harm category terms were present")

    score = min(100, 15 + len(categories) * 12 + sum(len(v) for v in indicators.values()) * 6 + len(risk_factors) * 8)
    prompt = build_llm_prompt(text, indicators, categories, coverage)
    result = TriageResult(
        language_hints=detect_language_hints(text_lower),
        extracted_indicators=indicators,
        crime_categories=categories,
        evidence_coverage=coverage,
        top_terms=[{"term": term, "count": count} for term, count in term_counts.most_common(12)],
        risk_score=score if text else 0,
        risk_factors=risk_factors,
        llm_review_prompt=prompt,
        limitations=[
            "This is triage, not automated suspect identification.",
            "The deterministic NLP layer cannot verify truth, intent, jurisdiction, or admissibility.",
            "An LLM review should cite the case record and must not invent facts beyond the submitted text.",
        ],
    )
    return asdict(result)


def build_llm_prompt(text: str, indicators: dict[str, list[str]], categories: list[dict[str, object]], coverage: list[dict[str, object]]) -> str:
    return (
        "You are assisting an investigator with a research prototype. "
        "Summarize only facts present in the complaint text, identify missing evidence, "
        "and separate verified indicators from hypotheses. Do not name suspects unless "
        "the input text itself names them. Return JSON with facts, possible_offence_categories, "
        "digital_indicators, evidence_gaps, and follow_up_questions.\n\n"
        f"Complaint text:\n{text[:4000]}\n\n"
        f"Extracted indicators:\n{indicators}\n\n"
        f"Matched categories:\n{categories}\n\n"
        f"Evidence coverage:\n{coverage}\n"
    )
