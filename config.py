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
from utils import BASE_PATH

# Fonction pour charger la config depuis config.env
def load_config():
    """Charge la configuration depuis config.env si disponible"""
    config_file = BASE_PATH / "config.env"
    
    if not config_file.exists():
        return None
    
    config = {}
    try:
        with open(str(config_file), 'r', encoding='utf-8') as f:
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

# ==================== FONCTION CHARGEMENT MULTI-COMPTES ====================
def load_accounts_from_config():
    """Charge tous les comptes depuis config.env"""
    if not _config:
        return [{"email": "votre_email@example.com", "password": "votre_mot_de_passe", "account_number": 1}]
    
    num_accounts = int(_config.get("NUM_ACCOUNTS", "1"))
    accounts = []
    
    for i in range(1, num_accounts + 1):
        email = _config.get(f"ACCOUNT_{i}_EMAIL")
        password = _config.get(f"ACCOUNT_{i}_PASSWORD")
        
        if email and password:
            accounts.append({
                "email": email,
                "password": password,
                "account_number": i
            })
    
    # Si aucun compte multi trouvé, essayer l'ancien format
    if not accounts:
        email = _config.get("LEBONCOIN_EMAIL")
        password = _config.get("LEBONCOIN_PASSWORD")
        if email and password:
            accounts.append({
                "email": email,
                "password": password,
                "account_number": 1
            })
    
    return accounts if accounts else [{"email": "votre_email@example.com", "password": "votre_mot_de_passe", "account_number": 1}]

# ==================== COMPTES LEBONCOIN (MULTI-COMPTES) ====================
ACCOUNTS = load_accounts_from_config()
NUM_ACCOUNTS = len(ACCOUNTS)

# ==================== GOOGLE SHEETS ====================
SHEET_NAME = _config.get("GOOGLE_SHEET_NAME") if _config else os.getenv("GOOGLE_SHEET_NAME", "LBC-Automation")

# ==================== DOSSIER PHOTOS ====================
# IMPORTANT : Le client DOIT configurer ce chemin via l'interface web
IMG_FOLDER = _config.get("IMG_FOLDER") if _config else os.getenv("IMG_FOLDER", "")

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

