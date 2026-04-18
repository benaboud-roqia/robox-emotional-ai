import base64, json, re, anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def analyze_image(image_bytes, media_type="image/jpeg"):
    data = base64.standard_b64encode(image_bytes).decode("utf-8")
    prompt = """Analyse cette image. Réponds UNIQUEMENT en JSON:
{"emotions":["liste"],"sentiment":"positif|négatif|neutre","confidence":"haute|moyenne|faible","message":"commentaire chaleureux en français/darija comme un pote algérien"}"""
    try:
        resp = client.messages.create(
            model=CLAUDE_MODEL, max_tokens=MAX_TOKENS,
            messages=[{"role":"user","content":[
                {"type":"image","source":{"type":"base64","media_type":media_type,"data":data}},
                {"type":"text","text":prompt}
            ]}]
        )
        raw = resp.content[0].text
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        pass
    return {"emotions":[],"sentiment":"neutre","confidence":"faible","message":"Wallah j'arrive pas à analyser cette image 😅"}
