# Talent Match Offre - Backend Hybride 🚀

Ce projet est une API backend développée avec **FastAPI**, conçue pour mettre en relation (matcher) intelligemment des CVs et des offres d'emploi. 

L'originalité de ce projet réside dans son **approche hybride** : il combine un filtrage classique par base de données (SQL) avec une recherche sémantique avancée par intelligence artificielle (Vector Search via l'API Google Gemini et PostgreSQL avec l'extension `pgvector`).

---

## 🛠️ Stack Technologique
* **Framework Web** : FastAPI (Python)
* **Base de données** : PostgreSQL conteneurisé (Docker) avec l'extension **pgvector**
* **IA & Modèles (Groq et Google Gemini)** :
  * `openai/gpt-oss-20b` : Analyse et structuration de textes complexes + Classification rapide (déduction du secteur).
  * `text-embedding-004` : Création des embeddings (vecteurs mathématiques de 3072 dimensions).
* **Traitement PDF** : PyMuPDF (`pymupdf`)

---

## 🔄 Workflow & Architecture

Le système est divisé en deux grands flux (pipelines) qui communiquent entre les différents modules du code.

### 1. Pipeline d'ingestion d'un CV (Endpoint : `POST /upload-cv`)

Lorsqu'un utilisateur upload un CV au format PDF, voici ce qui se passe en coulisses :

1. **Extraction (PyMuPDF)** : Le contenu brut du PDF est lu et extrait sous forme de texte.
2. **Nettoyage (Gemini 1.5 Pro)** : La fonction `ai_service.nettoyer_et_structurer_cv()` prend le texte brut (souvent bruité) et le résume de manière structurée (Expériences, Compétences, etc.).
3. **Classification (Gemini 1.5 Flash)** : La fonction `ai_service.classifier_secteur()` lit le texte propre et détermine à quel secteur d'activité appartient le CV (ex: "Informatique", "Finance").
4. **Vectorisation (text-embedding-004)** : La fonction `ai_service.generer_embedding()` transforme le texte structuré en un vecteur de 3072 nombres flottants (l'empreinte sémantique du CV).
5. **Sauvegarde (SQL)** : La fonction `database.save_cv()` enregistre le tout dans la base PostgreSQL. 

### 2. Pipeline de Matching (Endpoint : `POST /match`)

Lorsqu'un recruteur soumet la description d'une offre d'emploi, l'API cherche les meilleurs candidats :

1. **Analyse de l'offre** :
   * Le secteur de l'offre est déduit avec `ai_service.classifier_secteur()`.
   * L'offre est convertie en vecteur avec `ai_service.generer_embedding()`.
2. **Recherche Hybride (`database.chercher_matchs_hybride()`)** :
   * C'est ici qu'intervient la puissance de l'approche hybride via PostgreSQL.
   * **Étape A (Filtre strict - SQL)** : `WHERE secteur = 'Informatique'`. Cela élimine immédiatement tous les CVs qui ne sont pas dans le bon secteur, économisant énormément de calcul.
   * **Étape B (Recherche sémantique - pgvector)** : `ORDER BY embedding <=> vecteur_offre`. Sur les CVs restants, la base de données calcule la **distance cosinus** (la similarité de sens) entre l'offre et chaque CV.
3. **Réponse** : L'API renvoie le Top des candidats (par défaut les 20 meilleurs ayant un score de similarité > 60%).

---

## 🗄️ Structure de la Base de données

La base de données (`cv_database`) contient une table principale `cvs` :

| Colonne | Type | Description |
| :--- | :--- | :--- |
| `id` | SERIAL (PK) | Identifiant unique du CV |
| `nom_fichier` | TEXT | Le nom du fichier PDF original |
| `secteur` | VARCHAR(50) | Secteur d'activité déduit par l'IA |
| `texte_propre` | TEXT | Le résumé structuré généré par Gemini Pro |
| `embedding` | VECTOR(3072) | Le vecteur sémantique utilisé pour le matching |

---

## 🚀 Lancement du projet en local

1. **Démarrer la base de données (Docker)** :
   ```bash
   docker-compose up -d
   ```
   *(La base tournera sur le port `5433` du localhost pour éviter les conflits avec d'éventuelles autres bases de données).*

2. **Activer l'environnement virtuel Python** :
   ```bash
   .\venv\Scripts\activate
   ```

3. **Lancer le serveur API** :
   ```bash
   uvicorn main:app --reload
   ```

4. **Accéder à la documentation interactive (Swagger UI)** :
   Rendez-vous sur [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) pour tester vos routes `/upload-cv` et `/match` directement depuis votre navigateur !
