# Les routes de ton API (FastAPI)
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymupdf  # PyMuPDF
import ai_service
import database

#initialisation de l'application
app = FastAPI(
    title="Talent-Match-Offre-Hybrid API",
    description="API de matching hybride (SQL + Vectoriel) propulsée par Gemini",
    version="1.0.0"
)

# Configuration CORS pour autoriser ton frontend (Angular/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """S'exécute au lancement de l'API pour préparer la base de données."""
    database.initialiser_base()

#endpoitn : ingestion d'un CV
@app.post("/upload-cv", tags=["Pipeline CV"])
async def upload_cv(file: UploadFile = File(...)):
    """Phase 1 & 2 : Reçoit un PDF, extrait, nettoie, classifie, vectorise et sauvegarde."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptes.")

    try:
        #phase1: extraction du text brut (PyMuPDF)
        contenu = await file.read()
        texte_brut=""
        with pymupdf.open(stream=contenu, filetype="pdf") as doc:
            for page in doc:
                texte_brut += page.get_text()

        if not texte_brut.strip():
            raise HTTPException(status_code=400, detail="Le PDF semble vide ou illisible.")

        #phase2 : structuration via Gemini 1.5 pro
        text_propre = ai_service.nettoyer_et_structurer_cv(texte_brut)

        #phase3 : classification(Gemini 1.5 flash)
        secteur = ai_service.classifier_secteur(text_propre)

        #phase4: vectorisation(text-embedding-004)
        vecteur = ai_service.generer_embedding(text_propre)

        #phase 5: sauvgarde hybride(Methadonne + vecteur)
        database.save_cv(file.filename, secteur, text_propre, vecteur)

        return {
            "message": f"CV '{file.filename}' indexé avec succès.",
            "secteur_detecte": secteur
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Modele de donnes pour recevoir l'offre en json
class OffreRequest(BaseModel):
    description: str

#endpoint : recherche de candidats (Matching)
@app.post("/match", tags=["Pipeline Matching"])
async def match_cv(offre: OffreRequest):
    """Phase 3 : Analyse l'offre, applique le double filtre (SQL + Cosinus) et retourne le Top 20."""
    try:
        # Préparation de l'offre
        secteur_offre = ai_service.classifier_secteur(offre.description)
        vecteur_offre = ai_service.generer_embedding(offre.description)

        # Phase 3 : Le Matching Hybride (Filtre SQL strict -> Similarité Cosinus)
        resultats = database.chercher_matchs_hybride(secteur_offre, vecteur_offre)

        # Formatage de la réponse
        matchs = []
        for r in resultats:
            matchs.append({
                "nom_fichier": r[0],
                "score_similarite": round(float(r[2]) * 100, 2)
            })

        return {
            "secteur_offre": secteur_offre,
            "candidats_trouves": len(matchs),
            "top_matchs": matchs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Point de vérification
@app.get("/")
async def root():
    return {"status": "Talent-Match-Offre-Hybrid API est en ligne 🚀"}

