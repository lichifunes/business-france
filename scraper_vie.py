#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper VIE - SANS URL
Détection doublons sur titre + entreprise + lieu
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from playwright.sync_api import sync_playwright
from datetime import datetime
import time
import sqlite3
import os
import html
from ai_sorter import trier_offres_ia

# ============================================
# CONFIGURATION
# ============================================

DB_FILE = 'offres_vie.db'

CRITERES = {
    'keywords': [
        # DATA
        'data', 'données', 'donnée', 'database', 'bd', 'base de données',
        'big data', 'données massives', 'data mining', 'exploration de données',
        
        # ENGINEER
        'engineer', 'ingénieur', 'ingenieur', 'ing', 'engineering', 'ingénierie',
        'software engineer', 'ingénieur logiciel', 'systems engineer',
        
        # DEVELOPER / DEV
        'developer', 'développeur', 'developpeur', 'dev', 'programmeur', 'programmer',
        'coder', 'codeur', 'software developer', 'application developer',
        
        # DATA ROLES
        'data engineer', 'ingénieur données', 'ingénieur data', 'data scientist',
        'data analyst', 'analyste données', 'analyste data', 'data architect',
        'architecte données', 'data platform engineer', 'etl developer',
        'etl engineer', 'data integration', 'intégration données',
        
        # ANALYST
        'analyst', 'analyste', 'analytics', 'analytique', 'business analyst',
        'analyste métier', 'analyste business', 'functional analyst',
        'analyste fonctionnel', 'systems analyst', 'analyste système',
        'financial analyst', 'analyste financier', 'reporting analyst',
        'insights analyst', 'operations analyst', 'process analyst',
        
        # SCIENTIST
        'scientist', 'scientifique', 'data scientist', 'research scientist',
        'chercheur', 'applied scientist', 'science des données',
        
        # BI & REPORTING
        'business intelligence', 'bi', 'intelligence économique',
        'bi developer', 'bi analyst', 'reporting', 'visualisation',
        'data visualization', 'dataviz', 'data viz', 'tableau', 'power bi',
        
        # MACHINE LEARNING / AI
        'machine learning', 'ml', 'apprentissage automatique',
        'ml engineer', 'mlops', 'ai', 'ia', 'artificial intelligence',
        'intelligence artificielle', 'deep learning', 'apprentissage profond',
        'nlp', 'natural language processing', 'traitement du langage',
        'computer vision', 'vision par ordinateur', 'neural network',
        
        # ARCHITECTURE
        'architect', 'architecte', 'solution architect', 'architecte solutions',
        'enterprise architect', 'cloud architect', 'architecte cloud',
        'technical architect', 'architecte technique',
        
        # DEVOPS / SRE
        'devops', 'dev ops', 'sre', 'site reliability', 'infrastructure',
        'platform engineer', 'ingénieur plateforme', 'automation',
        'automatisation', 'ci/cd', 'continuous integration',
        
        # BACKEND / FULLSTACK
        'backend', 'back-end', 'backend developer', 'développeur backend',
        'fullstack', 'full stack', 'full-stack', 'développeur fullstack',
        'fullstack developer', 'full stack developer',
        
        # LANGAGES PROGRAMMATION
        'python', 'java', 'javascript', 'c++', 'cpp', 'c#', 'csharp',
        'sql', 'nosql', 'cobol', 'scala', 'r', 'go', 'golang',
        'typescript', 'php', 'ruby', '.net', 'dotnet',
        
        # CLOUD / INFRA
        'cloud', 'aws', 'azure', 'gcp', 'google cloud', 'cloud computing',
        'kubernetes', 'docker', 'container', 'microservices', 'api',
        
        # DATA STORAGE
        'data warehouse', 'entrepôt de données', 'data lake', 'lac de données',
        'data platform', 'plateforme données', 'etl', 'elt', 'data hub',
        'data mart', 'datalake', 'datawarehouse',
        
        # TESTING / QA
        'testing', 'test', 'qa', 'quality assurance', 'qualité',
        'tester', 'testeur', 'test engineer', 'ingénieur test',
        'automation testing', 'test automation', 'qa engineer',
        
        # PRODUCT / MANAGEMENT
        'product', 'produit', 'product manager', 'chef de produit',
        'product owner', 'po', 'project manager', 'chef de projet',
        'scrum master', 'agile', 'technical lead', 'tech lead',
        
        # TECH GENERAL
        'tech', 'technology', 'technologie', 'it', 'informatique',
        'software', 'logiciel', 'application', 'system', 'système',
        'digital', 'numérique', 'innovation', 'transformation digitale',
        
        # BUSINESS / MANAGEMENT
        'business', 'métier', 'consultant', 'consulting', 'conseil',
        'strategy', 'stratégie', 'technical', 'technique', 'support',
        'specialist', 'spécialiste', 'expert', 'coordinator', 'coordinateur',
        
        # QUANT / FINANCE
        'quant', 'quantitative', 'quantitative analyst', 'quant developer',
        'quantitative researcher', 'financial engineer', 'ingénieur financier',
        'risk', 'risque', 'risk analyst', 'trading', 'trader',
        
        # DATA GOVERNANCE / MANAGEMENT
        'data governance', 'gouvernance données', 'data quality',
        'qualité données', 'data management', 'gestion données',
        'master data', 'mdm', 'metadata', 'métadonnées',
        
        # WEB / FRONTEND 
        'web', 'frontend', 'front-end', 'ux', 'ui', 'interface',
        'react', 'angular', 'vue', 'javascript developer',

        
        # ============================================
        # FINANCE / BANCAIRE

        # ASSET MANAGEMENT
        'asset', 'asset management', 'gestion d\'actifs', 'gestion actifs',
        'portfolio', 'portefeuille', 'fund', 'funds', 'fonds',
        'etf', 'mutual fund', 'opcvm', 'sicav', 'fcp',
        'hedge fund', 'private equity', 'investment', 'investissement',
        'wealth management', 'gestion de patrimoine',
        
        # TRADING / MARKETS
        'trading', 'trader', 'market', 'marché', 'marchés',
        'equity', 'equities', 'actions', 'fixed income', 'obligataire',
        'derivatives', 'dérivés', 'options', 'futures', 'swaps',
        'forex', 'fx', 'commodities', 'matières premières',
        'crypto', 'cryptocurrency', 'blockchain', 'bitcoin',
        
        # FRONT OFFICE
        'front office', 'sales', 'trading desk', 'desk',
        'execution', 'exécution', 'order management', 'oms',
        'trade', 'transaction', 'deal', 'booking',
        
        # MIDDLE OFFICE
        'middle office', 'control', 'contrôle', 'reconciliation',
        'rapprochement', 'settlement', 'règlement-livraison',
        'collateral', 'collatéral', 'margin', 'marge',
        
        # RISK MANAGEMENT
        'risk', 'risque', 'var', 'value at risk', 'credit risk',
        'risque de crédit', 'market risk', 'risque de marché',
        'operational risk', 'risque opérationnel', 'stress test',
        'compliance', 'conformité', 'regulatory', 'réglementaire',
        
        # QUANT / ALGO TRADING
        'quant', 'quantitative', 'quantitative analyst',
        'algo', 'algorithmic', 'algorithmique', 'algo trading',
        'high frequency', 'hft', 'market making', 'arbitrage',
        'pricing', 'pricer', 'valorisation', 'valuation',
        
        # FINTECH / TRADING SYSTEMS
        'fintech', 'trading system', 'système de trading',
        'trading platform', 'plateforme de trading',
        'market data', 'données de marché', 'real-time', 'temps réel',
        'low latency', 'faible latence', 'performance',
        
        # IT BANCAIRE / FINANCE
        'banking', 'banque', 'bank', 'financial', 'financier',
        'finance it', 'it finance', 'financial services',
        'services financiers', 'capital markets', 'marchés de capitaux',
        'investment banking', 'banque d\'investissement',
        
        # SYSTÈMES & APPLICATIONS
        'murex', 'summit', 'calypso', 'sophis', 'reuters',
        'bloomberg', 'refinitiv', 'simcorp', 'aladdin',
        'front arena', 'kondor', 'kondor+', 'wall street',
        
        # RÉGULATION / REPORTING
        'mifid', 'basel', 'bâle', 'emir', 'dodd-frank',
        'regulatory reporting', 'reporting réglementaire',
        'solvency', 'solvabilité', 'capital', 'liquidity',
        
        # INSTRUMENTS FINANCIERS
        'bond', 'obligation', 'stock', 'action', 'share',
        'warrant', 'certificate', 'structured product',
        'produit structuré', 'exotic', 'vanilla',
        
        # OPERATIONS / POST-TRADE
        'operations', 'opérations', 'post-trade', 'post-marché',
        'clearing', 'compensation', 'custody', 'conservation',
        'back office', 'corporate actions', 'événements',
        
        # TREASURY / CASH
        'treasury', 'trésorerie', 'cash management', 'gestion de trésorerie',
        'liquidity', 'liquidité', 'funding', 'financement',
        'payment', 'paiement', 'swift', 'sepa',
        
        # ASSET SERVICING
        'transfer agent', 'agent de transfert', 'nav', 'valeur liquidative',
        'unit', 'part', 'subscription', 'souscription',
        'redemption', 'rachat', 'distribution', 'dividend',
        
        # PERFORMANCE / ANALYTICS
        'performance', 'attribution', 'benchmark', 'indice',
        'tracking', 'suivi', 'monitoring', 'surveillance',
        'dashboard', 'tableau de bord', 'kpi', 'reporting',
        
        # SECURITIES / INSTRUMENTS
        'securities', 'titres', 'financial instrument',
        'instrument financier', 'asset class', 'classe d\'actifs',
        'alternative', 'alternatif', 'real estate', 'immobilier',
        
        # CREDIT / LOANS
        'credit', 'crédit', 'loan', 'prêt', 'lending',
        'syndication', 'structured finance', 'finance structurée',
        'leveraged finance', 'corporate lending',
        
        # ESG / SUSTAINABLE
        'esg', 'sustainable', 'durable', 'green', 'vert',
        'sri', 'isr', 'responsible investment', 'impact',
        
        # CLIENT / DISTRIBUTION
        'client', 'customer', 'distribution', 'onboarding',
        'kyc', 'know your customer', 'aml', 'anti money laundering',
        'blanchiment', 'due diligence',
        
        # APPLICATIONS MÉTIER
        'pms', 'portfolio management system', 'oms', 'order management',
        'ems', 'execution management', 'rms', 'risk management system',
        'accounting', 'comptabilité', 'general ledger', 'grand livre',
        
        # AUTRES FINANCE/IT
        'financial data', 'données financières', 'market data feed',
        'flux de marché', 'tick', 'quote', 'cotation',
        'book', 'carnet d\'ordres', 'matching engine',
    ]
}


