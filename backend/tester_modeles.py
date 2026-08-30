from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


print("🚀 Liste exacte des modèles autorisés pour ta clé API :")
try:
    for model in client.models.list():
        # Affiche uniquement les modèles capables de générer du texte ou des embeddings
        if model.name.startswith("models/gemini") or model.name.startswith("models/text-embedding"):
            print(f"- {model.name.replace('models/', '')}")
except Exception as e:
    print(f"Erreur : {e}")