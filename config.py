"""
Configuration du Bot LBC Automation

⚙️ DEUX MODES DE CONFIGURATION :

1. Via l'interface web (RECOMMANDÉ) :
   - Lancez le bot : python main.py
   - Ouvrez : http://localhost:8000/config-page
   - Remplissez le formulaire
   - Vos paramètres seront sauvegardés dans config.env

2. Via le fichier config.env :
   - Copiez config.env.example vers config.env
   - Éditez config.env avec vos identifiants
   - Sauvegardez

💡 La configuration depuis config.env a la priorité sur les valeurs ci-dessous.
"""

import os
from pathlib import Path

# Fonction pour charger la config depuis config.env
def load_config():
    """Charge la configuration depuis config.env si disponible"""
    config_file = Path("config.env")
    
    if not config_file.exists():
        return None
    
    config = {}
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"').strip("'")
    except Exception as e:
        print(f"⚠️ Erreur lecture config.env: {e}")
        return None
    
    return config

# Charger depuis config.env ou utiliser les valeurs par défaut
_config = load_config()

# ==================== COMPTE LEBONCOIN ====================
EMAIL = _config.get("LEBONCOIN_EMAIL") if _config else os.getenv("LEBONCOIN_EMAIL", "votre_email@example.com")
PASSWORD = _config.get("LEBONCOIN_PASSWORD") if _config else os.getenv("LEBONCOIN_PASSWORD", "votre_mot_de_passe")

# ==================== GOOGLE SHEETS ====================
SHEET_NAME = _config.get("GOOGLE_SHEET_NAME") if _config else os.getenv("GOOGLE_SHEET_NAME", "LBC-Automation")

# ==================== PUBLICATION ====================
MAX_ADS_PER_RUN = int(_config.get("MAX_ADS_PER_RUN", "3")) if _config else int(os.getenv("MAX_ADS_PER_RUN", "3"))
DELAY_BETWEEN_ADS_MIN = int(_config.get("DELAY_BETWEEN_ADS_MIN", "300")) if _config else int(os.getenv("DELAY_BETWEEN_ADS_MIN", "300"))
DELAY_BETWEEN_ADS_MAX = int(_config.get("DELAY_BETWEEN_ADS_MAX", "600")) if _config else int(os.getenv("DELAY_BETWEEN_ADS_MAX", "600"))

_enable_posting = _config.get("ENABLE_REAL_POSTING", "false") if _config else os.getenv("ENABLE_REAL_POSTING", "false")
ENABLE_REAL_POSTING = _enable_posting.lower() in ('true', '1', 'yes', 'oui')

# ==================== MODE NAVIGATEUR ====================
BROWSER_MODE = _config.get("BROWSER_MODE") if _config else os.getenv("BROWSER_MODE", "minimized")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# ==================== GESTION DES CAPTCHAS ====================
CAPTCHA_MAX_WAIT = int(_config.get("CAPTCHA_MAX_WAIT", "300")) if _config else int(os.getenv("CAPTCHA_MAX_WAIT", "300"))
CAPTCHA_MODE = _config.get("CAPTCHA_MODE") if _config else os.getenv("CAPTCHA_MODE", "manual")

# ==================== NAVIGATION ====================
# URLs LeBonCoin
LOGIN_URL = "https://www.leboncoin.fr/se-connecter"
POST_AD_URL = "https://www.leboncoin.fr/deposer-une-annonce"

# Fichier de sauvegarde de session
COOKIE_FILE = "state.json"

# ==================== CONSEILS ====================
"""
STRATÉGIE ANTI-BAN RECOMMANDÉE :

1. Ne publiez JAMAIS plus de 3 annonces d'un coup
2. Espacez les sessions de publication (minimum 3-4 heures)
3. Variez les horaires de publication
4. Vérifiez manuellement après chaque session

EXEMPLE POUR 10 ANNONCES :
- Jour 1 Matin : 3 annonces
- Jour 1 Soir : 3 annonces  
- Jour 2 Matin : 3 annonces
- Jour 2 Soir : 1 annonce

DÉLAIS RECOMMANDÉS PAR NIVEAU DE PRUDENCE :
- Prudent (sûr) : 600-900 secondes (10-15 min)
- Normal (équilibré) : 300-600 secondes (5-10 min)  
- Rapide (risqué) : 180-300 secondes (3-5 min)
"""

