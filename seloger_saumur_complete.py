#!/usr/bin/env python3
"""
Script complet SeLoger : Gestion bannière cookies + Recherche Saumur + Récupération annonces
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import json
import argparse
from datetime import datetime

# Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("⚠️  Supabase non installé. Utilisez: pip install supabase")
    SUPABASE_AVAILABLE = False

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SupabaseManager:
    """Gestionnaire pour les interactions avec Supabase"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase = None
        self.current_campaign_id = None
        
        if supabase_url and supabase_key and SUPABASE_AVAILABLE:
            self.setup_supabase()
    
    def setup_supabase(self):
        """Configure la connexion Supabase"""
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Connexion Supabase établie")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion Supabase: {e}")
            return False
    
    def create_search_campaign(self, search_config: dict, search_url: str):
        """Crée une nouvelle campagne de scraping dans Supabase"""
        if not self.supabase:
            return None
        
        try:
            # Obtenir l'ID de la source SeLoger
            source_result = self.supabase.table('sources').select('id').eq('name', 'seloger').execute()
            
            if not source_result.data:
                logger.error("❌ Source SeLoger non trouvée dans la base")
                return None
            
            source_id = source_result.data[0]['id']
            
            # Créer la campagne
            campaign_data = {
                'source_id': source_id,
                'search_config': search_config,
                'search_url': search_url,
                'status': 'running',
                'started_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('search_campaigns').insert(campaign_data).execute()
            
            if result.data:
                self.current_campaign_id = result.data[0]['id']
                logger.info(f"✅ Campagne Supabase créée: {self.current_campaign_id}")
                return self.current_campaign_id
            else:
                logger.error("❌ Erreur création campagne")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur création campagne: {e}")
            return None
    
    def send_listings_to_supabase(self, listings: list):
        """Envoie les annonces vers Supabase (ID + URL uniquement)"""
        if not self.supabase or not self.current_campaign_id:
            return False
        
        try:
            # Obtenir l'ID de la source SeLoger
            source_result = self.supabase.table('sources').select('id').eq('name', 'seloger').execute()
            source_id = source_result.data[0]['id'] if source_result.data else None
            
            if not source_id:
                logger.error("❌ Source SeLoger non trouvée")
                return False
            
            success_count = 0
            
            for listing in listings:
                try:
                    # Préparer les données minimales pour la table listings
                    listing_data = {
                        'campaign_id': self.current_campaign_id,
                        'source_id': source_id,
                        'listing_id': listing.get('id', ''),
                        'url': listing.get('url', ''),
                        'scraped_at': datetime.now().isoformat(),
                        'needs_detail_scraping': True
                    }
                    
                    # Insérer dans la table listings
                    result = self.supabase.table('listings').insert(listing_data).execute()
                    
                    if result.data:
                        logger.info(f"   ✅ Annonce sauvée: ID {listing.get('id', 'N/A')}")
                        success_count += 1
                    else:
                        logger.error(f"   ❌ Erreur sauvegarde: ID {listing.get('id', 'N/A')}")
                        
                except Exception as e:
                    logger.error(f"   ❌ Erreur annonce: {e}")
                    continue
            
            logger.info(f"📊 {success_count}/{len(listings)} annonces sauvegardées dans Supabase")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi vers Supabase: {e}")
            return False
    
    def update_campaign_status(self, status: str, total_pages: int = 0, total_listings: int = 0):
        """Met à jour le statut de la campagne"""
        if not self.supabase or not self.current_campaign_id:
            return False
        
        try:
            update_data = {
                'status': status,
                'total_pages': total_pages,
                'total_listings_found': total_listings
            }
            
            if status == 'completed':
                update_data['completed_at'] = datetime.now().isoformat()
            
            self.supabase.table('search_campaigns').update(update_data).eq('id', self.current_campaign_id).execute()
            logger.info(f"✅ Campagne mise à jour: {status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour campagne: {e}")
            return False

def setup_driver(headless: bool = True):
    """Configure et retourne le driver Chrome avec les bonnes options"""
    try:
        options = Options()
        
        if headless:
            options.add_argument("--headless")
            logger.info("🔇 Mode invisible activé")
        else:
            options.add_argument("--start-maximized")
            logger.info("👁️ Mode visible activé")
            
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Utiliser undetected-chromedriver
        driver = uc.Chrome(options=options, version_main=None)
        
        # Masquer les indicateurs d'automatisation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        logger.error(f"Erreur lors de la configuration du driver: {e}")
        return None

def load_cookies(driver, cookie_file):
    """Charge les cookies depuis un fichier (version simplifiée)"""
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cookies_loaded = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('\t')
                if len(parts) >= 7:
                    try:
                        # Vérifier que le domaine correspond
                        domain = parts[0]
                        if 'seloger.com' in domain:
                            cookie = {
                                'name': parts[5],
                                'value': parts[6],
                                'domain': domain if domain.startswith('.') else f'.{domain}',
                                'path': parts[2] if parts[2] else '/',
                                'secure': parts[3].lower() == 'true'
                            }
                            driver.add_cookie(cookie)
                            cookies_loaded += 1
                    except Exception as e:
                        logger.warning(f"Cookie ignoré: {e}")
        
        logger.info(f"✅ {cookies_loaded} cookies chargés avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors du chargement des cookies: {e}")
        return False

def handle_cookie_banner(driver):
    """Gère la bannière de cookies Usercentrics"""
    logger.info("🍪 Gestion de la bannière de cookies...")
    
    try:
        # Attendre que la page soit chargée (réduit de 3 à 1 seconde)
        time.sleep(1)
        
        # Script pour cliquer sur "Tout accepter" dans le Shadow DOM
        script = """
        var host = document.querySelector('#usercentrics-root');
        if (host && host.shadowRoot) {
            var button = host.shadowRoot.querySelector('[data-testid="uc-accept-all-button"]');
            if (button) {
                button.click();
                return true;
            }
        }
        return false;
        """
        
        success = driver.execute_script(script)
        
        if success:
            logger.info("✅ Bannière de cookies acceptée")
            time.sleep(1)  # Réduit de 2 à 1 seconde
            return True
        else:
            logger.warning("⚠️ Bannière de cookies non trouvée ou déjà fermée")
            return True  # Continuer même si pas de bannière
            
    except Exception as e:
        logger.error(f"Erreur lors de la gestion de la bannière: {e}")
        return True  # Continuer même en cas d'erreur

def handle_alert_popup(driver):
    """Gère la pop-up d'alerte qui peut apparaître"""
    logger.info("🔔 Vérification des pop-ups d'alerte...")
    
    try:
        # Attendre un peu pour que la pop-up se charge si elle doit apparaître
        time.sleep(0.5)
        
        # Sélecteurs pour détecter la pop-up d'alerte
        popup_selectors = [
            'div:contains("Accélérez votre recherche")',
            'div:contains("Créer une alerte")', 
            '[role="dialog"]',
            '.modal',
            '.popup'
        ]
        
        # Sélecteurs pour fermer la pop-up (croix X)
        close_selectors = [
            'button[aria-label="Fermer"]',
            'button[aria-label="Close"]', 
            'button[aria-label="Fermer la modal"]',
            'button.close',
            '.modal-close',
            '.popup-close',
            '[data-testid*="close"]',
            '[aria-label*="fermer"]',
            '[aria-label*="close"]',
            'svg[aria-label="Fermer"]',
            'svg[aria-label="Close"]'
        ]
        
        # Vérifier si une pop-up est présente
        popup_found = False
        for selector in popup_selectors:
            try:
                if ':contains(' in selector:
                    # Utiliser XPath pour :contains
                    xpath_selector = "//div[contains(text(), 'Accélérez votre recherche') or contains(text(), 'Créer une alerte')]"
                    elements = driver.find_elements(By.XPATH, xpath_selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    for element in elements:
                        if element.is_displayed():
                            popup_found = True
                            logger.info("🔔 Pop-up d'alerte détectée")
                            break
            except:
                continue
            
            if popup_found:
                break
        
        if not popup_found:
            logger.info("ℹ️ Aucune pop-up d'alerte détectée")
            return True
        
        # Essayer de fermer la pop-up
        for selector in close_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if buttons:
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            logger.info("✅ Pop-up d'alerte fermée")
                            time.sleep(1)
                            return True
            except Exception as e:
                continue
        
        # Si aucun bouton de fermeture n'est trouvé, essayer d'appuyer sur Escape
        logger.info("🔄 Tentative de fermeture avec la touche Escape...")
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(1)
        
        logger.info("✅ Tentative de fermeture de la pop-up effectuée")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la gestion de la pop-up d'alerte: {e}")
        return True  # Continuer même en cas d'erreur

def search_saumur(driver):
    """Recherche la ville de Saumur"""
    logger.info("🏠 Recherche de Saumur...")
    
    # Différents sélecteurs possibles pour le champ de recherche
    search_selectors = [
        'input[placeholder*="Saisir le lieu"]',
        'input[placeholder*="lieu ou le code postal"]',
        'input[name="location"]',
        'input[data-testid="location-input"]',
        '.css-rbpmd input',
        '#location-input',
        '[data-cy="location-input"]',
        'input[type="text"]'
    ]
    
    for selector in search_selectors:
        try:
            logger.info(f"🔍 Tentative avec le sélecteur: {selector}")
            
            # Attendre que l'élément soit présent et visible (réduit de 10 à 5 secondes)
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            # Cliquer sur le champ pour le focus
            element.click()
            time.sleep(0.5)  # Réduit de 1 à 0.5 seconde
            
            # Effacer le contenu existant
            element.clear()
            time.sleep(0.2)  # Réduit de 0.5 à 0.2 seconde
            
            # Saisir "Saumur"
            element.send_keys("Saumur")
            logger.info("✅ 'Saumur' saisi dans le champ de recherche")
            time.sleep(1)  # Réduit de 2 à 1 seconde
            
            # Appuyer sur Entrée pour valider
            element.send_keys(Keys.RETURN)
            logger.info("⌨️ Touche Entrée pressée pour valider la recherche")
            time.sleep(2)  # Réduit de 3 à 2 secondes
            
            return True
                
        except TimeoutException:
            logger.warning(f"⏰ Timeout avec le sélecteur: {selector}")
            continue
        except Exception as e:
            logger.error(f"❌ Erreur avec le sélecteur {selector}: {e}")
            continue
    
    logger.error("❌ Impossible de trouver le champ de recherche")
    return False

def wait_for_results(driver):
    """Attend que les résultats de recherche se chargent"""
    logger.info("⏳ Attente des résultats de recherche...")
    
    try:
        # Attendre que l'URL change ou que des résultats apparaissent (réduit de 15 à 8 secondes)
        WebDriverWait(driver, 8).until(
            lambda d: "saumur" in d.current_url.lower() or 
                     len(d.find_elements(By.CSS_SELECTOR, '[data-testid*="classified-card-mfe"]')) > 0
        )
        
        logger.info(f"✅ Résultats chargés - URL: {driver.current_url}")
        return True
        
    except TimeoutException:
        logger.warning("⏰ Timeout lors de l'attente des résultats")
        logger.info(f"URL actuelle: {driver.current_url}")
        return False

def scroll_and_collect_listings(driver, max_scrolls=30):
    """Navigue par pagination et récupère toutes les annonces"""
    logger.info("📜 Début de la navigation par pagination et de la récupération des annonces...")
    
    all_listings = []
    page_number = 1
    max_pages = 999  # Pas de limite, on va jusqu'au bout
    
    while page_number <= max_pages:
        try:
            logger.info(f"🔄 Page {page_number}/{max_pages}")
            
            # Attendre que la page se charge complètement
            time.sleep(1)
            
            # Gérer une éventuelle pop-up d'alerte sur cette page
            handle_alert_popup(driver)
            
            # Récupérer les annonces de la page actuelle
            try:
                elements = driver.find_elements(
                    By.CSS_SELECTOR, 
                    '[data-testid*="classified-card-mfe"]'
                )
                logger.info(f"✅ Trouvé {len(elements)} éléments avec le sélecteur: [data-testid*=\"classified-card-mfe\"]")
                
                # Extraire les données de chaque annonce
                new_listings = []
                for element in elements:
                    listing_data = extract_listing_data_fast(element)
                    if listing_data:
                        # Éviter les doublons
                        if not any(existing.get('url') == listing_data.get('url') for existing in all_listings):
                            new_listings.append(listing_data)
                
                if new_listings:
                    all_listings.extend(new_listings)
                    logger.info(f"📊 {len(new_listings)} nouvelles annonces récupérées (Total: {len(all_listings)})")
                else:
                    logger.info("ℹ️ Aucune nouvelle annonce trouvée sur cette page")
                
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des annonces: {e}")
            
            # Chercher le bouton "Page suivante" ou "Suivant"
            next_button = None
            next_selectors = [
                'a[aria-label*="suivant"]',
                'a[aria-label*="Suivant"]', 
                'a[aria-label*="next"]',
                'a[aria-label*="Next"]',
                'button[aria-label*="suivant"]',
                'button[aria-label*="Suivant"]',
                '[data-testid*="next"]',
                '[data-testid*="suivant"]',
                '.pagination a[rel="next"]',
                '.pagination .next',
                'a:contains("Suivant")',
                'button:contains("Suivant")',
                'a[title*="suivant"]',
                'a[title*="Suivant"]'
            ]
            
            logger.info("🔍 Recherche du bouton 'Page suivante'...")
            
            for selector in next_selectors:
                try:
                    if ':contains(' in selector:
                        # Utiliser XPath pour :contains
                        xpath_selector = f"//a[contains(text(), 'Suivant')] | //button[contains(text(), 'Suivant')]"
                        buttons = driver.find_elements(By.XPATH, xpath_selector)
                    else:
                        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if buttons:
                        for button in buttons:
                            # Vérifier si le bouton est visible et cliquable
                            if button.is_displayed() and button.is_enabled():
                                # Vérifier qu'il ne s'agit pas d'un bouton désactivé
                                class_name = button.get_attribute('class') or ''
                                if 'disabled' not in class_name and 'inactive' not in class_name:
                                    next_button = button
                                    logger.info(f"✅ Bouton 'Page suivante' trouvé avec le sélecteur: {selector}")
                                    break
                    
                    if next_button:
                        break
                        
                except Exception as e:
                    continue
            
            # Si aucun bouton "suivant" n'est trouvé, essayer de détecter les numéros de page
            if not next_button:
                logger.info("🔍 Recherche des numéros de page...")
                try:
                    # Chercher la page suivante (numéro + 1)
                    next_page_num = page_number + 1
                    page_selectors = [
                        f'a[aria-label="Page {next_page_num}"]',
                        f'a:contains("{next_page_num}")',
                        f'button:contains("{next_page_num}")',
                        f'[data-page="{next_page_num}"]'
                    ]
                    
                    for selector in page_selectors:
                        try:
                            if ':contains(' in selector:
                                xpath_selector = f"//a[contains(text(), '{next_page_num}')] | //button[contains(text(), '{next_page_num}')]"
                                buttons = driver.find_elements(By.XPATH, xpath_selector)
                            else:
                                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                            
                            if buttons:
                                for button in buttons:
                                    if button.is_displayed() and button.is_enabled():
                                        next_button = button
                                        logger.info(f"✅ Page {next_page_num} trouvée")
                                        break
                            
                            if next_button:
                                break
                        except:
                            continue
                            
                except Exception as e:
                    logger.error(f"Erreur lors de la recherche des numéros de page: {e}")
            
            # Si un bouton est trouvé, cliquer dessus
            if next_button:
                try:
                    # Scroller vers le bouton pour s'assurer qu'il est visible
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(0.5)
                    
                    # Fermer toute pop-up qui pourrait gêner
                    handle_alert_popup(driver)
                    
                    # Essayer d'abord un clic normal
                    logger.info(f"👆 Clic sur le bouton 'Page suivante'...")
                    try:
                        next_button.click()
                    except Exception as click_error:
                        logger.warning(f"⚠️ Clic normal échoué: {click_error}")
                        # Essayer un clic JavaScript si le clic normal échoue
                        logger.info("🔄 Tentative de clic JavaScript...")
                        driver.execute_script("arguments[0].click();", next_button)
                    
                    # Attendre le chargement de la nouvelle page
                    time.sleep(2)
                    page_number += 1
                    logger.info(f"✅ Navigation vers page {page_number} réussie")
                    
                except Exception as e:
                    logger.error(f"❌ Erreur lors du clic sur le bouton suivant: {e}")
                    logger.info("🔄 Tentative de continuer malgré l'erreur...")
                    break
            else:
                logger.info("🔚 Aucun bouton 'Page suivante' trouvé - fin de la pagination")
                break
                
        except Exception as e:
            logger.error(f"Erreur sur la page {page_number}: {e}")
            break
    
    logger.info(f"🎯 Navigation terminée: {len(all_listings)} annonces au total sur {page_number-1} pages")
    return all_listings

def extract_listing_data_fast(element):
    """Version rapide d'extraction : URL + ID uniquement"""
    try:
        # URL de l'annonce (lien principal)
        try:
            link_elem = element.find_element(By.CSS_SELECTOR, 'a')
            url = link_elem.get_attribute('href')
            if url:
                # Extraire l'ID depuis l'URL
                import re
                id_patterns = [
                    r'/(\d+)\.htm',  # URLs SeLoger classiques
                    r'/detail/(\d+)',  # URLs SeLoger-Construire
                    r'/(\d+)/detail\.htm'  # URLs BellesDemeures
                ]
                
                listing_id = None
                for pattern in id_patterns:
                    match = re.search(pattern, url)
                    if match:
                        listing_id = match.group(1)
                        break
                
                # Si aucun pattern ne correspond, essayer d'extraire n'importe quel nombre long
                if not listing_id:
                    numbers = re.findall(r'\d{8,}', url)
                    if numbers:
                        listing_id = numbers[0]
                
                if listing_id:
                    return {
                        "url": url,
                        "id": listing_id
                    }
        except:
            pass
        
        return None
        
    except Exception as e:
        return None

def save_listings_to_file(listings, filename="saumur_listings.json"):
    """Sauvegarde les annonces dans un fichier JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 {len(listings)} annonces sauvegardées dans {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde: {e}")
        return False

def main():
    """Fonction principale"""
    # Gestion des arguments
    parser = argparse.ArgumentParser(description="Scraper SeLoger avec Supabase")
    parser.add_argument("--supabase-url", help="URL Supabase")
    parser.add_argument("--supabase-key", help="Clé API Supabase")
    parser.add_argument("--headless", action="store_true", default=True, help="Mode invisible (défaut: activé)")
    parser.add_argument("--visible", action="store_false", dest="headless", help="Mode visible")
    
    args = parser.parse_args()
    
    driver = None
    supabase_manager = None
    
    try:
        logger.info("🎬 Démarrage du script SeLoger complet...")
        
        # Initialiser Supabase si les paramètres sont fournis
        if args.supabase_url and args.supabase_key:
            logger.info("📊 Initialisation de Supabase...")
            supabase_manager = SupabaseManager(args.supabase_url, args.supabase_key)
            
            # Créer une campagne de recherche
            search_config = {
                'ville': 'saumur',
                'type_bien': 'tous',
                'type_transaction': 'vente'
            }
            search_url = "https://www.seloger.com/list.htm?tri=initial&naturebien=1,2,4&idtt=2&idtypebien=1,2&ci=490328"
            supabase_manager.create_search_campaign(search_config, search_url)
        
        # Configuration du driver
        driver = setup_driver(headless=args.headless)
        if not driver:
            logger.error("❌ Impossible de configurer le driver")
            return
        
        # Aller sur SeLoger
        logger.info("🌐 Navigation vers SeLoger...")
        driver.get("https://www.seloger.com")
        
        # Charger les cookies
        logger.info("🍪 Chargement des cookies...")
        load_cookies(driver, "cookies seloger.txt")
        
        # Recharger la page avec les cookies
        logger.info("🔄 Rechargement de la page avec les cookies...")
        driver.refresh()
        time.sleep(0.5)  # Minimal pour le chargement
        
        # Gérer la bannière de cookies
        handle_cookie_banner(driver)
        
        # Gérer les pop-ups d'alerte qui peuvent apparaître
        handle_alert_popup(driver)
        
        # Rechercher Saumur
        if search_saumur(driver):
            logger.info("🎯 Recherche de Saumur réussie")
            
            # Attendre les résultats
            if wait_for_results(driver):
                logger.info("✅ Résultats de recherche chargés")
                
                # Gérer une éventuelle pop-up d'alerte après le chargement des résultats
                handle_alert_popup(driver)
                
                # Navigation par pagination et récupération des annonces
                listings = scroll_and_collect_listings(driver)  # Toutes les pages disponibles
                
                if listings:
                    # Sauvegarder les annonces en local
                    save_listings_to_file(listings)
                    
                    # Envoyer vers Supabase si configuré
                    if supabase_manager and supabase_manager.supabase:
                        logger.info("🔗 Envoi vers Supabase...")
                        supabase_manager.send_listings_to_supabase(listings)
                        supabase_manager.update_campaign_status('completed', total_listings=len(listings))
                    
                    # Afficher un résumé
                    logger.info("📋 Résumé des annonces récupérées:")
                    for i, listing in enumerate(listings[:5], 1):  # Afficher les 5 premières
                        logger.info(f"   {i}. ID: {listing.get('id', 'Sans ID')} - URL: {listing.get('url', 'Sans URL')[:80]}...")
                    
                    if len(listings) > 5:
                        logger.info(f"   ... et {len(listings) - 5} autres annonces")
                    
                    logger.info("🎉 ✅ Script terminé avec succès!")
                else:
                    logger.warning("⚠️ Aucune annonce récupérée")
                    if supabase_manager and supabase_manager.supabase:
                        supabase_manager.update_campaign_status('completed', total_listings=0)
            else:
                logger.warning("⚠️ Résultats non chargés dans les temps")
                if supabase_manager and supabase_manager.supabase:
                    supabase_manager.update_campaign_status('failed')
        else:
            logger.error("❌ Échec de la recherche de Saumur")
            if supabase_manager and supabase_manager.supabase:
                supabase_manager.update_campaign_status('failed')
        
    except Exception as e:
        logger.error(f"Erreur dans le script principal: {e}")
        if supabase_manager and supabase_manager.supabase:
            supabase_manager.update_campaign_status('failed')
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("🔚 Navigateur fermé")
            except:
                pass

if __name__ == "__main__":
    main() 