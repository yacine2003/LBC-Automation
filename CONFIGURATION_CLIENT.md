# ⚙️ Configuration Client - Guide Simplifié

Guide ultra-simple pour configurer vos identifiants **sans toucher au code**.

---

## 🚀 Méthode Facile (Interface Web)

### Étape 1 : Démarrer le Bot

**Windows :**
- Double-cliquez sur `Lancer_Bot.bat`

**macOS/Linux :**
```bash
python3 main.py
```

### Étape 2 : Accéder à la Configuration

1. Ouvrez votre navigateur
2. Allez sur : **http://localhost:8000**
3. Cliquez sur le bouton **"⚙️ Configuration"** en haut à droite

### Étape 3 : Remplir le Formulaire

Vous verrez un formulaire avec :

#### 🔐 Identifiants LeBonCoin
- **Email** : Votre email LeBonCoin
- **Mot de passe** : Votre mot de passe LeBonCoin

#### 📊 Google Sheets
- **Nom du Sheet** : Le nom exact de votre Google Sheet
  - Exemple : `LBC-Automation` ou `Mes Annonces`

#### 📝 Paramètres de Publication
- **Annonces par session** : Combien d'annonces publier à la fois
  - Recommandé : `3`
- **Délai minimum** : Pause minimum entre chaque annonce (en secondes)
  - Recommandé : `300` (= 5 minutes)
- **Délai maximum** : Pause maximum entre chaque annonce
  - Recommandé : `600` (= 10 minutes)
- **☑️ Activer la publication réelle** : 
  - ❌ **Décoché** = Mode TEST (recommandé au début)
  - ✅ **Coché** = Mode PRODUCTION (publications réelles)

#### 🔧 Paramètres Avancés
- **Mode navigateur** : Comment afficher le navigateur
  - `Minimisé` ✅ (recommandé)
  - `Visible` (pour debug)
  - `Headless` (risqué)
- **Temps max captcha** : Temps pour résoudre un captcha
  - Recommandé : `300` (5 minutes)

### Étape 4 : Sauvegarder

1. Cliquez sur **"💾 Enregistrer la Configuration"**
2. Vous verrez un message de confirmation ✅
3. C'est terminé !

### Étape 5 : Utiliser le Bot

1. Cliquez sur **"← Retour au tableau de bord"**
2. Cliquez sur **"▶ DÉMARRER"**
3. Le bot utilise maintenant vos identifiants !

---

## 🔒 Sécurité

### Où sont stockés vos identifiants ?

Vos identifiants sont sauvegardés dans le fichier `config.env` sur **votre machine locale**.

**⚠️ Important :**
- ✅ Ce fichier reste sur votre ordinateur
- ✅ Il n'est JAMAIS envoyé sur Internet
- ❌ Ne partagez JAMAIS ce fichier avec personne
- ❌ Ne l'uploadez jamais sur Google Drive, Dropbox, etc.

### Modifier la Configuration

Vous pouvez modifier la configuration à tout moment :

1. Retournez sur **http://localhost:8000**
2. Cliquez sur **"⚙️ Configuration"**
3. Modifiez les valeurs
4. Cliquez sur **"Enregistrer"**
5. **Redémarrez le bot** pour appliquer les changements

---

## 📋 Exemple de Configuration

### Configuration de Test (Recommandée au début)

```
Email LeBonCoin: john.doe@example.com
Mot de passe: MonMotDePasse123!
Nom du Sheet: LBC-Automation
Annonces par session: 3
Délai min: 300
Délai max: 600
☐ Activer publication réelle (DÉCOCHÉ)
Mode navigateur: Minimisé
Temps max captcha: 300
```

**Résultat :** Le bot va **simuler** les publications (mode test)

### Configuration de Production (Après Tests)

Même configuration mais :
```
☑ Activer publication réelle (COCHÉ)
```

**Résultat :** Le bot va **vraiment publier** sur LeBonCoin

---

## ❓ Questions Fréquentes

### Q: Le formulaire est vide, c'est normal ?

**R:** Oui ! La première fois, les champs sont vides. Remplissez-les avec vos informations.

### Q: Mes identifiants sont-ils visibles ?

**R:** Le mot de passe est masqué (•••••) quand vous le tapez. Il est sauvegardé de façon sécurisée sur votre machine.

### Q: Puis-je utiliser le bot sans l'interface web ?

**R:** Oui ! Vous pouvez aussi créer/éditer manuellement le fichier `config.env`. Mais l'interface est plus simple.

### Q: Que se passe-t-il si je perds ma configuration ?

**R:** Le fichier `config.env` contient tout. Faites une sauvegarde de ce fichier sur une clé USB.

### Q: Puis-je avoir plusieurs configurations ?

**R:** Oui ! Créez des copies de `config.env` :
- `config.env.compte1`
- `config.env.compte2`

Puis renommez celui que vous voulez utiliser en `config.env`.

### Q: Le formulaire ne se sauvegarde pas ?

**R:** Vérifiez que :
1. Le serveur est bien démarré
2. Vous êtes sur `localhost:8000/config-page`
3. Tous les champs obligatoires (*) sont remplis

---

## 🎯 Récapitulatif Ultra-Rapide

```
1. Lancer Lancer_Bot.bat
2. Ouvrir http://localhost:8000
3. Cliquer "⚙️ Configuration"
4. Remplir le formulaire
5. Cliquer "Enregistrer"
6. Retour → Cliquer "DÉMARRER"
```

**C'est tout ! 🎉**

---

## 💡 Conseil

**Testez toujours en mode simulation d'abord !**

1. Première utilisation → Mode TEST (case décochée)
2. Vérifiez que tout fonctionne
3. Si OK → Mode PRODUCTION (case cochée)

---

**🚀 Configuration sans code, 100% via interface web !**

