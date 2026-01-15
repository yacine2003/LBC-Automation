# 📦 Instructions d'Installation et d'Utilisation

## 📁 Fichiers fournis

Vous avez reçu **2 fichiers** à placer dans le même dossier :

1. **LBC_Automation.exe** - Le programme principal
2. **service_account.json** - Fichier d'authentification Google Sheets

---

## ✅ Préparation de votre côté

### 1️⃣ Créer votre Google Sheet

Créez un Google Sheet avec ces colonnes (dans cet ordre) :

| ID | Titre | Description | Prix | Catégorie | Photos | Statut | Type | Ville |
|----|-------|-------------|------|-----------|--------|--------|------|-------|

**Exemple de données :**
```
Titre: "iPhone 13 Pro Max"
Description: "iPhone en excellent état..."
Prix: 750
Catégorie: "Téléphonie"
Photos: "iphone1.jpg,iphone2.jpg"
Statut: "A_FAIRE"
Type: "particulier"
Ville: "Paris"
```

⚠️ **Important :**
- La colonne **"Statut"** doit contenir **"A_FAIRE"** pour les annonces à publier
- Après publication, le bot mettra automatiquement le statut à **"FAIT"**
- Les noms de photos doivent correspondre aux fichiers dans votre dossier

---

### 2️⃣ Partager votre Google Sheet

1. Ouvrez votre Google Sheet
2. Cliquez sur le bouton **"Partager"** (en haut à droite)
3. Dans le champ "Ajouter des personnes ou des groupes", entrez :
   ```
   lbc-automation@lbc-automation-483321.iam.gserviceaccount.com
   ```
4. Donnez-lui les droits **"Éditeur"**
5. Cliquez sur **"Envoyer"**

✅ C'est fait ! Le bot peut maintenant accéder à votre Google Sheet.

---

### 3️⃣ Préparer vos photos

1. Créez un dossier sur votre ordinateur (ex: `C:/Photos/LBC`)
2. Placez-y toutes les photos de vos annonces
3. ⚠️ **Important :** Les noms des fichiers doivent correspondre exactement aux noms indiqués dans la colonne "Photos" de votre Google Sheet

**Exemple :**
- Google Sheet indique : `"iphone1.jpg,iphone2.jpg"`
- Votre dossier doit contenir : `iphone1.jpg` et `iphone2.jpg`

---

## 🚀 Utilisation du Bot

### 1️⃣ Lancer le programme

1. Placez les 2 fichiers (`LBC_Automation.exe` + `service_account.json`) dans le **même dossier**
2. Double-cliquez sur **`LBC_Automation.exe`**
3. Une fenêtre de navigateur s'ouvrira automatiquement sur `http://localhost:8000`

---

### 2️⃣ Configuration initiale

1. Cliquez sur **"⚙️ Configuration"** dans le menu
2. Remplissez le formulaire :

   **Comptes Leboncoin :**
   - Indiquez le **nombre de comptes** Leboncoin que vous souhaitez utiliser
   - Pour chaque compte, entrez :
     - **Email Leboncoin**
     - **Mot de passe Leboncoin**

   **Google Sheets :**
   - **Nom du Google Sheet** : Le nom exact de votre feuille (celui que vous voyez dans Google Sheets)

   **Photos :**
   - **Chemin du dossier photos** : Le chemin absolu vers votre dossier (ex: `C:/Photos/LBC`)
     - ⚠️ Utilisez des `/` (slash) et non des `\` (antislash)
     - Le chemin doit être **absolu** (commence par `C:/` ou `D:/`)

   **Paramètres :**
   - **Nombre d'annonces par session** : Recommandé 3 (pour éviter la détection)

3. Cliquez sur **"💾 Enregistrer la Configuration"**

---

### 3️⃣ Lancer la publication

1. Retournez sur la page principale
2. Cliquez sur le bouton **"▶️ Démarrer"**
3. Le bot va :
   - ✅ Se connecter à votre Google Sheet
   - ✅ Récupérer les annonces avec statut "A_FAIRE"
   - ✅ Se connecter à Leboncoin
   - ✅ Publier les annonces une par une
   - ✅ Mettre à jour le statut à "FAIT" après chaque publication

📊 Vous pouvez suivre la progression en temps réel sur l'interface web.

---

## 🛑 Arrêter le bot

Pour arrêter le bot à tout moment :
- Cliquez sur le bouton **"⏹️ Arrêter"** sur l'interface web

---

## ⚠️ Conseils de sécurité

Pour éviter d'être détecté comme un bot :

1. ✅ Ne publiez **pas plus de 3 annonces par session**
2. ✅ Espacez vos sessions de publication (minimum 3-4 heures entre chaque)
3. ✅ Variez les horaires de publication
4. ✅ Vérifiez manuellement après chaque session

---

## ❓ En cas de problème

**Le bot s'arrête après la première annonce ?**
- Vérifiez que votre Google Sheet est bien partagé avec le Service Account
- Vérifiez que les noms de photos correspondent exactement

**Erreur de connexion Google Sheets ?**
- Vérifiez que `service_account.json` est dans le même dossier que `LBC_Automation.exe`
- Vérifiez que votre Google Sheet est bien partagé

**Le bot ne trouve pas les photos ?**
- Vérifiez que le chemin est **absolu** (commence par `C:/` ou `D:/`)
- Vérifiez que les noms de fichiers correspondent exactement

---

## 📞 Support

Pour toute question, contactez votre développeur.
