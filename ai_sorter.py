# -*- coding: utf-8 -*-
import os
import json
import google.generativeai as genai

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

PROFIL_CANDIDAT = """
Je suis un ingénieur passionné par la Data et la Finance. 
Je cherche des postes de Data Engineer, Data Scientist, tout ce qui touche à la Data ou Développeur DevOps.
J'aime aussi les postes en Finance de Marché (Quant, IT Finance, ETF, Finance personnelle).
Technos : Python, SQL, Cloud, Big Data.
Je préfère les boites qui rémunèrent bien les VIE et qui ont une bonne réputation auprès des anciens VIE.
De préférence dans des grandes villes ou capitales économiques mais pas en Europe.
Je suis ouvert aux missions en Asie, Amérique du Nord, Moyen-Orient ou Afrique.
Je n'aime pas les missions trop éloignées des centres-villes.
J'aime les missions avec des responsabilités techniques, de la gestion de projet ou du management d'équipe.
Je n'aime pas les missions trop orientées "support" ou "maintenance".
"""

def trier_offres_ia(offres):
    """Trie les offres par pertinence via Gemini Pro"""
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
            offres_text += f"Mission: {o['mission'][:300]}...\n\n" # Tronquer pour le contexte
            
        prompt = f"""
        Voici une liste d'offres d'emploi VIE et mon profil.
        
        MON PROFIL:
        {PROFIL_CANDIDAT}
        
        TACHE:
        Trie ces offres de la plus pertinente à la moins pertinente pour mon profil.
        Retourne UNIQUEMENT un tableau JSON contenant les IDs des offres dans l'ordre trié.
        Exemple de réponse: [2, 0, 4, 1, 3]
        Ne mets pas de markdown, juste le tableau brut.
        
        LISTE DES OFFRES:
        {offres_text}
        """
        
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        
        # Nettoyage basique si l'IA met du markdown
        if text_resp.startswith('```json'): text_resp = text_resp[7:]
        if text_resp.startswith('```'): text_resp = text_resp[3:]
        if text_resp.endswith('```'): text_resp = text_resp[:-3]
        
        indices = json.loads(text_resp)
        
        # Reconstruire la liste triée
        offres_triees = []
        for idx in indices:
            if 0 <= idx < len(offres):
                offres[idx]['score_ia'] = f"Top {len(offres_triees)+1}" # Marqueur optionnel
                offres_triees.append(offres[idx])
        
        # Ajouter celles qui manqueraient (au cas où l'IA en oublie, rare mais possible)
        seen_ids = set(indices)
        for i, off in enumerate(offres):
            if i not in seen_ids:
                offres_triees.append(off)
                
        print("✅ Tri IA effectué")
        return offres_triees
        
    except Exception as e:
        print(f"❌ Erreur Gemini: {e}")
        return offres # Fallback ordre original
