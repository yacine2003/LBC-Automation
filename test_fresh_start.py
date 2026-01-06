"""
Script de test pour simuler une première installation
(sans cookies, nouvelle machine)
"""

import os
import shutil
from datetime import datetime

def main():
    print("=" * 80)
    print("🧪 TEST PREMIÈRE INSTALLATION - Simulation Machine Client")
    print("=" * 80)
    print()
    
    # Fichiers à sauvegarder/supprimer
    state_file = "state.json"
    backup_dir = "backup_test"
    
    # Créer un dossier de backup
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Sauvegarder state.json s'il existe
    if os.path.exists(state_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"state_backup_{timestamp}.json")
        shutil.copy(state_file, backup_path)
        print(f"✅ Sauvegarde de {state_file} vers {backup_path}")
        
        # Supprimer le fichier original
        os.remove(state_file)
        print(f"🗑️  Suppression de {state_file} (simulation nouvelle machine)")
    else:
        print(f"ℹ️  Pas de {state_file} existant (déjà en mode nouvelle machine)")
    
    print()
    print("=" * 80)
    print("📋 CONDITIONS DE TEST ACTIVÉES :")
    print("=" * 80)
    print("  ✅ Pas de cookies sauvegardés")
    print("  ✅ Pas de session active")
    print("  ⚠️  Le bot devra se connecter depuis zéro")
    print("  ⚠️  Possibilité de captcha à résoudre")
    print("  ⚠️  Bannière cookies à accepter")
    print()
    print("=" * 80)
    print("🚀 LANCEMENT DU BOT")
    print("=" * 80)
    print()
    print("Lancez maintenant : python3.10 main.py")
    print()
    print("💡 CONSEILS :")
    print("  - Surveillez le navigateur pour détecter les captchas")
    print("  - Résolvez manuellement si nécessaire")
    print("  - Le bot attendra automatiquement")
    print()
    print("🔄 Pour restaurer votre session après le test :")
    print(f"  - Copiez le fichier depuis {backup_dir}/ vers {state_file}")
    print()

if __name__ == "__main__":
    main()

