"""
Configuration du Bot LBC Automation
Modifiez ces valeurs selon vos besoins
"""

# ==================== COMPTE LEBONCOIN ====================
EMAIL = "comptleboncoin@outlook.fr"
PASSWORD = "Compte123@GED5"

# ==================== GOOGLE SHEETS ====================
SHEET_NAME = "LBC-Automation"  # Nom de votre Google Sheet

# ==================== PUBLICATION ====================
# Nombre maximum d'annonces à publier par session
# Recommandé : 3 (pour éviter les bans)
MAX_ADS_PER_RUN = 3

# Délai minimum entre chaque annonce (en secondes)
# Recommandé : 300 (5 minutes)
DELAY_BETWEEN_ADS_MIN = 300

# Délai maximum entre chaque annonce (en secondes)  
# Recommandé : 600 (10 minutes)
DELAY_BETWEEN_ADS_MAX = 600

# Activer la publication réelle (True) ou mode test (False)
# ATTENTION : En mode True, les annonces seront VRAIMENT publiées sur LeBonCoin !
ENABLE_REAL_POSTING = False

# ==================== GESTION DES CAPTCHAS ====================
# Temps maximum d'attente pour la résolution manuelle d'un captcha (en secondes)
# Recommandé : 300 (5 minutes)
CAPTCHA_MAX_WAIT = 300

# Mode de résolution des captchas
# "manual" = Résolution manuelle (le bot attend que vous résolviez)
# "auto" = Résolution automatique via service (non implémenté)
CAPTCHA_MODE = "manual"

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

