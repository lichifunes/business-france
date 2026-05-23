# -*- coding: utf-8 -*-
import os
import json
import google.generativeai as genai

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

PROFIL_CANDIDAT = """
Je suis docteur en pharmacie (PharmD) à la recherche d'un VIE à Barcelone.
Je vise des postes en industrie pharmaceutique, biotech, santé ou sciences de
la vie qui valorisent mon doctorat.

POSTES RECHERCHÉS (par ordre de préférence) :
1. Affaires réglementaires / Regulatory Affairs
2. Recherche clinique (CRA, clinical research, essais cliniques)
3. Pharmacovigilance / Drug Safety
4. R&D / développement pharmaceutique / affaires scientifiques
5. Affaires médicales (MSL) / Market Access
6. Assurance qualité (QA/QC, GMP/BPF)

CE QUE J'AIME :
- Missions scientifiques ou réglementaires avec de la responsabilité
- Laboratoires pharma / biotech, environnement international
- Aires thérapeutiques et innovation santé
- Barcelone

CE QUE JE N'AIME PAS :
- Postes purement commerciaux / vente sans dimension scientifique
- Télévente, support pur
- Missions sans lien avec la pharmacie / santé / sciences de la vie
"""

def trier_offres_ia(offres):
    """Trie les offres par pertinence via Gemini et attribue un score 0-100"""
    if not offres:
        return []
    
    if not GEMINI_API_KEY:
        print("⚠️ Pas de clé API Gemini, pas de tri sémantique.")
        return offres

    print(f"🤖 Analyse IA de {len(offres)} offre(s)...")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # Préparer le prompt
        offres_text = ""
        for i, o in enumerate(offres):
            offres_text += f"ID {i}:\n"
            offres_text += f"Titre: {o['titre']}\n"
            offres_text += f"Entreprise: {o['entreprise']}\n"
            offres_text += f"Lieu: {o['lieu']}\n"
            offres_text += f"Mission: {o['mission'][:400]}\n\n"
            
        prompt = f"""
        Voici une liste d'offres d'emploi VIE et mon profil.
        
        MON PROFIL:
        {PROFIL_CANDIDAT}
        
        TACHE:
        Pour chaque offre, attribue un score de pertinence de 0 à 100 :
        - 90-100 : parfaitement aligné (affaires réglementaires/recherche clinique/pharmacovigilance à Barcelone)
        - 70-89  : très pertinent (R&D pharma, affaires médicales, qualité GMP en pharma/biotech)
        - 50-69  : intéressant (sciences de la vie, labo, qualité, lien santé valorisant le doctorat)
        - 30-49  : peu pertinent (santé mais peu scientifique, ou hors pharma)
        - 0-29   : hors sujet (commercial pur, support, sans lien avec la pharmacie/santé)

        Retourne UNIQUEMENT un tableau JSON d'objets avec "id" (int), "score" (int 0-100), "raison" (string courte max 15 mots).
        Exemple: [{{"id": 0, "score": 88, "raison": "Affaires réglementaires chez Novartis Barcelone, parfait match PharmD"}}, ...]
        
        IMPORTANT: Ne mets PAS de markdown autour. Juste le JSON brut.
        
        LISTE DES OFFRES:
        {offres_text}
        """
        
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        
        # Nettoyage si l'IA met du markdown
        if text_resp.startswith('```json'): text_resp = text_resp[7:]
        if text_resp.startswith('```'): text_resp = text_resp[3:]
        if text_resp.endswith('```'): text_resp = text_resp[:-3]
        text_resp = text_resp.strip()
        
        resultats = json.loads(text_resp)
        
        # Indexer les résultats par ID
        scores_map = {}
        for r in resultats:
            scores_map[r['id']] = {'score': r['score'], 'raison': r.get('raison', '')}
        
        # Attribuer les scores aux offres
        for i, offre in enumerate(offres):
            if i in scores_map:
                offre['score_ia'] = scores_map[i]['score']
                offre['raison_ia'] = scores_map[i]['raison']
            else:
                offre['score_ia'] = 0
                offre['raison_ia'] = ''
        
        # Trier par score décroissant
        offres_triees = sorted(offres, key=lambda x: x.get('score_ia', 0), reverse=True)
        
        # Log les top offres
        for o in offres_triees[:5]:
            print(f"  🏆 {o['score_ia']}/100 — {o['titre'][:45]} | {o.get('raison_ia', '')}")
                
        print(f"✅ Tri IA effectué ({len(offres_triees)} offres scorées)")
        return offres_triees
        
    except Exception as e:
        print(f"❌ Erreur Gemini: {e}")
        return offres # Fallback ordre original
