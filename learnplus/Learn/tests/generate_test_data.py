from django.contrib.auth.models import User
from school.models import Matiere, Chapitre, Cours
from instructor.models import Instructor
from student.models import Student

def create_test_data():
    # Création des utilisateurs de test
    test_user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='testuser@example.com'
    )
    Student.objects.create(user=test_user)

    test_instructor = User.objects.create_user(
        username='testinstructor',
        password='testpass123',
        email='instructor@example.com'
    )
    Instructor.objects.create(user=test_instructor)

    admin_user = User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@example.com'
    )

    # Création des matières
    for i in range(5):
        matiere = Matiere.objects.create(
            nom=f'Matière Test {i}',
            description=f'Description de la matière {i}',
            status=True
        )

        # Création des chapitres pour chaque matière
        for j in range(3):
            chapitre = Chapitre.objects.create(
                titre=f'Chapitre {j} - Matière {i}',
                matiere=matiere,
                description=f'Description du chapitre {j}',
                ordre=j+1,
                status=True
            )

            # Création des cours pour chaque chapitre
            for k in range(4):
                Cours.objects.create(
                    titre=f'Cours {k} - Chapitre {j}',
                    chapitre=chapitre,
                    description=f'Description du cours {k}',
                    contenu=f'Contenu du cours {k}',
                    ordre=k+1,
                    status=True
                )

if __name__ == '__main__':
    create_test_data()
