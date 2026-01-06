#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test des différents modes de navigateur
Permet de vérifier que chaque mode fonctionne correctement
"""

from playwright.sync_api import sync_playwright
import time

def test_mode(mode: str):
    """Teste un mode de navigateur spécifique"""
    print("\n" + "=" * 80)
    print(f"🧪 TEST DU MODE : {mode.upper()}")
    print("=" * 80)
    
    with sync_playwright() as p:
        # Configuration commune
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox"
        ]
        
        # Lancement selon le mode
        if mode == "headless":
            print("   ⚠️  Mode headless : invisible (risqué)")
            browser = p.chromium.launch(
                headless=True,
                args=launch_args + ["--headless=new"]
            )
        elif mode == "minimized":
            print("   ✅ Mode super-minimisé : fenêtre quasi invisible")
            browser = p.chromium.launch(
                headless=False,
                args=launch_args + [
                    "--start-minimized",
                    "--window-position=-5000,-5000",
                    "--window-size=400,300",
                    "--mute-audio",
                    "--disable-notifications",
                    "--disable-infobars",
                    "--no-first-run",
                    "--no-default-browser-check"
                ]
            )
        else:  # visible
            print("   👁️  Mode visible : fenêtre normale")
            browser = p.chromium.launch(
                headless=False,
                args=launch_args
            )
        
        # Configuration du contexte
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="fr-FR"
        )
        
        page = context.new_page()
        
        # Test simple
        print("   🌐 Navigation vers LeBonCoin...")
        page.goto("https://www.leboncoin.fr", timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        
        title = page.title()
        print(f"   ✅ Page chargée : {title}")
        
        # Screenshot pour vérification
        screenshot_name = f"test_{mode}_mode.png"
        page.screenshot(path=screenshot_name)
        print(f"   📸 Screenshot sauvegardé : {screenshot_name}")
        
        # Attente pour observer
        print(f"   ⏱️  Observation pendant 5 secondes...")
        time.sleep(5)
        
        # Fermeture
        browser.close()
        print(f"   ✅ Test du mode '{mode}' terminé avec succès")

def main():
    print("\n" + "=" * 80)
    print("🎭 TEST DES MODES DE NAVIGATEUR")
    print("=" * 80)
    print("\nCe script va tester les 3 modes de navigateur disponibles :")
    print("  1. Visible   : Fenêtre normale (pour debug)")
    print("  2. Minimisé  : Fenêtre en arrière-plan (pour production)")
    print("  3. Headless  : Invisible (risqué, non recommandé)")
    print("\n" + "=" * 80)
    
    modes = ["visible", "minimized", "headless"]
    
    for mode in modes:
        try:
            test_mode(mode)
            print(f"\n✅ Mode '{mode}' : OK")
        except Exception as e:
            print(f"\n❌ Mode '{mode}' : ERREUR")
            print(f"   Détails : {e}")
        
        # Pause entre les tests
        if mode != modes[-1]:
            print("\n⏳ Pause de 3 secondes avant le prochain test...")
            time.sleep(3)
    
    # Résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80)
    print("\n✅ Tests terminés !")
    print("\n💡 Vérifiez les screenshots générés :")
    print("   - test_visible_mode.png")
    print("   - test_minimized_mode.png")
    print("   - test_headless_mode.png")
    print("\n📝 RECOMMANDATION :")
    print("   Pour la production, utilisez : BROWSER_MODE = \"minimized\"")
    print("   - Plus discret que 'visible'")
    print("   - Moins risqué que 'headless'")
    print("   - Permet de résoudre les captchas manuellement")
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()

