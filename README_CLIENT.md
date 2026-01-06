# 🤖 LBC Automation - Installation Client

Bot d'automatisation pour publier vos annonces sur LeBonCoin depuis Google Sheets.

---

## 🚀 Installation Rapide (10 minutes)

### Windows

1. **Extraire** le dossier ZIP
2. **Double-cliquer** sur `INSTALL_CLIENT.bat`
3. **Suivre** les instructions à l'écran
4. C'est installé ! ✅

### macOS/Linux

1. **Extraire** le dossier
2. **Ouvrir un Terminal** dans le dossier
3. **Exécuter** :
   ```bash
   pip3 install -r requirements.txt
   python3 -m playwright install chromium
   ```
4. C'est installé ! ✅

---

## ⚙️ Configuration (2 minutes)

### Via Interface Web (Le Plus Simple) ⭐

1. **Lancer le bot** :
   - Windows : Double-clic sur `Lancer_Bot.bat`
   - macOS/Linux : `python3 main.py`

2. **Ouvrir le navigateur** : http://localhost:8000

3. **Cliquer** sur "⚙️ Configuration" (en haut à droite)

4. **Remplir** le formulaire :
   - Email LeBonCoin
   - Mot de passe LeBonCoin
   - Nom de votre Google Sheet
   - Laisser les autres valeurs par défaut

5. **Cliquer** "Enregistrer"

6. **C'est terminé !** 🎉

📖 **Guide détaillé :** [CONFIGURATION_CLIENT.md](CONFIGURATION_CLIENT.md)

---

## 📊 Configurer Google Sheets

### 1. Créer le Service Account

1. Aller sur [Google Cloud Console](https://console.cloud.google.com)
2. Créer un projet : "LBC Automation"
3. Activer l'API Google Sheets
4. Créer un Service Account
5. Télécharger la clé JSON
6. Renommer en `service_account.json`
7. Placer dans le dossier du bot

### 2. Partager le Sheet

1. Ouvrir votre Google Sheet
2. Cliquer "Partager"
3. Coller l'email du service account
4. Donner les droits "Éditeur"

### 3. Structure du Sheet

| ID | Titre | Description | Prix | Categorie | Photos | Statut | Ville |
|----|-------|-------------|------|-----------|--------|--------|-------|
| 1 | Formation Excel | Description... | 50 | Cours particuliers | photo1.jpg | A_FAIRE | Paris |

---

## 🎮 Utilisation

### Premier Lancement

1. **Ajouter** vos photos dans le dossier `img/`
2. **Remplir** votre Google Sheet
3. **Lancer** le bot (Double-clic sur `Lancer_Bot.bat`)
4. **Ouvrir** http://localhost:8000
5. **Cliquer** "DÉMARRER"
6. **Observer** les logs en temps réel

### Mode TEST vs PRODUCTION

**Mode TEST** (recommandé au début) :
- Le bot simule tout sans publier réellement
- Parfait pour vérifier que tout fonctionne

**Mode PRODUCTION** :
- Le bot publie réellement sur LeBonCoin
- À activer seulement après avoir testé

**Comment changer ?**
→ Interface : http://localhost:8000/config-page → Cocher/décocher "Publication réelle"

---

## 📁 Structure des Fichiers

```
LBC-Automation/
├── Lancer_Bot.bat          ← Double-clic pour lancer
├── INSTALL_CLIENT.bat      ← Installation automatique
├── CONFIGURATION_CLIENT.md ← Guide configuration
├── README_CLIENT.md        ← Ce fichier
├── config.env              ← Vos identifiants (créé automatiquement)
├── service_account.json    ← Clés Google (à ajouter)
├── img/                    ← Vos photos ici
└── ...autres fichiers (ne pas toucher)
```

---

## 🆘 Aide

### Le bot ne démarre pas

**Solution :**
```bash
# Windows
python --version
# Doit afficher : Python 3.10 ou supérieur

# Si erreur : Réinstallez Python avec "Add to PATH"
```

### Erreur "Sheet not found"

**Solutions :**
1. Vérifier le nom exact du Sheet (sensible à la casse)
2. Vérifier que le Sheet est partagé avec le service account
3. Vérifier que `service_account.json` existe

### Erreur "Impossible de se connecter"

**Solutions :**
1. Vérifier email et mot de passe dans la configuration
2. Se connecter manuellement sur leboncoin.fr pour tester
3. Désactiver l'authentification à deux facteurs (2FA)

### Le navigateur ne se minimise pas

**Solution :**
→ Configuration → Mode navigateur → Choisir "Visible" temporairement

---

## 🔐 Sécurité

### ✅ Ce qui est sécurisé

- Identifiants stockés **localement** sur votre machine
- Fichier `config.env` **jamais partagé**
- Mot de passe **non visible** dans l'interface

### ⚠️ À ne JAMAIS faire

- ❌ Partager le fichier `config.env`
- ❌ Uploader `service_account.json` en ligne
- ❌ Donner vos identifiants LeBonCoin

---

## 📖 Documentation Complète

- **CONFIGURATION_CLIENT.md** - Guide de configuration détaillé
- **README.md** - Documentation technique complète

---

## 🎯 Checklist Avant Premier Lancement

- [ ] Python 3.10+ installé
- [ ] Dépendances installées (`INSTALL_CLIENT.bat` ou `pip install`)
- [ ] Service Account Google créé
- [ ] Fichier `service_account.json` ajouté
- [ ] Google Sheet partagé avec le service account
- [ ] Configuration remplie (http://localhost:8000/config-page)
- [ ] Photos ajoutées dans le dossier `img/`
- [ ] Google Sheet structuré correctement
- [ ] Mode TEST activé pour les premiers essais

---

## ✨ Support

En cas de problème :
1. Consultez la section "Aide" ci-dessus
2. Vérifiez les logs dans le terminal
3. Contactez le support technique

---

**🚀 Installation simple, configuration par interface web, aucune modification de code nécessaire !**

