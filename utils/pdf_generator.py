from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether, Image as RLImage)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, String
from datetime import datetime
import io

# Couleurs
BLUE    = colors.HexColor("#1d4ed8")
BLUE2   = colors.HexColor("#3b82f6")
BLUE_BG = colors.HexColor("#eff6ff")
BLUE_BD = colors.HexColor("#bfdbfe")
DARK    = colors.HexColor("#1e293b")
GRAY    = colors.HexColor("#64748b")
LGRAY   = colors.HexColor("#f8fafc")
GREEN   = colors.HexColor("#16a34a")
RED     = colors.HexColor("#dc2626")
YELLOW  = colors.HexColor("#d97706")
PURPLE  = colors.HexColor("#7c3aed")
WHITE   = colors.white

W = A4[0] - 4.4*cm  # largeur utile

def slabel(l):
    return "Positif 😊" if l=="positif" else ("Négatif 😞" if l=="négatif" else "Neutre 😐")

def scolor(l):
    return GREEN if l=="positif" else (RED if l=="négatif" else YELLOW)

def make_sentiment_chart(sentiments, width=None, height=100):
    w = width or W
    d = Drawing(w, height)
    # Fond
    d.add(Rect(0, 0, w, height, fillColor=BLUE_BG, strokeColor=BLUE_BD, strokeWidth=0.5, rx=4, ry=4))

    if not sentiments or len(sentiments) < 2:
        d.add(String(w/2, height/2, "Pas assez de données (min. 2 messages)",
                     textAnchor="middle", fontSize=9, fillColor=GRAY))
        return d

    scores = [max(-1, min(1, s.get("average_score", 0))) for s in sentiments]
    n = len(scores)
    pad_x, pad_y = 35, 15
    cw = w - 2*pad_x
    ch = height - 2*pad_y
    zero_y = pad_y + ch/2

    # Zones colorées
    d.add(Rect(pad_x, zero_y, cw, ch/2, fillColor=colors.HexColor("#f0fdf4"), strokeWidth=0))
    d.add(Rect(pad_x, pad_y, cw, ch/2, fillColor=colors.HexColor("#fef2f2"), strokeWidth=0))

    # Grille
    for i in range(3):
        y = pad_y + i*(ch/2)
        d.add(Line(pad_x, y, pad_x+cw, y, strokeColor=BLUE_BD, strokeWidth=0.4))

    # Labels Y
    d.add(String(pad_x-4, zero_y+ch/2-4, "+1", textAnchor="end", fontSize=7, fillColor=GREEN))
    d.add(String(pad_x-4, zero_y-3, "0", textAnchor="end", fontSize=7, fillColor=GRAY))
    d.add(String(pad_x-4, pad_y-3, "-1", textAnchor="end", fontSize=7, fillColor=RED))

    # Points et lignes
    pts = []
    for i, sc in enumerate(scores):
        x = pad_x + (i/(n-1))*cw if n > 1 else pad_x + cw/2
        y = zero_y + sc*(ch/2)
        pts.append((x, y))

    # Ligne de tendance
    for i in range(len(pts)-1):
        x1,y1 = pts[i]; x2,y2 = pts[i+1]
        avg = (y1+y2)/2
        col = GREEN if avg > zero_y+2 else (RED if avg < zero_y-2 else BLUE2)
        d.add(Line(x1, y1, x2, y2, strokeColor=col, strokeWidth=1.8))

    # Points
    for i,(x,y) in enumerate(pts):
        sc = scores[i]
        col = GREEN if sc > 0.2 else (RED if sc < -0.2 else YELLOW)
        d.add(Circle(x, y, 3.5, fillColor=col, strokeColor=WHITE, strokeWidth=1))

    # Titre
    d.add(String(w/2, height-8, "Évolution émotionnelle au fil de la conversation",
                 textAnchor="middle", fontSize=8, fillColor=DARK))
    return d

def make_bar(label, value, max_val, color, width=None):
    """Barre de progression horizontale."""
    w = width or W
    bar_w = w - 6*cm
    pct = min(value/max_val, 1) if max_val > 0 else 0
    d = Drawing(w, 18)
    d.add(String(0, 4, label, fontSize=8, fillColor=DARK))
    d.add(Rect(3.5*cm, 2, bar_w, 12, fillColor=colors.HexColor("#e2e8f0"), strokeWidth=0, rx=4, ry=4))
    if pct > 0:
        d.add(Rect(3.5*cm, 2, bar_w*pct, 12, fillColor=color, strokeWidth=0, rx=4, ry=4))
    d.add(String(3.5*cm + bar_w + 4, 4, f"{value}", fontSize=8, fillColor=GRAY))
    return d

