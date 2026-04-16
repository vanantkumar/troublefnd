# model.py

import joblib

class MLModel:
    def __init__(self):
        try:
            self.model = joblib.load("model.pkl")  # your trained model
        except:
            self.model = None

    def predict(self, text):
        if self.model is None:
            return {"label": "Unknown", "confidence": 0}

        try:
            pred = self.model.predict([text])[0]
            prob = self.model.predict_proba([text]).max()

            label = "Fake" if pred == 1 else "Real"

            return {
                "label": label,
                "confidence": round(prob * 100, 2)
            }
        except:
            return {"label": "Error", "confidence": 0}
