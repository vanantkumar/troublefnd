import re
import math


# ── Vocabulary ─────────────────────────────────────────────────────────────────

FAKE_VOCAB: dict[str, float] = {
    # Sensationalism
    "shocking": 3.4, "explosive": 3.2, "bombshell": 3.6, "secret": 2.9,
    "exposed": 3.0, "massive": 2.2, "incredible": 2.4, "unbelievable": 3.1,
    "mind blowing": 3.5, "jaw dropping": 3.4, "stunning": 2.8, "outrageous": 3.0,
    "terrifying": 2.9, "horrifying": 3.0, "disgusting": 2.8, "insane": 2.6,

    # Conspiracy / distrust
    "hoax": 4.2, "coverup": 3.9, "cover-up": 3.9, "agenda": 2.8,
    "elite": 2.5, "cabal": 4.1, "crisis actor": 4.6, "false flag": 4.4,
    "deep state": 4.3, "globalist": 4.0, "new world order": 4.6,
    "wake up sheeple": 4.4, "wake up": 2.9, "sheeple": 4.1,
    "truth they hide": 4.0, "they don't want you": 3.9,
    "you won't believe": 3.9, "mainstream media lies": 4.2,
    "shadow government": 4.3, "secret society": 4.0, "puppet masters": 4.1,
    "controlled opposition": 3.8, "george soros": 3.2, "illuminati": 4.5,
    "new world order": 4.5, "plandemic": 4.6, "scamdemic": 4.7,
    "great reset": 3.5, "they are hiding": 3.8, "what they don't": 3.6,

    # Medical misinformation
    "miracle cure": 4.3, "doctors hate": 4.1, "banned": 2.9, "suppressed": 3.2,
    "big pharma": 3.6, "chemtrail": 4.4, "5g causes": 4.3, "detox": 2.4,
    "natural cure": 3.0, "cure cancer": 3.8, "vaccine injury": 3.3,
    "depopulation": 4.2, "microchip vaccine": 4.6, "poison": 2.6,
    "toxins": 2.5, "bleach cure": 4.8, "essential oils cure": 3.9,

    # Engagement bait
    "must share": 3.8, "share before deleted": 4.3, "share before removed": 4.3,
    "going viral": 2.2, "guaranteed": 2.2, "clickbait": 3.1,
    "share this now": 3.7, "spread the word": 3.0, "pass it on": 2.8,
    "before it's too late": 3.6, "don't let them silence": 3.9,
    "they will delete": 3.8, "censored": 3.0, "banned from": 3.1,

    # Political inflammatory
    "rigged": 3.3, "stolen election": 3.9, "fraud": 2.8, "radical left": 3.4,
    "radical right": 3.4, "destroy": 2.1, "regime": 2.5, "dictator": 2.6,
    "communist": 2.7, "fascist": 2.6, "socialist agenda": 3.5,
    "deep state agenda": 4.2, "election fraud": 3.8, "vote rigging": 3.7,
    "corrupt politician": 3.0, "political puppet": 3.5, "fake president": 4.0,

    # Weak / anonymous attribution
    "anonymous sources": 2.6, "unnamed officials": 2.7, "sources say": 2.1,
    "rumor": 2.9, "unconfirmed": 2.8, "alleged": 1.8, "supposedly": 2.4,
    "people are saying": 3.2, "everyone knows": 2.9, "many people say": 3.1,
    "i heard": 2.7, "word is": 2.6,

    # Emotional manipulation
    "urgent": 2.4, "breaking": 1.8, "exclusive": 2.3,
    "shocking truth": 4.0, "100%": 2.3, "absolute proof": 3.8,
    "undeniable proof": 3.9, "smoking gun": 3.6, "caught red handed": 3.5,
    "they admitted": 3.2, "finally exposed": 3.7, "it's over": 2.8,
    "game over": 2.7, "the truth is out": 3.5,

    # Pseudoscience
    "flat earth": 4.5, "moon landing fake": 4.7, "reptilian": 4.6,
    "lizard people": 4.7, "clone": 3.0, "microwave mind": 4.4,
    "astral projection cures": 4.0, "quantum healing": 3.8, "vibration cures": 3.7,
}

