# 🤖 LBC Automation - Publication Automatique d'Annonces

Bot d'automatisation pour publier vos annonces sur LeBonCoin depuis Google Sheets.

## ✨ Fonctionnalités

- ✅ **Publication automatique** depuis Google Sheets
- ✅ **Publication multiple** : Publiez plusieurs annonces en une session (3 par défaut)
- ✅ **Anti-ban intelligent** : Délais aléatoires entre publications (5-10 min)
- ✅ **Reprise automatique** : Le bot reprend là où il s'est arrêté
- ✅ **Marquage automatique** : Statut "FAIT" après chaque publication
- ✅ **Interface Web** : Contrôle visuel via navigateur
- ✅ **Mode TEST/PRODUCTION** : Testez avant de vraiment publier
- ✅ **Arrêt gracieux** : Arrêt propre à tout moment
- ✅ **Simulation humaine** : Frappe lente, pauses aléatoires, stealth mode

## 📋 Prérequis

- Python 3.10+
- Compte Google avec accès à Google Sheets API
- Compte LeBonCoin valide

## 🚀 Installation

1. **Cloner/télécharger le projet**
   ```bash
   cd /Users/yacine/Automatisation
   ```

2. **Installer les dépendances**
   ```bash
   pip3.10 install fastapi uvicorn playwright gspread oauth2client playwright-stealth
   python3.10 -m playwright install chromium
   ```

