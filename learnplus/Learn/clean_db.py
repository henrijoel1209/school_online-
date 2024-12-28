import sqlite3

def clean_migrations():
    # Connexion à la base de données SQLite
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Supprimer l'entrée de migration problématique
        cursor.execute("DELETE FROM django_migrations WHERE app='student' AND name='0014_courseprogress_learningactivity_chapterprogress'")
        
        # Valider les changements
        conn.commit()
        print("Migration nettoyée avec succès")
        
    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == '__main__':
    clean_migrations()