REAL_VOCAB: dict[str, float] = {
    # Strong source attribution
    "according to": 2.2, "said in a statement": 2.4, "spokesperson": 2.1,
    "confirmed by": 2.0, "announced": 1.7, "told reporters": 2.1,
    "press conference": 2.0, "official statement": 2.2, "in a press release": 2.3,
    "reuters": 2.8, "associated press": 2.8, "bbc": 2.5, "pti": 2.4,
    "the hindu": 2.3, "ndtv": 2.3, "times of india": 2.2, "bloomberg": 2.5,
    "financial times": 2.6, "wall street journal": 2.6, "new york times": 2.4,
    "guardian": 2.3, "washington post": 2.4, "ap news": 2.7,

    # Research & data signals
    "study": 1.9, "research": 1.8, "analysis": 2.0, "data": 1.9,
    "published": 1.8, "journal": 2.1, "university": 2.0,
    "scientists": 1.9, "experts": 1.7, "statistics": 2.1,
    "survey": 1.8, "poll": 1.6, "percent": 1.7, "findings": 1.9,
    "meta-analysis": 2.5, "systematic review": 2.5, "clinical trial": 2.2,
    "randomized": 2.3, "peer reviewed": 2.4, "double blind": 2.4,
    "sample size": 2.2, "confidence interval": 2.3, "p-value": 2.4,
    "median": 1.9, "mean": 1.7, "standard deviation": 2.2,

    # Government / legal / institutional
    "parliament": 1.9, "senate": 1.8, "minister": 1.7,
    "department": 1.6, "committee": 1.8, "government": 1.4,
    "officials": 1.6, "court": 1.7, "ruling": 1.8,
    "verdict": 1.9, "evidence": 2.0, "investigation": 1.8,
    "legislation": 2.0, "amendment": 1.9, "constitution": 1.8,
    "supreme court": 2.1, "high court": 2.0, "tribunal": 1.9,
    "regulatory": 2.0, "compliance": 1.8, "audit": 1.9,

    # Financial / economic precision
    "billion": 1.5, "million": 1.5, "market": 1.4, "index": 1.6,
    "economy": 1.5, "gdp": 2.0, "inflation": 1.7, "fiscal": 1.9,
    "quarterly": 1.8, "annual report": 2.0, "earnings": 1.7,
    "revenue": 1.6, "profit": 1.5, "loss": 1.5, "forecast": 1.7,

    # Health / science
    "hospital": 1.7, "health": 1.4, "climate": 1.5, "census": 2.1,
    "who": 1.6, "cdc": 1.9, "icmr": 1.9, "lancet": 2.4,
    "nature journal": 2.5, "science magazine": 2.4, "pubmed": 2.4,

    # Neutral factual reporting
    "said": 1.3, "told": 1.3, "reported": 1.4, "cited": 1.7,
    "noted": 1.5, "added": 1.4, "stated": 1.5, "explained": 1.4,
    "acknowledged": 1.6, "clarified": 1.7, "reiterated": 1.6,
}

TRUSTED_SOURCES = [
    "reuters", "associated press", "ap news", "bbc", "bloomberg",
    "financial times", "wall street journal", "new york times",
    "washington post", "the hindu", "ndtv", "pti", "times of india",
    "guardian", "al jazeera", "nature", "science", "lancet",
    "who", "unicef", "world bank", "imf",
]

SENSATIONAL_TERMS = [
    "shocking", "incredible", "unbelievable", "bombshell", "explosive",
    "outrage", "urgent", "must share", "wake up", "you won't believe",
    "they don't want", "miracle cure", "banned", "suppressed",
    "going viral", "share before deleted", "breaking news", "mind blowing",
    "jaw dropping", "absolute proof", "undeniable proof", "smoking gun",
    "finally exposed", "false flag", "plandemic", "scamdemic",
    "they will delete", "don't let them silence",
]

HEDGE_WORDS = [
    "allegedly", "reportedly", "sources say", "unnamed", "anonymous",
    "claimed", "purportedly", "unverified", "rumored", "supposedly",
    "people are saying", "i heard",
]

NEGATION_WORDS = ["not", "no", "never", "neither", "nor", "without", "denies", "denied", "false that"]


