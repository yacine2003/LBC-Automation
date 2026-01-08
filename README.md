# 🤖 LBC Automation - Publication Automatique d'Annonces

Bot d'automatisation pour publier vos annonces sur LeBonCoin depuis Google Sheets avec interface web de contrôle.

## ✨ Fonctionnalités

- ✅ **Publication automatique** depuis Google Sheets
- ✅ **Publication multiple** : Plusieurs annonces en une session (configurable)
- ✅ **Anti-ban intelligent** : Délais aléatoires, frappe humaine, stealth mode
- ✅ **Reprise automatique** : Le bot reprend là où il s'est arrêté
- ✅ **Interface Web** : Contrôle visuel avec logs en temps réel
- ✅ **Gestion des captchas** : Détection automatique avec alertes visuelles/sonores
- ✅ **Mode TEST/PRODUCTION** : Testez avant de vraiment publier
- ✅ **Configuration web** : Interface pour paramétrer le bot sans toucher au code
- ✅ **Multi-plateforme** : Windows, macOS, Linux

## 📋 Prérequis

- Python 3.10+
- Compte Google avec accès à Google Sheets API
- Compte LeBonCoin valide

## 🚀 Installation Rapide

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd Automatisation
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Configurer Google Sheets API

1. Créez un projet sur [Google Cloud Console](https://console.cloud.google.com)
2. Activez l'API Google Sheets
3. Créez un Service Account et téléchargez le fichier JSON
4. Renommez-le `service_account.json` et placez-le dans le projet
5. Partagez votre Google Sheet avec l'email du Service Account

### 4. Configurer le bot

```bash
# Lancer le serveur
python main.py

# Ouvrir l'interface de configuration
# http://localhost:8000/config-page

# Remplir le formulaire :
# - Email LeBonCoin
# - Mot de passe LeBonCoin
# - Nom du Google Sheet
# - Dossier des photos (chemin absolu)
# - Autres paramètres (délais, mode navigateur, etc.)
```

## 📊 Structure Google Sheets

Votre feuille doit contenir ces colonnes :

| ID | Titre | Description | Prix | Categorie | Photos | Status | Type | Ville |
|----|-------|-------------|------|-----------|--------|--------|------|-------|
| 1 | Formation Excel | Description... | 15 | Cours particuliers | photo1.jpg | A_FAIRE | Informatique | Paris |

- **Status** : `A_FAIRE` (à publier) ou `FAIT` (déjà publié)
- **Photos** : Noms des fichiers séparés par des virgules

## 🎮 Utilisation

### Démarrage

1. **Lancer le serveur**
   ```bash
   python main.py
   ```

2. **Ouvrir l'interface**
   ```
   http://localhost:8000
   ```

3. **Démarrer la publication**
   - Cliquer sur "🚀 Démarrer la Publication"
   - Surveiller les logs en temps réel
   - Utiliser "⏹ Arrêter" si nécessaire

### Windows : Lancement Rapide

Double-cliquez sur `Lancer_Bot.bat` pour démarrer automatiquement le serveur.

## ⚙️ Configuration

### Via l'Interface Web (Recommandé)

1. Ouvrir `http://localhost:8000/config-page`
2. Remplir tous les champs
3. Enregistrer

### Paramètres Importants

- **Dossier photos** : Chemin absolu vers vos images (ex: `C:/Photos/LBC` ou `/Users/nom/Photos`)
- **Délais entre annonces** : 
  - Tests : 60-120 secondes (1-2 min)
  - Production : 300-600 secondes (5-10 min)
- **Mode navigateur** :
  - `minimized` : Recommandé (fenêtre minimisée mais accessible)
  - `visible` : Debug/test (fenêtre normale)
  - `headless` : Invisible (risque de détection élevé)
- **Publication réelle** : Activer uniquement quand vous êtes prêt !

## 🛡️ Sécurité & Anti-Ban

Le bot intègre plusieurs protections :
- ✅ Playwright Stealth (masque l'automatisation)
- ✅ User-Agent réaliste
- ✅ Frappe au clavier avec délais variables
- ✅ Pauses aléatoires entre actions
- ✅ Délais importants entre publications
- ✅ Gestion automatique des captchas

**⚠️ Recommandations :**
- Ne publiez jamais plus de 5 annonces par session
- Espacez les sessions de 3-4 heures minimum
- Utilisez des délais de 5-10 minutes entre annonces en production
- Surveillez votre compte LBC régulièrement

## 🔐 Gestion des Captchas

Le bot détecte et gère automatiquement les captchas :

1. **Détection automatique** à chaque étape clé
2. **Alerte visuelle et sonore** sur l'interface web
3. **Pause automatique** : vous avez 5 minutes pour résoudre
4. **Reprise automatique** après résolution

## 📁 Structure du Projet

```
Automatisation/
├── bot_engine.py              # Moteur d'automatisation Playwright
├── main.py                    # Serveur API FastAPI
├── config.py                  # Configuration centralisée
├── config_loader.py           # Chargement config.env
├── gsheet_manager.py          # Gestion Google Sheets
├── captcha_handler.py         # Gestion des captchas
├── config.env.example         # Template de configuration
├── requirements.txt           # Dépendances Python
├── .gitignore                 # Fichiers à ignorer (déjà configuré)
├── static/
│   ├── index.html            # Interface web principale
│   ├── config.html           # Interface de configuration
│   └── app.js                # WebSocket client
├── img/
│   └── .gitkeep              # Dossier des photos (vide par défaut)
├── Lancer_Bot.bat            # Script de lancement Windows
├── INSTALL_CLIENT.bat        # Script d'installation Windows
├── README_CLIENT.md          # Guide simplifié pour le client
├── CONFIGURATION_CLIENT.md   # Guide de configuration détaillé
└── GESTION_PHOTOS.md         # Guide gestion des photos

⚠️ Fichiers NON versionnés (dans .gitignore) :
├── config.env                # Configuration personnelle
├── service_account.json      # Clés API Google
├── state.json                # Session/cookies sauvegardés
└── img/*                     # Vos photos
```

## 🔧 Dépannage

### Le bot ne démarre pas
```bash
# Vérifier l'installation
pip install -r requirements.txt
python -m playwright install chromium
```

### Erreur "IMG_FOLDER non configuré"
- Ouvrir `http://localhost:8000/config-page`
- Remplir le champ "Dossier des photos" avec un chemin absolu
- Exemple : `C:/Photos/LBC` (Windows) ou `/Users/nom/Photos` (Mac)

### Le bot ne trouve pas d'annonces
- Vérifier que des lignes ont `Status = A_FAIRE` dans le Google Sheet
- Vérifier le nom du Sheet dans la configuration

### Erreur "Sheet not found"
- Vérifier que vous avez partagé le Sheet avec le Service Account
- Vérifier le fichier `service_account.json`

### Erreur de connexion LBC
- Vérifier EMAIL et PASSWORD dans la configuration
- Supprimer `state.json` et réessayer

## 📖 Documentation Complète

- **[README_CLIENT.md](README_CLIENT.md)** : Guide simplifié pour l'utilisateur final
- **[CONFIGURATION_CLIENT.md](CONFIGURATION_CLIENT.md)** : Configuration détaillée
- **[GESTION_PHOTOS.md](GESTION_PHOTOS.md)** : Organisation des photos

## 🪟 Déploiement Client

### Installation Automatique (Windows)

1. Lancer `INSTALL_CLIENT.bat`
2. Le script installe tout automatiquement
3. Configurer via l'interface web
4. Lancer avec `Lancer_Bot.bat`

### Installation Manuelle

Voir `README_CLIENT.md` pour les instructions complètes.

## 📝 Logs

Le bot affiche des logs détaillés dans l'interface web et dans le terminal :

```
================================================================================
>>> DÉMARRAGE SESSION - Limite: 3 annonces par session
================================================================================
✅ Dossier photos configuré : /Users/nom/Photos

>>> ANNONCE 1/3
>>> Annonce trouvée : Formation Excel (ligne 2)
[Form] Remplissage Titre...
[Form] Gestion Photos...
[Final] Recherche bouton pour validation finale...
>>> 🚀 PUBLICATION RÉELLE - Clic sur 'Continuer'...
>>> ✅ Clic effectué ! Attente de confirmation...
✅ Annonce publiée avec succès ! (1/3)

⏳ Pause de 7.3 minutes avant la prochaine annonce...
```

## ⚖️ Mentions Légales

Ce bot est fourni à titre éducatif. L'utilisateur est responsable de son usage et doit respecter les Conditions Générales d'Utilisation de LeBonCoin.

---

**🚀 Développé avec ❤️ | Bonne publication !**
