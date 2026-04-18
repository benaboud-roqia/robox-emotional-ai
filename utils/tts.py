from gtts import gTTS
import io, re

def speak(text, lang="fr"):
    clean = re.sub(r'[^\w\s\.,!?;:\'\-àâäéèêëîïôùûüçœæ]', '', text).strip() or "..."
    tts = gTTS(text=clean[:500], lang=lang, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()
