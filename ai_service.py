import types
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from google import genai

#charger la variable GOOGLE_API_KEY depuis le fichier .env
load_dotenv()

#initalisation du client unique pour tous les models

client = genai.Client()

def nettoyer_et_structurer_cv(texte_brut: str):
    """
    Étape 1 : Le modèle LOURD (Gemini 1.5 Pro).
    Prend le texte brut du PDF, retire le bruit et structure les données clés.
    """
    prompt = f"""
    Tu es un expert RH. Voici le texte brut extrait d'un CV, qui peut contenir des erreurs de formatage.
    Ton but est de nettoyer ce texte et d'en extraire les informations essentielles (Expériences, Compétences, Formation).
    Résume-le de manière claire et professionnelle, sans ajouter d'informations inventées.
    
    Texte brut :
    {texte_brut}
    """

    response = client.models.generate_content(
        model='gemini-1.5-pro',
        contents=prompt
    )

    return response.text


def classifier_secteur(texte_propre: str)->str:
    """
    Étape 2 : Le modèle RAPIDE (Gemini 1.5 Flash).
    Déduit le secteur d'activité pour notre filtre SQL hybride.
    """
    prompt = f"""
    Tu es un algorithme de classification. Analyse ce résumé de CV et retourne UNIQUEMENT le nom du secteur d'activité principal parmi cette liste : 
    [Informatique, Finance, Santé, Ingénierie, Marketing, Ressources Humaines, Logistique, Commercial, Autre].
    Ne réponds absolument rien d'autre que le mot exact de la liste.
    
    CV :
    {texte_propre}
    """

    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )

    return response.text.strip()

def generer_embedding(texte: str)->list[float]:
    """
    Étape 3 : Le modèle VECTORIEL (text-embedding-004).
    Transforme le texte propre en un vecteur de 768 dimensions.
    """

    response = client.models.embed_content(
        model='text-embedding-004',
        contents=texte,
        config=types.EmbedContentConfig(
            task_type='RETRIEVAL_DOCUMENT'
        )
    )
    return response.embeddings[0].values




# --- Zone de test local ---
if __name__ == "__main__":
    print("🚀 Lancement des tests des 3 modèles Gemini...")
    
    # Simulation d'un texte brut très moche sorti d'un PDF
    cv_bruit = "Page 1 - - Développeur JAVA . Exp: 3 ans. Spring Boot, angular... \n\n 12/2026 !! passionné par le code."
    
    print("\n1. Test Gemini 1.5 Pro (Nettoyage)...")
    cv_propre = nettoyer_et_structurer_cv(cv_bruit)
    print(cv_propre)
    
    print("\n2. Test Gemini 1.5 Flash (Secteur)...")
    secteur = classifier_secteur(cv_propre)
    print(f"Secteur trouvé : {secteur}")
    
    print("\n3. Test Embeddings (Vectorisation)...")
    vecteur = generer_embedding(cv_propre)
    print(f"✅ Vecteur généré ! Dimension : {len(vecteur)}")
    