def generate_pdf(history, sentiments, session_start, user_info=None, sig_bytes=None):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=2.2*cm, leftMargin=2.2*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm
    )

    # Styles
    def sty(name, **kw):
        base = dict(fontName="Helvetica", fontSize=10, textColor=DARK, leading=14)
        base.update(kw)
        return ParagraphStyle(name, **base)

    S_TITLE  = sty("title",  fontSize=18, textColor=BLUE,  alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=3, leading=22)
    S_SUB    = sty("sub",    fontSize=9,  textColor=GRAY,  alignment=TA_CENTER, spaceAfter=2)
    S_H1     = sty("h1",     fontSize=12, textColor=BLUE,  fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=5)
    S_BODY   = sty("body",   fontSize=9,  leading=13, alignment=TA_JUSTIFY)
    S_SMALL  = sty("small",  fontSize=8,  textColor=GRAY)
    S_BOLD   = sty("bold",   fontSize=9,  fontName="Helvetica-Bold")
    S_FOOTER = sty("footer", fontSize=7,  textColor=GRAY, alignment=TA_CENTER)
    S_LABEL  = sty("label",  fontSize=8,  textColor=BLUE, fontName="Helvetica-Bold")

    story = []
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")
    user_msgs = [m for m in history if m["role"] == "user"]
    n_msgs = len(user_msgs)

    # ══ HEADER ══════════════════════════════════════════════════════
    story += [
        Spacer(1, .1*cm),
        Paragraph("RAPPORT DE DIAGNOSTIC ÉMOTIONNEL", S_TITLE),
        Paragraph("Analyse des Sentiments &amp; Profil Psycho-Émotionnel", S_SUB),
        Paragraph("Généré par Robox — Assistant Intelligent en Santé Émotionnelle", S_SUB),
        Spacer(1, .3*cm),
        HRFlowable(width="100%", thickness=2.5, color=BLUE, spaceAfter=4),
        Spacer(1, .2*cm),
    ]

    # ══ INFOS PERSONNELLES ══════════════════════════════════════════
    if user_info and any(user_info.get(k,"").strip() for k in ["nom","prenom","age","email","tel","profession"]):
        story.append(Paragraph("▌ INFORMATIONS PERSONNELLES", S_H1))
        story.append(HRFlowable(width="100%", thickness=.5, color=BLUE2, spaceAfter=4))

        fields = [
            ("Nom complet", f"{user_info.get('prenom','')} {user_info.get('nom','')}".strip()),
            ("Âge", user_info.get("age","")),
            ("Profession", user_info.get("profession","")),
            ("Email", user_info.get("email","")),
            ("Téléphone", user_info.get("tel","")),
        ]
        rows = [[Paragraph(f"<b>{k}</b>", S_LABEL), Paragraph(v or "—", S_BODY)]
                for k,v in fields if v]

        if rows:
            t = Table(rows, colWidths=[4*cm, W-4*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0),(0,-1), BLUE_BG),
                ("GRID", (0,0),(-1,-1), .3, BLUE_BD),
                ("PADDING", (0,0),(-1,-1), 6),
                ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, BLUE_BG]),
            ]))
            story += [t, Spacer(1, .4*cm)]

    # ══ INFOS SESSION ═══════════════════════════════════════════════
    story.append(Paragraph("▌ INFORMATIONS DE SESSION", S_H1))
    story.append(HRFlowable(width="100%", thickness=.5, color=BLUE2, spaceAfter=4))

    sess_rows = [
        [Paragraph("<b>Date du rapport</b>", S_LABEL), Paragraph(now, S_BODY)],
        [Paragraph("<b>Début de session</b>", S_LABEL), Paragraph(session_start or "—", S_BODY)],
        [Paragraph("<b>Nombre d'échanges</b>", S_LABEL), Paragraph(f"{n_msgs} messages utilisateur", S_BODY)],
        [Paragraph("<b>Durée estimée</b>", S_LABEL), Paragraph(f"~{n_msgs*2} minutes", S_BODY)],
    ]
    t = Table(sess_rows, colWidths=[4*cm, W-4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,-1), BLUE_BG),
        ("GRID", (0,0),(-1,-1), .3, BLUE_BD),
        ("PADDING", (0,0),(-1,-1), 6),
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, BLUE_BG]),
    ]))
    story += [t, Spacer(1, .4*cm)]

    # ══ DASHBOARD ÉMOTIONNEL ════════════════════════════════════════
    if sentiments and len(sentiments) >= 2:
        story.append(Paragraph("▌ DASHBOARD ÉMOTIONNEL", S_H1))
        story.append(HRFlowable(width="100%", thickness=.5, color=BLUE2, spaceAfter=4))
        story.append(make_sentiment_chart(sentiments, width=W))
        story.append(Spacer(1, .3*cm))

    # ══ SYNTHÈSE SENTIMENTS ═════════════════════════════════════════
    if sentiments:
        scores = [s.get("average_score", 0) for s in sentiments]
        avg = sum(scores)/len(scores)
        pos = sum(1 for s in sentiments if s.get("final_label")=="positif")
        neg = sum(1 for s in sentiments if s.get("final_label")=="négatif")
        neu = len(sentiments)-pos-neg
        gl  = "positif" if avg>.2 else ("négatif" if avg<-.2 else "neutre")
        total = len(sentiments)

        story.append(Paragraph("▌ SYNTHÈSE DES SENTIMENTS", S_H1))
        story.append(HRFlowable(width="100%", thickness=.5, color=BLUE2, spaceAfter=4))

        # Tableau synthèse
        synth_rows = [
            [Paragraph("<b>Tendance générale</b>", S_LABEL),
             Paragraph(f"<b><font color='#{('16a34a' if gl=='positif' else ('dc2626' if gl=='négatif' else 'd97706'))}'>{slabel(gl)}</font></b>", S_BODY)],
            [Paragraph("<b>Score moyen</b>", S_LABEL),
             Paragraph(f"{avg:.3f}  &nbsp;(de -1.0 très négatif à +1.0 très positif)", S_BODY)],
            [Paragraph("<b>Messages positifs</b>", S_LABEL),
             Paragraph(f"{pos} / {total}  ({int(pos/total*100) if total else 0}%)", S_BODY)],
            [Paragraph("<b>Messages neutres</b>", S_LABEL),
             Paragraph(f"{neu} / {total}  ({int(neu/total*100) if total else 0}%)", S_BODY)],
            [Paragraph("<b>Messages négatifs</b>", S_LABEL),
             Paragraph(f"{neg} / {total}  ({int(neg/total*100) if total else 0}%)", S_BODY)],
        ]
        t = Table(synth_rows, colWidths=[4*cm, W-4*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(0,-1), BLUE_BG),
            ("GRID", (0,0),(-1,-1), .3, BLUE_BD),
            ("PADDING", (0,0),(-1,-1), 6),
            ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, BLUE_BG]),
        ]))
        story += [t, Spacer(1, .3*cm)]

        # Barres de répartition
        story.append(make_bar("Positif", pos, total, GREEN, width=W))
        story.append(make_bar("Neutre", neu, total, YELLOW, width=W))
        story.append(make_bar("Négatif", neg, total, RED, width=W))
        story.append(Spacer(1, .4*cm))

        # ══ DIAGNOSTIC PSYCHO-ÉMOTIONNEL ════════════════════════════
        story.append(Paragraph("▌ DIAGNOSTIC PSYCHO-ÉMOTIONNEL", S_H1))
        story.append(HRFlowable(width="100%", thickness=.5, color=BLUE2, spaceAfter=4))

        # Analyse basée sur les vraies données
        if avg > 0.5:
            etat = "Excellent état émotionnel"
            desc = ("L'analyse révèle un état émotionnel <b>très positif et stable</b>. "
                    "La personne exprime une énergie constructive, de l'enthousiasme et une attitude optimiste. "
                    "Les échanges témoignent d'un bien-être général solide.")
            reco = ("• Maintenir les habitudes positives actuelles\n"
                    "• Partager cette énergie avec l'entourage\n"
                    "• Continuer à cultiver les sources de joie identifiées")
        elif avg > 0.2:
            etat = "Bon état émotionnel"
            desc = ("L'analyse révèle un état émotionnel <b>globalement positif</b>. "
                    "La personne montre une bonne résilience émotionnelle avec quelques variations normales. "
                    "L'équilibre général est satisfaisant.")
            reco = ("• Identifier et renforcer les sources de bien-être\n"
                    "• Pratiquer la pleine conscience au quotidien\n"
                    "• Maintenir des connexions sociales positives")
        elif avg > -0.2:
            etat = "État émotionnel équilibré"
            desc = ("L'analyse révèle un état émotionnel <b>neutre à mixte</b>. "
                    "La personne alterne entre différents états sans dominante marquée. "
                    "Une attention particulière au bien-être quotidien est conseillée.")
            reco = ("• Explorer les sources de stress ou d'inconfort\n"
                    "• Pratiquer des activités ressourçantes\n"
                    "• Envisager un accompagnement si les fluctuations persistent")
        elif avg > -0.5:
            etat = "État émotionnel difficile"
            desc = ("L'analyse révèle un état émotionnel <b>négatif</b>. "
                    "Des signes de stress, de tristesse ou de frustration ont été détectés de manière récurrente. "
                    "Un soutien bienveillant est recommandé.")
            reco = ("• Parler à un proche de confiance\n"
                    "• Consulter un professionnel de santé mentale\n"
                    "• Pratiquer des techniques de relaxation (respiration, méditation)\n"
                    "• Réduire les sources de stress identifiées")
        else:
            etat = "État émotionnel très difficile"
            desc = ("L'analyse révèle un état émotionnel <b>très négatif et persistant</b>. "
                    "Des signes importants de détresse émotionnelle ont été détectés. "
                    "Une consultation professionnelle est fortement recommandée.")
            reco = ("• Consulter un médecin ou psychologue rapidement\n"
                    "• Ne pas rester seul(e) avec ces émotions\n"
                    "• Contacter une ligne d'écoute si nécessaire\n"
                    "• Informer un proche de confiance de votre état")

        diag_rows = [
            [Paragraph("<b>État détecté</b>", S_LABEL), Paragraph(f"<b>{etat}</b>", S_BODY)],
            [Paragraph("<b>Analyse</b>", S_LABEL), Paragraph(desc, S_BODY)],
            [Paragraph("<b>Recommandations</b>", S_LABEL), Paragraph(reco.replace("\n","<br/>"), S_BODY)],
        ]
        t = Table(diag_rows, colWidths=[4*cm, W-4*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(0,-1), BLUE_BG),
            ("GRID", (0,0),(-1,-1), .3, BLUE_BD),
            ("PADDING", (0,0),(-1,-1), 7),
            ("VALIGN", (0,0),(-1,-1), "TOP"),
            ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, BLUE_BG]),
        ]))
        story += [t, Spacer(1, .4*cm)]

    # ══ HISTORIQUE ══════════════════════════════════════════════════
    story.append(Paragraph("▌ HISTORIQUE DE LA CONVERSATION", S_H1))
    story.append(HRFlowable(width="100%", thickness=.5, color=BLUE2, spaceAfter=4))

    si = 0
    for m in history:
        txt = m["content"][:400] + ("..." if len(m["content"]) > 400 else "")
        if m["role"] == "user":
            s = sentiments[si] if si < len(sentiments) else None
            si += 1
            lbl = f" [{slabel(s['final_label'])}]" if s else ""
            row = [[Paragraph(f"<b>👤 Vous{lbl}</b>", S_SMALL), Paragraph(txt, S_BODY)]]
            bg = BLUE_BG
        else:
            row = [[Paragraph("<b>🤖 Robox</b>", S_SMALL), Paragraph(txt, S_BODY)]]
            bg = WHITE
        t = Table(row, colWidths=[3.2*cm, W-3.2*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), bg),
            ("VALIGN", (0,0),(-1,-1), "TOP"),
            ("GRID", (0,0),(-1,-1), .25, BLUE_BD),
            ("PADDING", (0,0),(-1,-1), 5),
        ]))
        story += [KeepTogether(t), Spacer(1, .06*cm)]

    # ══ SIGNATURE ═══════════════════════════════════════════════════
    story += [Spacer(1, .4*cm), Paragraph("▌ SIGNATURE ÉLECTRONIQUE", S_H1),
              HRFlowable(width="100%", thickness=.5, color=BLUE2, spaceAfter=4)]

    sig_name = ""
    if user_info:
        sig_name = f"{user_info.get('prenom','')} {user_info.get('nom','')}".strip()

    sig_rows = [
        [Paragraph("<b>Signataire</b>", S_LABEL), Paragraph(sig_name or "—", S_BODY)],
        [Paragraph("<b>Date</b>", S_LABEL), Paragraph(now, S_BODY)],
    ]

    if sig_bytes:
        try:
            img = RLImage(io.BytesIO(sig_bytes), width=5*cm, height=1.8*cm)
            sig_rows.append([Paragraph("<b>Signature</b>", S_LABEL), img])
        except Exception:
            sig_rows.append([Paragraph("<b>Signature</b>", S_LABEL), Paragraph("Signature numérique apposée", S_BODY)])
    else:
        sig_rows.append([Paragraph("<b>Signature</b>", S_LABEL), Paragraph("Aucune signature fournie", S_SMALL)])

    t = Table(sig_rows, colWidths=[4*cm, W-4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,-1), BLUE_BG),
        ("GRID", (0,0),(-1,-1), .3, BLUE_BD),
        ("PADDING", (0,0),(-1,-1), 6),
        ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, BLUE_BG]),
    ]))
    story += [t, Spacer(1, .5*cm)]

    # ══ FOOTER ══════════════════════════════════════════════════════
    story += [
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, .15*cm),
        Paragraph(f"Rapport généré par Robox — Assistant Intelligent en Santé Émotionnelle | {now}", S_FOOTER),
        Paragraph("Ce rapport est confidentiel. Il ne remplace pas un avis médical professionnel.", S_FOOTER),
    ]

    doc.build(story)
    buf.seek(0)
    return buf.read()
