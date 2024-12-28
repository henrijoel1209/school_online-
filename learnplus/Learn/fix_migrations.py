import os
import django
from django.db import connection

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Learn.settings')
django.setup()

def fix_migrations():
    # 1. Supprimer le fichier de migration
    migration_file = 'student/migrations/0014_courseprogress_learningactivity_chapterprogress.py'
    if os.path.exists(migration_file):
        os.remove(migration_file)
        print(f"Fichier supprimé : {migration_file}")
    
    # 2. Nettoyer la table des migrations
    cursor = connection.cursor()
    cursor.execute("DELETE FROM django_migrations WHERE app='student' AND name='0014_courseprogress_learningactivity_chapterprogress';")
    connection.commit()
    print("Entrée de migration supprimée de la base de données")

if __name__ == '__main__':
    fix_migrations()