3. **Configurer Google Sheets API**
   - Créez un projet sur [Google Cloud Console](https://console.cloud.google.com)
   - Activez l'API Google Sheets
   - Créez un Service Account et téléchargez le fichier JSON
   - Renommez-le `service_account.json` et placez-le dans le projet
   - Partagez votre Google Sheet avec l'email du Service Account

4. **Configurer le bot**
   - Éditez `config.py` avec vos informations :
     ```python
     EMAIL = "votre_email@example.com"
     PASSWORD = "votre_mot_de_passe"
     SHEET_NAME = "Nom-de-votre-Sheet"
     ```

## 📊 Structure Google Sheets

Votre feuille doit contenir ces colonnes :

| ID | Titre | Description | Prix | Categorie | Photos | Statut | Type | Ville |
|----|-------|-------------|------|-----------|--------|--------|------|-------|
| 1 | Formation Resell | Description... | 15 | Cours particuliers | IMG_1423.jpg | A_FAIRE | Informatique | Strasbourg |

- **Statut** : `A_FAIRE` (à publier) ou `FAIT` (déjà publié)
- **Photos** : Placez vos images dans le dossier `img/`

## 🎮 Utilisation

### Démarrage Rapide

1. **Tester la configuration**
   ```bash
   python3.10 test_multi_publish.py
   ```

2. **Lancer le serveur**
   ```bash
   python3.10 main.py
   ```

3. **Ouvrir l'interface web**
   ```
   http://localhost:8000
   ```

4. **Cliquer sur "DÉMARRER"**
   - Le bot publiera jusqu'à 3 annonces
   - Il attendra 5-10 minutes entre chaque
   - Il s'arrêtera automatiquement

### Mode TEST vs PRODUCTION

**Mode TEST** (par défaut) :
- Remplit tous les formulaires
- NE publie PAS vraiment
- Marque quand même comme "FAIT"
- Parfait pour vérifier le fonctionnement

**Mode PRODUCTION** :
1. Dans `config.py`, changez :
   ```python
   ENABLE_REAL_POSTING = True
   ```
2. Relancez le bot

## ⚙️ Configuration

Éditez `config.py` pour ajuster :

```python
# === PUBLICATION ===
MAX_ADS_PER_RUN = 3              # Annonces par session (recommandé : 3)
DELAY_BETWEEN_ADS_MIN = 300      # Délai min entre annonces (5 min)
DELAY_BETWEEN_ADS_MAX = 600      # Délai max entre annonces (10 min)
ENABLE_REAL_POSTING = False      # True = publication réelle

# === NAVIGATEUR ===
BROWSER_MODE = "minimized"       # "visible", "minimized" ou "headless" 🆕
USER_AGENT = "Mozilla/5.0..."    # User-Agent Windows (déjà configuré)
```

### 🖥️ Modes d'Affichage du Navigateur

#### Mode Minimisé (Recommandé pour production)
```python
BROWSER_MODE = "minimized"
```
- ✅ Fenêtre dans la barre des tâches Windows (ou Dock macOS)
- ✅ Moins détectable que le mode headless
- ✅ Accessible pour résoudre les captchas
- ✅ N'interfère pas avec votre travail
- 🎯 **PARFAIT POUR LA PRODUCTION CLIENT**

#### Mode Visible (Pour debug/test)
```python
BROWSER_MODE = "visible"
```
- 👁️ Fenêtre normale visible à l'écran
- ✅ Idéal pour débugger ou voir ce qui se passe
- ⚠️ Peut être intrusif pendant le travail

#### Mode Headless (Non recommandé)
```python
BROWSER_MODE = "headless"
```
- 👻 Complètement invisible (pas de fenêtre)
- ⚠️ **RISQUE ÉLEVÉ** de détection par LeBonCoin
- ❌ Impossible de résoudre les captchas manuellement
- ❌ Difficile à débugger
- ⚠️ À éviter en production

## 📖 Guide Complet

Consultez [GUIDE_PUBLICATION.md](GUIDE_PUBLICATION.md) pour :
- Stratégies anti-ban détaillées
- Exemples de sessions
- Dépannage
- Conseils de sécurité

## 🛡️ Sécurité & Anti-Ban

Le bot intègre plusieurs protections :
- ✅ Playwright Stealth (masquage de l'automatisation)
- ✅ User-Agent réaliste
- ✅ Frappe au clavier avec délais variables
- ✅ Pauses aléatoires entre actions
- ✅ Délais importants entre publications
- ✅ Limitation du nombre d'annonces par session
- ✅ **Gestion automatique des captchas** 🆕

**⚠️ Recommandations :**
- Ne publiez jamais plus de 3 annonces d'affilée
- Espacez les sessions de 3-4 heures minimum
- Variez les horaires de publication
- Surveillez votre compte LBC régulièrement

## 🪟 Déploiement sur Windows

Le bot est optimisé pour Windows ! Pour un déploiement client :

### Option 1 : Lancement par double-clic
1. Double-cliquez sur `Lancer_Bot.bat`
2. Le serveur démarre automatiquement
3. Ouvrez votre navigateur sur `http://localhost:8000`

### Option 2 : Ligne de commande
```cmd
cd C:\Users\VotreNom\Documents\Automatisation
python main.py
```

### Configuration pour Windows
Le bot est pré-configuré avec :
- ✅ User-Agent Windows natif
- ✅ Mode navigateur minimisé par défaut
- ✅ Tous les paramètres anti-ban

📖 **Guide complet** : Consultez [DEPLOIEMENT_WINDOWS.md](DEPLOIEMENT_WINDOWS.md)

## 🔐 Gestion des Captchas

Le bot détecte et gère automatiquement les captchas :

### Types supportés
- reCAPTCHA (Google)
- hCaptcha
- DataDome
- Cloudflare Turnstile
- FunCaptcha

### Fonctionnement
1. **Détection automatique** à 3 moments clés :
   - Après la connexion
   - Sur la page de dépôt
   - Avant la validation finale

2. **Pause automatique** si captcha détecté
   - Le navigateur reste ouvert
   - Vous avez 5 minutes pour résoudre
   - Le bot reprend automatiquement après résolution

3. **Configuration** dans `config.py` :
```python
CAPTCHA_MAX_WAIT = 300  # Temps d'attente max (5 min)
CAPTCHA_MODE = "manual" # Mode de résolution
```

### Test sans cookies
Pour tester dans les conditions du client (sans session) :
```bash
python3.10 test_fresh_start.py
```

Consultez [GUIDE_TEST_CAPTCHA.md](GUIDE_TEST_CAPTCHA.md) pour plus de détails.

## 📁 Structure du Projet

```
Automatisation/
├── bot_engine.py              # Moteur d'automatisation Playwright
├── main.py                    # Serveur API FastAPI
├── config.py                  # Configuration centralisée ⚙️
├── gsheet_manager.py          # Gestion Google Sheets
├── captcha_handler.py         # Gestion automatique des captchas 🆕
├── state.json                 # Session sauvegardée
├── service_account.json       # Clés API Google (à créer)
├── static/
│   ├── index.html            # Interface web
│   └── app.js                # WebSocket client
├── img/                      # Dossier des photos
├── backup_test/              # Sauvegardes pour tests
├── README.md                 # Ce fichier
├── DEPLOIEMENT_WINDOWS.md    # Guide complet Windows 🆕
├── test_multi_publish.py     # Script de test
├── test_fresh_start.py       # Test première installation 🆕
├── test_browser_modes.py     # Test des modes navigateur 🆕
├── check_sheet_columns.py    # Diagnostic Google Sheet
└── Lancer_Bot.bat            # Lancement rapide Windows 🆕
```

## 🔧 Dépannage

### Le bot ne trouve pas d'annonces
- Vérifiez que des lignes ont `Statut = A_FAIRE`
- Vérifiez le nom du Sheet dans `config.py`

### Erreur "Sheet not found"
- Vérifiez que vous avez partagé le Sheet avec le Service Account
- Vérifiez le fichier `service_account.json`

### Le navigateur ne se lance pas
```bash
python3.10 -m playwright install chromium
```

### Erreur de connexion LBC
- Vérifiez EMAIL et PASSWORD dans `config.py`
- Supprimez `state.json` et réessayez

## 📝 Logs

Le bot affiche des logs détaillés :
```
================================================================================
>>> DÉMARRAGE SESSION - Limite: 3 annonces par session
================================================================================

>>> ANNONCE 1/3
>>> Annonce trouvée : Formation Resell (ligne 2)
[Form] Remplissage Titre...
[Form] Gestion Catégorie...
✅ Annonce publiée avec succès ! (1/3)

⏳ Pause de 7.3 minutes avant la prochaine annonce...
```

## 🤝 Support

Pour toute question, consultez :
- [GUIDE_PUBLICATION.md](GUIDE_PUBLICATION.md) - Guide détaillé
- Les commentaires dans le code
- Les logs d'exécution

## ⚖️ Mentions Légales

Ce bot est fourni à titre éducatif. L'utilisateur est responsable de son usage et doit respecter les Conditions Générales d'Utilisation de LeBonCoin.

---

**🚀 Bonne publication !**

