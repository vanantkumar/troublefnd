

import re
import math


# ── Vocabulary dictionaries (term → log-probability weight) ───────────────────

FAKE_VOCAB: dict[str, float] = {
    # Sensationalist language
    "shocking": 3.2, "explosive": 3.1, "bombshell": 3.4, "secret": 2.8,
    "exposed": 2.9, "massive": 2.1, "incredible": 2.3, "unbelievable": 3.0,
    "hoax": 4.1, "coverup": 3.8, "cover-up": 3.8, "agenda": 2.7,
    "elite": 2.4, "cabal": 4.0, "crisis actor": 4.5,

    # Conspiracy / distrust phrases
    "you won't believe": 3.8, "they don't want": 3.5, "mainstream media": 2.6,
    "fake news": 3.0, "deep state": 4.2, "globalist": 3.9,
    "new world order": 4.5, "wake up sheeple": 4.3, "wake up": 2.8,
    "sheeple": 4.0, "truth they hide": 3.9,

    # Medical misinformation
    "miracle cure": 4.2, "doctors hate": 4.0, "banned": 2.8, "suppressed": 3.1,
    "big pharma": 3.5, "chemtrail": 4.3, "5g causes": 4.2,

    # Engagement bait
    "must share": 3.7, "share before deleted": 4.2, "share before removed": 4.2,
    "going viral": 2.1, "100%": 2.2, "guaranteed": 2.1, "clickbait": 3.0,

    # Political inflammatory
    "rigged": 3.2, "stolen election": 3.8, "fraud": 2.7, "radical": 2.0,
    "destroy": 2.0, "expose": 2.1, "outrage": 2.6, "scandal": 2.5,

    # Weak attribution
    "anonymous sources": 2.5, "unnamed officials": 2.6, "reportedly": 1.4,
    "allegedly": 1.6, "sources say": 2.0, "claim": 1.5, "rumor": 2.8,

    # Emotional manipulation
    "urgent": 2.3, "breaking": 1.7, "viral": 1.9, "exclusive": 2.2,
    "shocking truth": 3.9, "what they don't": 3.5, "illuminati": 4.4,
}

REAL_VOCAB: dict[str, float] = {
    # Source attribution
    "according to": 2.1, "said in a statement": 2.3, "spokesperson": 2.0,
    "confirmed": 1.8, "announced": 1.6, "told reporters": 2.0,
    "press conference": 1.9, "official statement": 2.1,

    # Research & data
    "study": 1.8, "research": 1.7, "analysis": 1.9, "data": 1.8,
    "published": 1.7, "journal": 2.0, "university": 1.9,
    "scientists": 1.8, "experts": 1.6, "statistics": 2.0,
    "survey": 1.7, "poll": 1.5, "percent": 1.6, "findings": 1.8,

    # Government / institutions
    "parliament": 1.8, "senate": 1.7, "minister": 1.6,
    "department": 1.5, "committee": 1.7, "government": 1.3,
    "officials": 1.5, "court": 1.6, "ruling": 1.7,
    "verdict": 1.8, "evidence": 1.9, "investigation": 1.7,

    # Financial / economic
    "billion": 1.4, "million": 1.4, "market": 1.3, "index": 1.5,
    "economy": 1.4, "gdp": 1.9, "inflation": 1.6, "fiscal": 1.8,

    # Health / science
    "clinical trial": 2.1, "peer reviewed": 2.3, "vaccine": 1.2,
    "hospital": 1.6, "health": 1.3, "climate": 1.4, "census": 2.0,

    # Neutral reporting verbs
    "said": 1.2, "told": 1.2, "reported": 1.3, "cited": 1.6,
    "noted": 1.4, "added": 1.3, "stated": 1.4, "explained": 1.3,
}

SENSATIONAL_TERMS = [
    "shocking", "incredible", "unbelievable", "bombshell", "explosive",
    "outrage", "urgent", "must share", "wake up", "you won't believe",
    "they don't want", "miracle cure", "banned", "suppressed",
    "going viral", "share before deleted", "breaking news",
]

HEDGE_WORDS = [
    "allegedly", "reportedly", "sources say", "unnamed", "anonymous",
    "claimed", "purportedly", "unverified", "rumored",
]


class FakeNewsClassifier:
    """
    Naive Bayes classifier with hand-crafted TF-IDF-like vocabulary weights.
    Augmented with linguistic feature extraction (CAPS ratio, exclamations,
    sentence length, sensational term density).
    """

    def __init__(self):
        self.fake_vocab = FAKE_VOCAB
        self.real_vocab = REAL_VOCAB
        self.sensational = SENSATIONAL_TERMS
        self.hedge_words = HEDGE_WORDS

    # ── Feature extraction ─────────────────────────────────────────────────────
    def _extract_features(self, text: str) -> dict:
        lower = text.lower()
        words = re.split(r"\s+", lower.strip())
        total_words = max(len(words), 1)

        # Vocabulary scoring (TF-IDF weighted Naive Bayes log-likelihood)
        fake_score = 0.0
        real_score = 0.0
        matched_fake = []
        matched_real = []

        for term, weight in self.fake_vocab.items():
            if term in lower:
                fake_score += weight
                matched_fake.append(term)

        for term, weight in self.real_vocab.items():
            if term in lower:
                real_score += weight
                matched_real.append(term)

        # Linguistic features
        caps_words = len(re.findall(r"\b[A-Z]{3,}\b", text))
        caps_ratio = round((caps_words / total_words) * 100)
        exclaims = len(re.findall(r"!", text))
        questions = len(re.findall(r"\?", text))
        sensational = sum(1 for s in self.sensational if s in lower)
        hedges = sum(1 for h in self.hedge_words if h in lower)
        avg_word_len = sum(len(w) for w in words) / total_words
        sentences = re.split(r"[.!?]+", text)
        sentences = [s for s in sentences if len(s.strip()) > 5]
        avg_sent_len = round(total_words / max(len(sentences), 1))

        # Adjust scores with linguistic signals
        fake_score += caps_ratio * 0.15
        fake_score += exclaims * 0.45
        fake_score += sensational * 1.3
        fake_score += questions * 0.2
        real_score += hedges * 0.5
        real_score += (1.8 if avg_word_len > 5.5 else 0)
        real_score += (1.2 if avg_sent_len > 18 else 0)

        # Posterior probability (Naive Bayes)
        total = fake_score + real_score + 1e-9
        real_prob = min(95, max(5, round((real_score / total) * 100)))

        return {
            "fake_score": round(fake_score, 2),
            "real_score": round(real_score, 2),
            "real_prob": real_prob,
            "matched_fake": matched_fake[:8],
            "matched_real": matched_real[:8],
            "features": {
                "word_count": total_words,
                "caps_ratio": caps_ratio,
                "exclaims": exclaims,
                "sensational": sensational,
                "hedges": hedges,
                "avg_word_len": round(avg_word_len, 1),
                "avg_sent_len": avg_sent_len,
            },
        }

    # ── Public API ─────────────────────────────────────────────────────────────
    def predict(self, text: str) -> dict:
        """
        Run the classifier on input text.
        Returns a dict with verdict, probability, matched signals, features.
        """
        if not text or not text.strip():
            return {
                "verdict": "NO_INPUT",
                "real_prob": 50,
                "fake_score": 0,
                "real_score": 0,
                "matched_fake": [],
                "matched_real": [],
                "features": {
                    "word_count": 0, "caps_ratio": 0, "exclaims": 0,
                    "sensational": 0, "hedges": 0,
                    "avg_word_len": 0, "avg_sent_len": 0,
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

        return {
            "verdict": verdict,
            **result,
        }
