from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
_a = SentimentIntensityAnalyzer()

def analyze(text):
    c = _a.polarity_scores(text)["compound"]
    label = "positif" if c >= 0.05 else ("négatif" if c <= -0.05 else "neutre")
    return {"source": "VADER", "label": label, "compound": round(c, 3)}
