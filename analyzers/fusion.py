from . import textblob_analyzer, vader_analyzer, transformers_analyzer

S = {"positif": 1, "neutre": 0, "négatif": -1}

def analyze_all(text):
    tb = textblob_analyzer.analyze(text)
    vd = vader_analyzer.analyze(text)
    tr = transformers_analyzer.analyze(text)
    avg = sum(S.get(r["label"], 0) for r in [tb, vd, tr]) / 3
    if avg > 0.2:   final, emoji = "positif", "😊"
    elif avg < -0.2: final, emoji = "négatif", "😞"
    else:            final, emoji = "neutre",  "😐"
    return {"final_label": final, "emoji": emoji,
            "average_score": round(avg, 3), "details": [tb, vd, tr]}
