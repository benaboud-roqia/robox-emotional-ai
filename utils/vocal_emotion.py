"""
Analyse des émotions vocales basée sur les mots-clés et patterns du texte transcrit.
Détecte 20+ états émotionnels.
"""

import re

EMOTION_PATTERNS = {
    # Détresse
    "pleurs": {
        "keywords": ["je pleure", "je pleurs", "en larmes", "je chiale", "snif", "sniff", "bkiit", "nbki", "دموع", "بكاء", "نبكي"],
        "emoji": "😢", "color": "#3b82f6", "label": "Pleurs détectés",
        "response_hint": "La personne pleure. Sois très doux, empathique, écoute avant tout."
    },
    "peur": {
        "keywords": ["j'ai peur", "j'ai peur", "terrifié", "effrayé", "angoissé", "khayef", "خايف", "scared", "afraid", "terrified", "anxieux"],
        "emoji": "😨", "color": "#8b5cf6", "label": "Peur détectée",
        "response_hint": "La personne a peur. Rassure-la, sois calme et protecteur."
    },
    "stress": {
        "keywords": ["stressé", "stressée", "sous pression", "débordé", "overwhelmed", "stressed", "mstress", "مضغوط", "متوتر"],
        "emoji": "😰", "color": "#f59e0b", "label": "Stress détecté",
        "response_hint": "La personne est stressée. Aide-la à respirer, propose des solutions concrètes."
    },
    "tristesse": {
        "keywords": ["triste", "déprimé", "malheureux", "cafard", "mélancolique", "sad", "depressed", "7zin", "حزين", "مكتئب", "malheur"],
        "emoji": "😞", "color": "#6366f1", "label": "Tristesse détectée",
        "response_hint": "La personne est triste. Montre de la compassion, écoute sans juger."
    },
    "colere": {
        "keywords": ["en colère", "énervé", "furieux", "rage", "angry", "mad", "3ayyan", "غاضب", "متعصب", "je suis fou", "ça m'énerve"],
        "emoji": "😡", "color": "#ef4444", "label": "Colère détectée",
        "response_hint": "La personne est en colère. Reste calme, valide ses émotions sans alimenter la colère."
    },
    "joie": {
        "keywords": ["heureux", "heureuse", "content", "contente", "super", "génial", "happy", "joyeux", "farhan", "فرحان", "سعيد", "wah wah", "hamdullah"],
        "emoji": "😊", "color": "#10b981", "label": "Joie détectée",
        "response_hint": "La personne est heureuse. Partage sa joie, encourage-la à continuer."
    },
    "excitation": {
        "keywords": ["excité", "excitée", "trop bien", "incroyable", "amazing", "excited", "mthayyaj", "متحمس", "wow", "omg", "!!!"],
        "emoji": "🤩", "color": "#f59e0b", "label": "Excitation détectée",
        "response_hint": "La personne est très excitée. Partage son enthousiasme!"
    },
    "confort": {
        "keywords": ["bien", "à l'aise", "comfortable", "relaxé", "serein", "tranquille", "comfortable", "mriih", "مرتاح", "بخير", "ça va bien"],
        "emoji": "😌", "color": "#10b981", "label": "Confort détecté",
        "response_hint": "La personne se sent bien et à l'aise. Maintiens cette atmosphère positive."
    },
    "inconfort": {
        "keywords": ["mal à l'aise", "inconfortable", "gêné", "awkward", "uncomfortable", "msh mriih", "مش مرتاح", "ça me dérange"],
        "emoji": "😣", "color": "#f97316", "label": "Inconfort détecté",
        "response_hint": "La personne est mal à l'aise. Sois doux, demande ce qui la dérange."
    },
    "douleur": {
        "keywords": ["j'ai mal", "douleur", "ça fait mal", "souffrance", "pain", "hurts", "3andi wja3", "عندي وجع", "يؤلمني"],
        "emoji": "🤕", "color": "#ef4444", "label": "Douleur détectée",
        "response_hint": "La personne souffre physiquement. Montre de l'empathie, suggère de consulter si nécessaire."
    },
    "solitude": {
        "keywords": ["seul", "seule", "isolé", "personne", "lonely", "alone", "wahdi", "وحدي", "ما عندي حتى واحد"],
        "emoji": "🥺", "color": "#8b5cf6", "label": "Solitude détectée",
        "response_hint": "La personne se sent seule. Sois présent, chaleureux, fais-lui sentir qu'elle compte."
    },
    "fatigue": {
        "keywords": ["fatigué", "épuisé", "tired", "exhausted", "3ayyan", "عياان", "تعبان", "je suis crevé", "j'en peux plus"],
        "emoji": "😴", "color": "#94a3b8", "label": "Fatigue détectée",
        "response_hint": "La personne est fatiguée. Sois compréhensif, propose du repos et de la douceur."
    },
    "confusion": {
        "keywords": ["je comprends pas", "confus", "perdu", "confused", "lost", "mfhemsh", "ما فهمتش", "c'est quoi", "je sais pas"],
        "emoji": "😕", "color": "#f59e0b", "label": "Confusion détectée",
        "response_hint": "La personne est confuse. Explique clairement, sois patient et pédagogue."
    },
    "espoir": {
        "keywords": ["j'espère", "peut-être", "inshallah", "إن شاء الله", "hopefully", "on verra", "je crois que"],
        "emoji": "🌟", "color": "#10b981", "label": "Espoir détecté",
        "response_hint": "La personne garde espoir. Encourage-la, renforce cet optimisme."
    },
    "amour": {
        "keywords": ["je t'aime", "amour", "love", "7bib", "حبيبي", "❤️", "💕", "romantique", "mon cœur"],
        "emoji": "❤️", "color": "#ec4899", "label": "Amour détecté",
        "response_hint": "La personne exprime de l'amour. Sois chaleureux et bienveillant."
    },
    "gratitude": {
        "keywords": ["merci", "thank you", "شكراً", "شكرا", "reconnaissant", "grateful", "je suis touché", "c'est gentil"],
        "emoji": "🙏", "color": "#10b981", "label": "Gratitude détectée",
        "response_hint": "La personne est reconnaissante. Accueille sa gratitude avec chaleur."
    },
    "neutre": {
        "keywords": [],
        "emoji": "😐", "color": "#94a3b8", "label": "Neutre",
        "response_hint": ""
    }
}

def detect_vocal_emotion(text: str) -> dict:
    """Détecte l'émotion dans le texte transcrit."""
    if not text:
        return EMOTION_PATTERNS["neutre"]

    text_lower = text.lower()

    # Score par émotion
    scores = {}
    for emotion, data in EMOTION_PATTERNS.items():
        if emotion == "neutre":
            continue
        score = 0
        for kw in data["keywords"]:
            if kw.lower() in text_lower:
                score += 1
        if score > 0:
            scores[emotion] = score

    if not scores:
        return {**EMOTION_PATTERNS["neutre"], "emotion": "neutre", "confidence": "faible"}

    # Émotion dominante
    best = max(scores, key=scores.get)
    result = {**EMOTION_PATTERNS[best], "emotion": best, "confidence": "haute" if scores[best] > 1 else "moyenne"}
    return result

def get_all_emotions():
    """Retourne tous les états émotionnels possibles."""
    return {k: {"emoji": v["emoji"], "label": v["label"], "color": v["color"]}
            for k, v in EMOTION_PATTERNS.items()}