def _env(name, default):
    value = os.getenv(name)
    return value if value not in (None, '') else default


EMAIL_CONFIG = {
    'from': _env('EMAIL_FROM', 'lpennarguear@gmail.com'),
    'sender_name': _env('EMAIL_SENDER_NAME', 'Scraper VIE'),
    'to': _env('EMAIL_TO', 'lpennarguear@gmail.com'),
    'password': os.getenv('EMAIL_PASSWORD', ''),
    'smtp_server': _env('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(_env('SMTP_PORT', '587'))
}

# ============================================
# DATABASE
# ============================================

def init_database():
    print(f"[DEBUG] BDD : {os.path.abspath(DB_FILE)}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Table SANS contrainte URL, avec clé composite titre+entreprise+lieu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            entreprise TEXT,
            lieu TEXT,
            date_trouvee TEXT,
            date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(titre, entreprise, lieu)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ BDD OK ({os.path.getsize(DB_FILE)} octets)\n")


def offre_existe(titre, entreprise, lieu):
    """Vérifie si l'offre existe sur la base titre+entreprise+lieu"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM offres 
        WHERE titre = ? AND entreprise = ? AND lieu = ?
    ''', (titre, entreprise, lieu))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def inserer_offre(offre):
    """Insère une offre dans la base"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO offres (titre, entreprise, lieu, date_trouvee)
            VALUES (?, ?, ?, ?)
        ''', (offre['titre'], offre['entreprise'], offre['lieu'], offre['date']))
        conn.commit()
        print(f"  💾 Insérée")
    except sqlite3.IntegrityError:
        print(f"  ⚠️ Doublon")
    except Exception as e:
        print(f"  ❌ Erreur : {e}")
    finally:
        conn.close()


def get_stats():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM offres')
    total = cursor.fetchone()[0]
    conn.close()
    return total


def affiche_bdd_sample():
    print("\n[DEBUG] Dernières offres en base :")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT titre, entreprise, lieu FROM offres ORDER BY id DESC LIMIT 5')
    rows = cursor.fetchall()
    if len(rows) == 0:
        print("  ❌ Base vide")
    else:
        for i, row in enumerate(rows, 1):
            print(f"  {i}. {row[0][:40]} | {row[1][:30]} | {row[2]}")
    conn.close()

# ============================================
# SCRAPING
# ============================================

def scraper_offres_vie():
    print("🚀 Scraping...")
    
    with sync_playwright() as p:
        headless = os.getenv('HEADLESS', 'true').lower() not in {'0', 'false', 'no'}
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        # page.goto('https://mon-vie-via.businessfrance.fr/offres/recherche?latest=true', timeout=60000)
        page.goto('https://mon-vie-via.businessfrance.fr/offres/recherche?query&specializationsIds=212&specializationsIds=24&missionsTypesIds=VIE&teletravail=0&porteEnv=0', timeout=60000)
        time.sleep(5)
        
        # Fermer popup cookies
        try:
            page.query_selector('button#didomi-notice-agree-button').click()
            time.sleep(2)
        except:
            pass
        
        # Nombre total
        try:
            total = int(''.join(filter(str.isdigit, page.query_selector('.count').inner_text())))
            print(f"🎯 Total : {total} offres")
        except:
            total = 9999
        
        while True:
            elements = page.query_selector_all('.figure_container')
            print(f"📊 Chargées : {len(elements)}/{total}")
            
            if len(elements) >= total:
                break
            
            try:
                btn = page.query_selector('a.btn_bleu_vert.see-more-btn')
                if btn and btn.is_visible():
                    btn.scroll_into_view_if_needed()
                    time.sleep(1)
                    btn.click(force=True)
                    time.sleep(1)
                else:
                    break
            except:
                break
        
        # Extraire
        elements = page.query_selector_all('.figure_container')
        print(f"✅ Total : {len(elements)} offres\n")
        
        offres = []
        for el in elements:
            try:
                content_el = el.query_selector('figcaption.offer-content') or el

                titre_el = content_el.query_selector('h2.mission-title') or content_el.query_selector('h2:not(.location)') or el.query_selector('h2')
                titre = titre_el.inner_text().strip() if titre_el else 'N/A'

                entreprise_el = content_el.query_selector('h3.organization-name') or el.query_selector('h3.organization-name')
                entreprise = entreprise_el.inner_text().strip() if entreprise_el else 'N/A'

                lieu_el = content_el.query_selector('h2.location') or content_el.query_selector('.location') or el.query_selector('.location')
                lieu = lieu_el.text_content().strip() if lieu_el else 'N/A'

                mission_el = content_el.query_selector('h4.mission-excerpt')
                mission = mission_el.inner_text().strip() if mission_el else ''

                meta_items = []
                meta_list = content_el.query_selector_all('ul.meta-list li') if content_el else []
                for li in meta_list:
                    text = li.inner_text().strip()
                    if text:
                        meta_items.append(text)
                meta = " | ".join(meta_items)

                offres.append({
                    'titre': titre,
                    'entreprise': entreprise,
                    'lieu': lieu,
                    'mission': mission,
                    'meta': meta,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
            except:
                continue
        
        browser.close()
        return offres


def filtrer_offres(offres):
    print(f"🔍 Filtrage de {len(offres)} offres...\n")
    filtrees = []
    
    for offre in offres:
        if any(kw in offre['titre'].lower() for kw in CRITERES['keywords']):
            filtrees.append(offre)
            print(f"✅ {offre['titre'][:60]} | {offre['entreprise'][:30]}")
    
    print(f"\n📊 {len(filtrees)} matchent\n")
    return filtrees


def filtrer_nouvelles_offres(offres):
    print(f"🔍 Vérification doublons...\n")
    nouvelles = []
    
    for offre in offres:
        if not offre_existe(offre['titre'], offre['entreprise'], offre['lieu']):
            nouvelles.append(offre)
            print(f"🆕 {offre['titre'][:60]}")
            inserer_offre(offre)
        else:
            print(f"⏭️ {offre['titre'][:60]}")
    
    print(f"\n📊 {len(nouvelles)} NOUVELLE(S)\n")
    return nouvelles


def envoyer_email(offres):
    if len(offres) == 0:
        print("📧 Pas de nouvelles offres\n")
        return
    
    print(f"📧 Envoi email ({len(offres)} offres)...")

    def _format_offre_html(offre, index):
        def _esc(value: str) -> str:
            return html.escape(value or '')

        titre = _esc(offre.get('titre', ''))
        entreprise = _esc(offre.get('entreprise', ''))
        lieu = _esc(offre.get('lieu', ''))
        mission_text = (offre.get('mission') or '').strip()
        meta_text = (offre.get('meta') or '').strip()
        
        mission_html = _esc(mission_text).replace('\n', '<br>')
        
        # Tags (badges) pour les métadonnées
        tags_html = ""
        if meta_text:
            tags = [t.strip() for t in meta_text.split('|')]
            for tag in tags:
                if tag:
                    tags_html += (
                        f'<span style="display:inline-block;background:#f1f5f9;color:#475569;'
                        f'padding:4px 10px;border-radius:12px;font-size:11px;font-weight:600;'
                        f'margin-right:6px;margin-bottom:6px;">{_esc(tag)}</span>'
                    )

        # Badge IA Score si présent
        score_html = ""
        if 'score_ia' in offre:
             score_html = (
                 f'<td style="text-align:right;vertical-align:middle;">'
                 f'<span style="background:#dcfce7;color:#166534;padding:4px 8px;border-radius:4px;'
                 f'font-size:11px;font-weight:700;">🤖 {offre["score_ia"]}</span></td>'
             )
        else:
             score_html = '<td></td>'

        return (
            f"""
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px;border:1px solid #e2e8f0;border-collapse:collapse;">
                <tr><td style="height:6px;background:linear-gradient(90deg, #6366f1, #8b5cf6);font-size:0;line-height:0;" colspan="2">&nbsp;</td></tr>
                <tr><td style="padding:20px 24px;" colspan="2">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td style="vertical-align:middle;">
                                <span style="font-size:11px;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.05em;background:#eef2ff;padding:4px 8px;">OFFRE #{index}</span>
                            </td>
                            {score_html}
                        </tr>
                    </table>
                    <h2 style="margin:12px 0 8px 0;font-size:18px;font-weight:800;color:#1e293b;line-height:1.3;font-family:Arial,Helvetica,sans-serif;">{titre}</h2>
                    <p style="margin:0 0 16px 0;font-size:14px;color:#64748b;">
                        <strong style="color:#334155;">🏢 {entreprise}</strong> &bull; 📍 {lieu}
                    </p>
                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:12px;">
                        <tr><td style="background:#f8fafc;border:1px solid #f1f5f9;padding:14px;">
                            <div style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;margin-bottom:6px;letter-spacing:0.05em;">Mission</div>
                            <div style="color:#334155;font-size:13px;line-height:1.6;">{mission_html}</div>
                        </td></tr>
                    </table>
                    <div>{tags_html}</div>
                </td></tr>
            </table>
            """
        )

    items_html = ''.join(_format_offre_html(o, i + 1) for i, o in enumerate(offres))
    
    html_body = f"""<html>
    <head><meta charset="utf-8"></head>
    <body style="margin:0;padding:0;background:#eef1f6;font-family:Arial,Helvetica,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#eef1f6;">
            <tr><td align="center" style="padding:24px 16px;">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border:1px solid #e2e8f0;">
                    <!-- Header -->
                    <tr><td style="background:#0f172a;color:#ffffff;padding:28px 32px;">
                        <div style="font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:#94a3b8;">VIE Daily Digest</div>
                        <h1 style="margin:8px 0 6px;font-size:24px;line-height:1.2;color:#ffffff;">{len(offres)} nouvelle(s) offre(s)</h1>
                        <div style="font-size:13px;color:#94a3b8;">{datetime.now().strftime('%d/%m/%Y à %H:%M')}</div>
                    </td></tr>
                    <!-- Contenu -->
                    <tr><td style="padding:24px 28px;background:#f8fafc;">
                        <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:16px;">
                            <tr><td style="background:#e2e8f0;color:#0f172a;padding:6px 14px;font-size:12px;font-weight:600;">
                                Sélection filtrée &bull; {len(offres)} résultats
                            </td></tr>
                        </table>
                        {items_html}
                    </td></tr>
                    <!-- Footer -->
                    <tr><td style="padding:18px 28px;color:#64748b;font-size:12px;background:#ffffff;border-top:1px solid #e2e8f0;text-align:center;">
                        Scraper VIE automatique — Simple &bull; Efficace &bull; Moderne
                    </td></tr>
                </table>
            </td></tr>
        </table>
    </body>
    </html>"""
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🎯 {len(offres)} nouvelle(s) offre(s) VIE - {datetime.now().strftime('%d/%m/%Y')}"
    msg['From'] = formataddr((EMAIL_CONFIG['sender_name'], EMAIL_CONFIG['from']))
    msg['To'] = EMAIL_CONFIG['to']
    msg.attach(MIMEText(html_body, 'html'))
    
    # Debug config (sans mot de passe)
    pwd_preview = EMAIL_CONFIG['password'][:3] + '***' if EMAIL_CONFIG['password'] else '(VIDE!)'
    print(f"[MAIL] From: {EMAIL_CONFIG['from']}")
    print(f"[MAIL] To: {EMAIL_CONFIG['to']}")
    print(f"[MAIL] SMTP: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
    print(f"[MAIL] Password: {pwd_preview}")
    
    try:
        print("[MAIL] Connexion SMTP...")
        srv = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'], timeout=30)
        srv.ehlo()
        print("[MAIL] STARTTLS...")
        srv.starttls()
        srv.ehlo()
        print("[MAIL] Login...")
        srv.login(EMAIL_CONFIG['from'], EMAIL_CONFIG['password'])
        print("[MAIL] Envoi...")
        srv.send_message(msg)
        srv.quit()
        print("✅ Email envoyé !\n")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Erreur AUTH SMTP : {e}")
        print("💡 Vérifiez que EMAIL_PASSWORD est un App Password Gmail (16 chars)")
        print(f"💡 Compte utilisé : {EMAIL_CONFIG['from']}\n")
    except smtplib.SMTPException as e:
        print(f"❌ Erreur SMTP : {e}\n")
    except Exception as e:
        import traceback
        print(f"❌ Erreur inattendue : {e}")
        traceback.print_exc()
        print()

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 SCRAPER VIE - SANS URL")
    print("="*60 + "\n")
    
    init_database()
    print(f"📊 Base AVANT : {get_stats()} offres")
    affiche_bdd_sample()
    
    offres = scraper_offres_vie()
    offres_filtrees = filtrer_offres(offres)
    nouvelles = filtrer_nouvelles_offres(offres_filtrees)
    
    # Tri intelligent si activé
    nouvelles_triees = trier_offres_ia(nouvelles)
    
    envoyer_email(nouvelles_triees)
    
    print(f"📊 Base APRÈS : {get_stats()} offres")
    affiche_bdd_sample()
    
    print("\n" + "="*60)
    print("✅ Terminé !")
    print("="*60 + "\n")
