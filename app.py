from flask import Flask, request, jsonify, render_template, session, send_file
from analyzers.fusion import analyze_all
from analyzers.transformers_analyzer import _get_pipeline
from chatbot.robox import chat
from vision.image_analyzer import analyze_image
from utils.pdf_generator import generate_pdf
from utils.tts import speak
from utils.database import (init_db, create_conversation, save_message,
    get_all_conversations, get_conversation_messages,
    delete_conversation, update_conv_title)
from utils.vocal_emotion import detect_vocal_emotion
import uuid, io, threading, base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
MAX_FREE_MESSAGES = 50

init_db()
threading.Thread(target=_get_pipeline, daemon=True).start()

def get_conv_id():
    if "conv_id" not in session:
        session["conv_id"] = str(uuid.uuid4())
    return session["conv_id"]

@app.route("/")
def index():
    session["history"] = []
    session["sentiments"] = []
    session["start"] = datetime.now().strftime("%d/%m/%Y à %H:%M")
    session["msg_count"] = 0
    session.pop("conv_id", None)
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_route():
    count = session.get("msg_count", 0)
    if count >= MAX_FREE_MESSAGES:
        return jsonify({"reply": "⭐ Limite de 50 messages atteinte. Passe à Premium!", "limit": True})

    data = request.get_json()
    msg = data.get("message", "").strip()
    lang = data.get("lang", "auto")
    personality = data.get("personality", "auto")
    vocal_emotion = data.get("vocal_emotion", None)

    if not msg:
        return jsonify({"error": "vide"}), 400

    conv_id = get_conv_id()

    # Créer la conversation si première fois
    if count == 0:
        title = msg[:50] + ("..." if len(msg) > 50 else "")
        create_conversation(conv_id, title, lang, personality)

    sentiment = analyze_all(msg)
    history = session.get("history", [])
    history.append({"role": "user", "content": msg})

    # Enrichir le contexte avec l'émotion vocale
    vocal_hint = ""
    if vocal_emotion and vocal_emotion != "neutre":
        from utils.vocal_emotion import EMOTION_PATTERNS
        hint = EMOTION_PATTERNS.get(vocal_emotion, {}).get("response_hint", "")
        if hint:
            vocal_hint = f"\n\n[ÉMOTION VOCALE DÉTECTÉE]: {vocal_emotion}. {hint}"

    reply = chat(history, sentiment, lang, personality, vocal_hint)
    history.append({"role": "assistant", "content": reply})
    session["history"] = history
    session["sentiments"] = session.get("sentiments", []) + [sentiment]
    session["msg_count"] = count + 1

    # Sauvegarder en base
    save_message(conv_id, "user", msg, sentiment, vocal_emotion)
    save_message(conv_id, "assistant", reply)

    return jsonify({
        "reply": reply,
        "sentiment": sentiment,
        "msg_count": session["msg_count"],
        "max_messages": MAX_FREE_MESSAGES,
        "conv_id": conv_id
    })

@app.route("/tts", methods=["POST"])
def tts_route():
    data = request.get_json()
    text = data.get("text", "").strip()
    lang = data.get("lang", "fr")
    if not text:
        return jsonify({"error": "vide"}), 400
    audio = speak(text, lang)
    return send_file(io.BytesIO(audio), mimetype="audio/mpeg", download_name="r.mp3")

@app.route("/analyze-image", methods=["POST"])
def image_route():
    if "image" not in request.files:
        return jsonify({"error": "no image", "message": "Aucune image reçue", "emotions": [], "sentiment": "neutre", "confidence": "faible"}), 200
    f = request.files["image"]
    if not f or f.filename == "":
        return jsonify({"error": "empty", "message": "Fichier vide", "emotions": [], "sentiment": "neutre", "confidence": "faible"}), 200
    try:
        result = analyze_image(f.read(), f.content_type or "image/jpeg")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "message": "Je n'arrive pas à analyser cette image 😅", "emotions": [], "sentiment": "neutre", "confidence": "faible"}), 200

@app.route("/conversations")
def conversations_route():
    convs = get_all_conversations()
    return jsonify(convs)

@app.route("/conversation/<conv_id>")
def load_conversation(conv_id):
    msgs = get_conversation_messages(conv_id)
    return jsonify(msgs)

@app.route("/conversation/<conv_id>", methods=["DELETE"])
def delete_conv(conv_id):
    delete_conversation(conv_id)
    return jsonify({"ok": True})

@app.route("/history")
def history_route():
    return jsonify({
        "history": session.get("history", []),
        "sentiments": session.get("sentiments", []),
        "start": session.get("start", ""),
        "msg_count": session.get("msg_count", 0),
        "conv_id": session.get("conv_id", "")
    })

@app.route("/export-pdf", methods=["POST"])
def pdf_route():
    data = request.get_json() or {}
    
    # Récupérer l'historique depuis la session OU depuis la DB si conv_id fourni
    conv_id = data.get("conv_id") or session.get("conv_id")
    h = session.get("history", [])
    sentiments = session.get("sentiments", [])
    
    # Si on a un conv_id et pas assez en session, charger depuis DB
    if conv_id and len([m for m in h if m["role"]=="user"]) < 10:
        from utils.database import get_conversation_messages
        db_msgs = get_conversation_messages(conv_id)
        h = [{"role": m["role"], "content": m["content"]} for m in db_msgs]
        sentiments = [m["sentiment"] for m in db_msgs if m["role"]=="user" and m.get("sentiment")]
        sentiments = [s for s in sentiments if s]

    user_msgs = [m for m in h if m["role"] == "user"]
    if len(user_msgs) < 10:
        return jsonify({"error": "min10", "count": len(user_msgs)}), 400

    user_info = data.get("user_info", {})
    signature_b64 = data.get("signature", "")
    sig_bytes = None
    if signature_b64:
        try:
            sig_bytes = base64.b64decode(signature_b64.split(",")[-1])
        except Exception:
            sig_bytes = None

    try:
        pdf = generate_pdf(h, sentiments, session.get("start", ""), user_info, sig_bytes)
        name = f"rapport_robox_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        return send_file(io.BytesIO(pdf), mimetype="application/pdf", as_attachment=True, download_name=name)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset_route():
    session["history"] = []
    session["sentiments"] = []
    session["start"] = datetime.now().strftime("%d/%m/%Y à %H:%M")
    session["msg_count"] = 0
    session.pop("conv_id", None)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, port=5000)
