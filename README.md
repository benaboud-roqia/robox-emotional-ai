# 🤖 Robox — Assistant Émotionnel Intelligent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![Claude AI](https://img.shields.io/badge/Claude_AI-Anthropic-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Robox** est un chatbot intelligent de détection et d'analyse des sentiments.  
Il parle naturellement en **français**, **anglais** et **darija algérienne** 🇩🇿  
et génère des **rapports de diagnostic émotionnel** complets en PDF.

</div>

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🧠 **Analyse triple** | TextBlob + VADER + RoBERTa fusionnés |
| 🤖 **Claude AI** | Réponses intelligentes et empathiques |
| 🎤 **Vocal avancé** | Détection de 16 émotions vocales (pleurs, peur, joie...) |
| 📷 **Vision** | Analyse photo/selfie via Claude Vision |
| 📄 **PDF Diagnostic** | Rapport complet avec graphique, diagnostic et signature |
| 🌍 **Multilingue** | FR / EN / AR avec RTL automatique |
| 🎭 **Personnalités** | Auto / Drôle / Sérieux / Coach |
| 💾 **Persistance** | Historique des conversations en SQLite |
| 🌙 **Dark/Light** | Mode sombre et clair |
| 📱 **Responsive** | Interface 100% mobile |

---

## 🚀 Installation rapide

### Windows — Double-clic
```
Double-cliquer sur start_robox.bat
```
Le script installe tout et ouvre le navigateur automatiquement.

### Manuel
```bash
# 1. Cloner le repo
git clone https://github.com/ton-username/robox-emotional-chatbot.git
cd robox-emotional-chatbot

# 2. Installer les dépendances
pip install -r requirements.txt
python -m textblob.download_corpora

# 3. Configurer la clé API
cp config.example.py config.py
# Éditer config.py et mettre ta clé Anthropic

# 4. Lancer
python app.py
```

Ouvrir **http://localhost:5000** dans Chrome.

---

## 🔑 Configuration

Copie `config.example.py` en `config.py` et remplis ta clé :

```python
ANTHROPIC_API_KEY = "sk-ant-..."   # https://console.anthropic.com
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1024
```

> ⚠️ **Ne jamais publier `config.py` sur GitHub** — il est dans `.gitignore`

---

## 🏗️ Structure du projet

```
robox-emotional-chatbot/
├── app.py                          # Serveur Flask principal
├── config.py                       # Clés API (non versionné)
├── config.example.py               # Template de configuration
├── requirements.txt                # Dépendances Python
├── start_robox.bat                 # Lanceur Windows
│
├── analyzers/                      # Moteurs d'analyse sentiment
│   ├── textblob_analyzer.py        # Analyse lexicale
│   ├── vader_analyzer.py           # Analyse sociale
│   ├── transformers_analyzer.py    # RoBERTa deep learning
│   └── fusion.py                   # Fusion des 3 résultats
│
├── chatbot/
│   └── robox.py                    # Personnalités & prompts Claude
│
├── vision/
│   └── image_analyzer.py           # Analyse photo via Claude Vision
│
├── utils/
│   ├── database.py                 # Persistance SQLite
│   ├── pdf_generator.py            # Génération rapport PDF
│   ├── tts.py                      # Text-to-Speech (gTTS)
│   └── vocal_emotion.py            # Détection émotions vocales
│
├── templates/
│   └── index.html                  # Interface web complète
│
└── data/
    └── robox.db                    # Base de données (auto-créée)
```

---

## 🎤 Émotions vocales détectées

Robox détecte automatiquement **16 états émotionnels** dans la voix :

😢 Pleurs · 😨 Peur · 😰 Stress · 😞 Tristesse · 😡 Colère  
😊 Joie · 🤩 Excitation · 😌 Confort · 😣 Inconfort · 🤕 Douleur  
🥺 Solitude · 😴 Fatigue · 😕 Confusion · 🌟 Espoir · ❤️ Amour · 🙏 Gratitude

---

## 📄 Rapport PDF

Le rapport généré contient :
- Informations personnelles (nom, âge, profession...)
- Dashboard émotionnel avec graphique d'évolution
- Synthèse des sentiments avec barres de progression
- **Diagnostic psycho-émotionnel** basé sur les données réelles
- Recommandations personnalisées
- Historique complet de la conversation
- Signature électronique digitale

---

## 🛠️ Technologies utilisées

- **Backend** : Python 3.10+, Flask
- **IA** : Claude AI (Anthropic), HuggingFace Transformers (RoBERTa)
- **NLP** : TextBlob, VADER Sentiment
- **Base de données** : SQLite
- **PDF** : ReportLab
- **TTS** : gTTS (Google Text-to-Speech)
- **Frontend** : HTML5, CSS3, JavaScript vanilla

---

## 👥 Développeurs

<div align="center">

| Développeur | Rôle |
|---|---|
| **BENABOUD Roqia** | AI & SD|
| **BENABOUD Salah Eddine** | SI |
| **BENSAID Roxane Céline** |ISIK|

</div>

---
<img width="3452" height="1792" alt="C1" src="https://github.com/user-attachments/assets/3c4ccfbc-3d63-406b-b21d-6b1085235143" />
<img width="3437" height="1812" alt="C2" src="https://github.com/user-attachments/assets/4ba27353-a065-4e2d-9e49-707f25a3a110" />
<img width="1285" height="1445" alt="C3" src="https://github.com/user-attachments/assets/4a2252cf-caee-48d5-8d63-fed5500b6961" />
<img width="2220" height="520" alt="image" src="https://github.com/user-attachments/assets/cb50a291-9142-40df-a589-5b35ec7db828" />
<img width="2207" height="1625" alt="image" src="https://github.com/user-attachments/assets/820d4820-e2b3-47dd-8492-d061cf2a95de" />
<img width="2215" height="757" alt="image" src="https://github.com/user-attachments/assets/43b5997a-c389-450d-85a8-09284eab9da9" />




## 📝 Licence

Ce projet est sous licence **MIT** — libre d'utilisation, modification et distribution.

---

<div align="center">
Fait avec ❤️ en Algérie 🇩🇿
</div>
