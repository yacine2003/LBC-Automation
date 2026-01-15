# 🔨 Guide de Compilation en .EXE

Ce guide explique comment compiler LBC Automation en fichier .exe pour la distribution aux clients.

---

## 📋 Prérequis

### Sur votre machine de développement :
- ✅ Python 3.10+
- ✅ Toutes les dépendances installées (`pip install -r requirements.txt`)
- ✅ PyInstaller (`pip install pyinstaller`)

---

## 🚀 Compilation Rapide

### Windows :
```batch
Double-clic sur build_exe.bat
```

### macOS/Linux :
```bash
pip install pyinstaller
pyinstaller --onefile --name "LBC_Automation" \
  --add-data "static:static" \
  --add-data "config.env.example:." \
  --hidden-import=uvicorn.lifespan.on \
  --hidden-import=uvicorn.lifespan.off \
  --hidden-import=uvicorn.protocols.websockets.auto \
  --hidden-import=uvicorn.protocols.http.auto \
  --hidden-import=uvicorn.protocols.websockets.websockets_impl \
  --hidden-import=playwright._impl._api_structures \
  --collect-all fastapi \
  --collect-all uvicorn \
  --collect-all playwright \
  launcher.py
```

---

## 📦 Résultat de la Compilation

Après la compilation, vous obtenez :

```
dist/
├── LBC_Automation.exe          # Fichier exécutable (~50-100 MB)
└── LBC_Automation_Package/     # Package complet pour le client
    ├── LBC_Automation.exe
    ├── config.env.example
    ├── README.md
    ├── GUIDE_RAPIDE.txt
    ├── img/
    │   └── README.txt
    └── requirements.txt
```

---

## 📤 Livraison au Client

### Étape 1 : Préparer le package

1. Copier le dossier `dist/LBC_Automation_Package`
2. Renommer en `LBC_Automation`
3. Ajouter `service_account.json` (à envoyer séparément par email sécurisé)

### Étape 2 : Créer un ZIP

```
LBC_Automation.zip
├── LBC_Automation.exe
├── config.env.example
├── README.md
├── GUIDE_RAPIDE.txt
├── img/
└── service_account.json (à ajouter)
```

### Étape 3 : Instructions pour le client

**Email au client :**

```
Bonjour,

Voici LBC Automation. Pour l'installer :

1. Décompressez LBC_Automation.zip
2. Double-cliquez sur LBC_Automation.exe
3. Attendez l'installation de Chromium (première fois uniquement)
4. Le navigateur s'ouvre automatiquement sur http://localhost:8000
5. Cliquez sur "⚙️ Configuration"
6. Remplissez vos identifiants LeBonCoin
7. Cliquez sur "Enregistrer"
8. C'est prêt !

Cordialement
```

---

## 🔧 Architecture de la Compilation

### Fichiers modifiés pour l'exe :

1. **`utils.py`** (nouveau)
   - Fonction `get_base_path()` pour détecter si on est en .exe ou en script
   - Retourne le bon chemin de base

2. **`main.py`**
   - Import de `BASE_PATH` depuis utils
   - Tous les chemins utilisent `BASE_PATH`

3. **`config.py`**
   - Utilise `BASE_PATH` pour `config.env`

4. **`gsheet_manager.py`**
   - Utilise `BASE_PATH` pour `service_account.json`

5. **`bot_engine.py`**
   - Utilise `BASE_PATH` pour les sessions et screenshots

6. **`launcher.py`** (nouveau)
   - Point d'entrée pour l'exe
   - Vérifie et installe Chromium au premier lancement
   - Ouvre le navigateur automatiquement
   - Lance le serveur FastAPI

---

## ⚙️ Fonctionnement en Mode .EXE

### Première exécution :

```
1. Double-clic sur LBC_Automation.exe
   └─> Détection : Chromium non installé
       └─> Installation automatique de Chromium (~200 MB)
           └─> Ouverture du navigateur sur http://localhost:8000
               └─> Interface de configuration affichée
```

### Exécutions suivantes :

```
1. Double-clic sur LBC_Automation.exe
   └─> Détection : Chromium déjà installé ✅
       └─> Ouverture immédiate du navigateur
           └─> Interface prête
```

---

## 📊 Tailles des Fichiers

| Composant | Taille | Description |
|-----------|--------|-------------|
| **LBC_Automation.exe** | ~50-100 MB | Exécutable principal |
| **Chromium** | ~200 MB | Téléchargé au premier lancement |
| **config.env** | <1 KB | Créé lors de la configuration |
| **service_account.json** | <5 KB | Fourni séparément |
| **sessions** | ~10 KB/compte | Créés automatiquement |
| **Total initial** | ~50-100 MB | ZIP à envoyer au client |
| **Total après install** | ~250-300 MB | Sur le PC du client |

---

## 🔍 Dépannage

### L'exe ne se lance pas

**Antivirus :**
- Les antivirus peuvent bloquer les .exe créés avec PyInstaller
- Solution : Ajouter une exception ou signer l'exe

**Fichiers manquants :**
```
LBC_Automation.exe : OK
static/ : NÉCESSAIRE (inclus dans l'exe via --add-data)
config.env.example : NÉCESSAIRE (inclus dans l'exe)
service_account.json : À FOURNIR SÉPARÉMENT
```

### Erreur "Chromium not found"

- Premier lancement : normal, installation en cours
- Lancements suivants : problème d'installation
  - Solution : Supprimer le dossier AppData/Local/ms-playwright
  - Relancer l'exe

### L'interface web ne s'affiche pas

- Vérifier que le port 8000 n'est pas utilisé
- Ouvrir manuellement : http://localhost:8000

---

## 🎯 Avantages de l'.EXE

✅ **Pour le client :**
- Un seul fichier à télécharger
- Pas besoin d'installer Python
- Double-clic pour lancer
- Interface professionnelle

✅ **Pour vous :**
- Distribution simplifiée
- Pas de support Python
- Moins de problèmes de dépendances
- Protection du code source

---

## ⚠️ Limitations

- ⚠️ Fichier volumineux (~50-100 MB)
- ⚠️ Chromium téléchargé séparément (~200 MB)
- ⚠️ Windows uniquement (pour build_exe.bat)
- ⚠️ Antivirus peut bloquer (faux positif)

---

## 💡 Alternative : Installeur Inno Setup

Si vous préférez un installeur professionnel au lieu d'un .exe unique :

1. Installer Inno Setup (gratuit)
2. Créer un script .iss
3. Compiler l'installeur
4. Résultat : `LBC_Automation_Setup.exe` (~30 MB)

Avantages :
- Fichier plus petit
- Installation dans Program Files
- Icône sur le bureau
- Désinstallation propre

---

## 📝 Checklist de Livraison

Avant d'envoyer au client :

- [ ] Compiler l'exe avec `build_exe.bat`
- [ ] Tester l'exe sur une machine vierge
- [ ] Préparer `service_account.json`
- [ ] Créer le ZIP final
- [ ] Rédiger l'email d'instructions
- [ ] Tester l'installation côté client

---

## 🎉 Conclusion

Le projet est maintenant **prêt pour la compilation en .exe** !

Tous les chemins sont absolus, compatibles avec PyInstaller.

**Prochaines étapes :**
1. Compiler avec `build_exe.bat` (sur Windows)
2. Tester l'exe
3. Préparer le package
4. Livrer au client

**Bonne chance ! 🚀**
