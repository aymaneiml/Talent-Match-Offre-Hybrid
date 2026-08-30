from google.genai import types
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from google import genai
from groq import Groq

#charger la variable GOOGLE_API_KEY depuis le fichier .env
load_dotenv()

# 1. Groq pour le texte (0 Go sur ton PC)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Gemini pour la vectorisation (0 Go sur ton PC)
gemini_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# On choisit l'un des modèles disponibles dans ta liste Groq
GROQ_MODEL = "openai/gpt-oss-20b"

def nettoyer_et_structurer_cv(texte_brut: str) -> str:
    """
    Étape 1 : Groq nettoie et structure le texte extrait du PDF.
    """
    prompt = f"""
    Tu es un expert RH. Voici le texte brut extrait d'un CV, qui peut contenir des erreurs de formatage.
    Ton but est de nettoyer ce texte et d'en extraire les informations essentielles (Expériences, Compétences, Formation).
    Résume-le de manière claire et professionnelle, sans ajouter d'informations inventées.
    
    Texte brut :
    {texte_brut}
    """
    
    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=GROQ_MODEL, 
        temperature=0.3
    )
    return chat_completion.choices[0].message.content


def classifier_secteur(texte_propre: str) -> str:
    """
    Étape 2 : Groq déduit le secteur d'activité.
    """
    prompt = f"""
    Tu es un algorithme de classification. Analyse ce résumé de CV et retourne UNIQUEMENT le nom du secteur d'activité principal parmi cette liste : 
    [Informatique, Finance, Santé, Ingénierie, Marketing, Ressources Humaines, Logistique, Commercial, Autre].
    Ne réponds absolument rien d'autre que le mot exact de la liste.
    
    CV :
    {texte_propre}
    """
    
    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=GROQ_MODEL,
        temperature=0.1 
    )
    return chat_completion.choices[0].message.content.strip()


def generer_embedding(texte: str)->list[float]:
    """
    Étape 3 : Le modèle VECTORIEL (gemini-embedding-2).
    Transforme le texte propre en un vecteur de 768 dimensions.
    """

    response = gemini_client.models.embed_content(
        model='gemini-embedding-2',
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
    

