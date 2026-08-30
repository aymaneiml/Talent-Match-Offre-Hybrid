# Connexion DB et requêtes SQL (pgvector)
import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Établit la connexion à PostgreSQL et enregistre pgvector."""
    db_host = os.getenv("DB_HOST","localhost")
    db_port=os.getenv("DB_PORT","5432")

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user="admin",
        password="password123",
        dbname="cv_database"
    )
    # Très important : il faut dire à psycopg2 qu'on utilise des vecteurs
    try:
        register_vector(conn)
    except psycopg2.ProgrammingError:
        pass # L'extension n'est pas encore créée (normal lors du premier lancement)
        
    return conn

def initialiser_base():
    """Configure la base de données de A à Z avec la table hybride."""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1. Activer l'extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        # 2. Créer la table avec la colonne 'secteur' et 'embedding' (3072 pour Gemini text-embedding-004)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cvs (
                id SERIAL PRIMARY KEY,
                nom_fichier TEXT,
                secteur VARCHAR(50), 
                texte_propre TEXT,
                embedding vector(3072)
            );
        """)
        conn.commit() #alide les modifications
        print("[OK] Base de données initialisée avec succès.")
        print("Tables créées : cvs")

    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'initialisation : {e}")
        conn.rollback() #annule les modifications de la transaction en cours.
    
    finally:
        cur.close()
        conn.close()

def save_cv(nom_fichier: str, secteur: str, text_propre: str, vecteur: list[float]):
    """Sauvegarde le CV avec ses métadonnées et son vecteur mathématique."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO cvs (nom_fichier, secteur, texte_propre, embedding)
            VALUES (%s, %s, %s, %s)
        """, (nom_fichier, secteur, text_propre, vecteur))
        
        conn.commit()
        print(f"[OK] CV '{nom_fichier}' sauvegarde avec succes dans le secteur '{secteur}'.")
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la sauvegarde : {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def chercher_matchs_hybride(secteur_offre:str, vecteur_offre: list[float], limit: int = 20, seuil: float=0.60):
    """
    Le cœur de l'architecture :
    1. Le filtre WHERE élimine les mauvais secteurs.
    2. Le filtre <=> calcule la proximité sémantique sur le reste.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # On passe le vecteur 3 fois : pour le calcul du score, pour la condition WHERE, et pour le tri (ORDER BY)
        cur.execute("""
            SELECT nom_fichier, texte_propre, 1 - (embedding <=> %s::vector) AS score
            FROM cvs
            WHERE secteur = %s AND 1 - (embedding <=> %s::vector) >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (vecteur_offre, secteur_offre, vecteur_offre, seuil, vecteur_offre, limit))

        resultats = cur.fetchall()
        return resultats
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        return []
    finally:
        cur.close()
        conn.close()
        
# --- Zone de test local ---
if __name__ == "__main__":
    initialiser_base()