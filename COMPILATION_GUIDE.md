# 🏗️ Guide de Compilation Windows

Ce guide vous explique comment transformer le projet Python en un fichier `.exe` autonome pour Windows.

## 1. Prérequis sur Windows

Assurez-vous d'avoir installé **Python 3.10 ou plus récent** sur votre machine Windows.
Lors de l'installation de Python, cochez bien la case **"Add Python to PATH"**.

## 2. Préparation

1. Copiez tout le dossier du projet sur votre machine Windows.
2. Ouvrez un terminal (PowerShell ou Invite de commandes) dans le dossier du projet.

## 3. Installation des dépendances

Avant de compiler, il faut installer les librairies nécessaires sur votre machine Windows.
Exécutez cette commande :

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

## 4. Compilation

J'ai préparé un script automatique pour générer l'exécutable. Lancez simplement :

```powershell
python build_windows.py
```

Le script va :
1. Nettoyer les anciens builds.
2. Configurer PyInstaller pour cacher la console (`--noconsole`).
3. Inclure le dossier `static` (l'interface web) dans l'exécutable.
4. Générer un fichier unique `.exe`.

## 5. Résultat

Une fois terminé, vous trouverez votre logiciel ici :
📂 **`dist/LBC_Automation_Bot.exe`**

Vous pouvez déplacer ce fichier `.exe` n'importe où (sur le bureau du client, clé USB, etc.).

## ⚠️ Notes Importantes pour le Client

- **Premier Lancement** : Le logiciel utilise un navigateur automatisé (Chromium). Si c'est la première fois qu'il est lancé sur une machine, il peut prendre quelques secondes pour s'initialiser.
- **Dossier Photo** : Le client doit toujours configurer le dossier des photos via l'interface.
- **Console Cachée** : Comme la console est cachée, si le logiciel ne démarre pas, vérifiez le fichier `app.log` qui sera créé à côté de l'exécutable.
