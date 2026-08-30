import os
from groq import Groq
from dotenv import load_dotenv

# Charge les variables d'environnement (dont GROQ_API_KEY)
load_dotenv()

# Initialisation du client Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

print("🚀 Liste exacte des modèles disponibles sur Groq :")
try:
    # Récupération de la liste des modèles
    modeles = client.models.list()
    
    # L'API Groq stocke les modèles dans l'attribut 'data'
    for model in modeles.data:
        print(f"- {model.id}")
        
except Exception as e:
    print(f"❌ Erreur : {e}")