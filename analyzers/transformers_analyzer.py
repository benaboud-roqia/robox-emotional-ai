from transformers import pipeline

_pipe = None

def _get_pipeline():
    global _pipe
    if _pipe is None:
        _pipe = pipeline("sentiment-analysis",
                         model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                         truncation=True, max_length=512)
    return _pipe

MAP = {"positive":"positif","negative":"négatif","neutral":"neutre",
       "POSITIVE":"positif","NEGATIVE":"négatif","NEUTRAL":"neutre",
       "LABEL_0":"négatif","LABEL_1":"neutre","LABEL_2":"positif"}

def analyze(text):
    try:
        r = _get_pipeline()(text[:512])[0]
        label = MAP.get(r["label"], "neutre")
        return {"source": "Transformers", "label": label, "score": round(r["score"], 3)}
    except Exception:
        return {"source": "Transformers", "label": "neutre", "score": 0.5}
