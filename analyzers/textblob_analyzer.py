from textblob import TextBlob

def analyze(text):
    b = TextBlob(text)
    p = b.sentiment.polarity
    label = "positif" if p > 0.1 else ("négatif" if p < -0.1 else "neutre")
    return {"source": "TextBlob", "label": label, "polarity": round(p, 3)}
