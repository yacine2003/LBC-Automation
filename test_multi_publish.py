"""
Script de test pour vérifier la logique de publication multiple
Lance le bot en mode simulation pour tester le workflow
"""

import sys
from config import MAX_ADS_PER_RUN, ENABLE_REAL_POSTING, SHEET_NAME

def main():
    print("=" * 80)
    print("🧪 TEST DE CONFIGURATION - Publication Multiple")
    print("=" * 80)
    print()
    
    print(f"📊 Google Sheet      : {SHEET_NAME}")
    print(f"📝 Annonces par run  : {MAX_ADS_PER_RUN}")
    print(f"🚀 Mode publication  : {'RÉEL ⚠️' if ENABLE_REAL_POSTING else 'SIMULATION ✅'}")
    print()
    
    if ENABLE_REAL_POSTING:
        print("⚠️  ATTENTION : Le mode PUBLICATION RÉELLE est activé !")
        print("⚠️  Les annonces seront VRAIMENT publiées sur LeBonCoin.")
        print()
        response = input("Continuer ? (tapez 'OUI' pour confirmer) : ")
        if response.upper() != "OUI":
            print("❌ Test annulé.")
            sys.exit(0)
    else:
        print("✅ Mode SIMULATION activé - Aucune vraie publication")
        print()
    
    print("=" * 80)
    print("Prêt à lancer le bot ! Utilisez :")
    print("  python3.10 main.py")
    print("=" * 80)

if __name__ == "__main__":
    main()

