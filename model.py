# model.py

import re

# ── Vocabulary dictionaries ─────────────────────────
FAKE_VOCAB = {
    "shocking": 3.2, "explosive": 3.1, "bombshell": 3.4,
    "secret": 2.8, "exposed": 2.9, "massive": 2.1,
    "incredible": 2.5, "breaking": 2.0, "viral": 2.2
}

REAL_VOCAB = {
    "government": 1.5, "policy": 1.7, "official": 1.6,
    "report": 1.8, "data": 1.5, "research": 1.9,
    "analysis": 1.6, "confirmed": 1.7
}


# ── Text Preprocessing ─────────────────────────
def preprocess(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    tokens = text.split()
    return tokens


# ── Fake News Classifier ─────────────────────────
class FakeNewsClassifier:
    def __init__(self):
        self.fake_vocab = FAKE_VOCAB
        self.real_vocab = REAL_VOCAB

    def score(self, tokens):
        fake_score = 0
        real_score = 0

        for word in tokens:
            fake_score += self.fake_vocab.get(word, 0)
            real_score += self.real_vocab.get(word, 0)

        return fake_score, real_score

    def predict(self, text: str):
        tokens = preprocess(text)

        if not tokens:
            return {
                "label": "Invalid",
                "confidence": 0,
                "reason": "No valid text provided"
            }

        fake_score, real_score = self.score(tokens)

        total = fake_score + real_score + 1e-6  # avoid division by zero

        if fake_score > real_score:
            label = "Fake News"
            confidence = fake_score / total
        else:
            label = "Real News"
            confidence = real_score / total

        return {
            "label": label,
            "confidence": round(confidence * 100, 2),
            "fake_score": round(fake_score, 2),
            "real_score": round(real_score, 2)
        }