class FakeNewsClassifier:

    def __init__(self):
        self.fake_vocab = FAKE_VOCAB
        self.real_vocab = REAL_VOCAB
        self.sensational = SENSATIONAL_TERMS
        self.hedge_words = HEDGE_WORDS
        self.trusted_sources = TRUSTED_SOURCES
        self.negations = NEGATION_WORDS

    def _is_negated(self, term: str, text: str) -> bool:
        """Check if a term is preceded by a negation within 3 words."""
        pattern = r'(?:' + '|'.join(re.escape(n) for n in self.negations) + r')\s+(?:\w+\s+){0,2}' + re.escape(term)
        return bool(re.search(pattern, text))

    def _tfidf_weight(self, raw_score: float, word_count: int) -> float:
        """Normalize score by log of document length (TF-IDF length norm)."""
        return raw_score / math.log(max(word_count, 2) + 1)

    def _extract_features(self, text: str) -> dict:
        lower = text.lower()
        words = re.split(r'\s+', lower.strip())
        total_words = max(len(words), 1)

        # ── Vocabulary scoring with negation guard ─────────────────────────
        fake_score = 0.0
        real_score = 0.0
        matched_fake = []
        matched_real = []

        for term, weight in self.fake_vocab.items():
            if term in lower and not self._is_negated(term, lower):
                fake_score += weight
                matched_fake.append(term)

        for term, weight in self.real_vocab.items():
            if term in lower:
                real_score += weight
                matched_real.append(term)

        # ── TF-IDF length normalization ────────────────────────────────────
        fake_score = self._tfidf_weight(fake_score, total_words)
        real_score = self._tfidf_weight(real_score, total_words)

        # ── Linguistic features ────────────────────────────────────────────
        caps_words    = len(re.findall(r'\b[A-Z]{3,}\b', text))
        caps_ratio    = round((caps_words / total_words) * 100)
        exclaims      = len(re.findall(r'!', text))
        questions     = len(re.findall(r'\?', text))
        repeat_punct  = len(re.findall(r'[!?]{2,}', text))
        all_caps_sent = len(re.findall(r'[A-Z]{10,}', text))
        sensational   = sum(1 for s in self.sensational if s in lower)
        hedges        = sum(1 for h in self.hedge_words if h in lower)

        words_raw     = text.split()
        avg_word_len  = sum(len(w) for w in words_raw) / total_words
        sentences     = [s for s in re.split(r'[.!?]+', text) if len(s.strip()) > 5]
        avg_sent_len  = round(total_words / max(len(sentences), 1))

        # Named entity proxy: count capitalized multi-word sequences
        named_entities = len(re.findall(r'(?:[A-Z][a-z]+ ){1,3}[A-Z][a-z]+', text))

        # Trusted source detection
        source_boost = sum(1 for s in self.trusted_sources if s in lower)

        # ── Score adjustments ──────────────────────────────────────────────
        fake_score += caps_ratio     * 0.04
        fake_score += exclaims       * 0.35
        fake_score += repeat_punct   * 0.6
        fake_score += all_caps_sent  * 0.5
        fake_score += sensational    * 0.9
        fake_score += questions      * 0.12

        real_score += hedges         * 0.3
        real_score += source_boost   * 1.2
        real_score += named_entities * 0.06
        real_score += (1.4 if avg_word_len  > 5.5 else 0)
        real_score += (1.0 if avg_sent_len  > 18  else 0)
        real_score += (0.8 if total_words   > 100 else 0)

        # Penalty: very short text with high caps → likely bait
        if total_words < 15 and caps_ratio > 20:
            fake_score += 1.5

        # ── Naive Bayes posterior ──────────────────────────────────────────
        total     = fake_score + real_score + 1e-9
        real_prob = (real_score / total) * 100

        # Confidence clamping — avoid overconfident extremes
        real_prob = min(92, max(8, round(real_prob)))

        return {
            "fake_score"   : round(fake_score, 3),
            "real_score"   : round(real_score, 3),
            "real_prob"    : real_prob,
            "matched_fake" : matched_fake[:8],
            "matched_real" : matched_real[:8],
            "features": {
                "word_count"   : total_words,
                "caps_ratio"   : caps_ratio,
                "exclaims"     : exclaims,
                "sensational"  : sensational,
                "hedges"       : hedges,
                "avg_word_len" : round(avg_word_len, 1),
                "avg_sent_len" : avg_sent_len,
            },
        }

    def predict(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "verdict": "NO_INPUT", "real_prob": 50,
                "fake_score": 0.0, "real_score": 0.0,
                "matched_fake": [], "matched_real": [],
                "features": {
                    "word_count": 0, "caps_ratio": 0, "exclaims": 0,
                    "sensational": 0, "hedges": 0,
                    "avg_word_len": 0.0, "avg_sent_len": 0,
                },
            }

        result = self._extract_features(text)
        r = result["real_prob"]

        if r >= 65:
            verdict = "LIKELY_REAL"
        elif r <= 35:
            verdict = "LIKELY_FAKE"
        else:
            verdict = "UNCERTAIN"

        return {"verdict": verdict, **result}
