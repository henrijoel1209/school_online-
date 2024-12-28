from django.db import models
from django.contrib.auth.models import User
from school.models import Filiere, Niveau, Classe, Matiere
from student.models import Student
from instructor.models import Instructor
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class AdminManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_manager')
    photo = models.ImageField(upload_to='images/Admin', null=True, blank=True)
    contact = models.CharField(max_length=255)
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Admin Manager'
        verbose_name_plural = 'Admin Managers'

    def __str__(self):
        return f"Admin: {self.user.username}"

    def create_filiere(self, nom, description=None, responsable=None):
        """Créer une nouvelle filière"""
        return Filiere.objects.create(
            nom=nom,
            description=description or f"Description de la filière {nom}",
            responsable=responsable
        )

    def create_niveau(self, nom):
        """Créer un nouveau niveau"""
        return Niveau.objects.create(
            nom=nom
        )

    def create_classe(self, niveau, numero_classe, filiere=None):
        """Créer une nouvelle classe"""
        return Classe.objects.create(
            niveau=niveau,
            numeroClasse=numero_classe,
            filiere=filiere
        )

    def create_matiere(self, nom, description=None, image=None):
        """Créer une nouvelle matière"""
        return Matiere.objects.create(
            nom=nom,
            description=description or f"Description de la matière {nom}",
            image=image
        )

    def create_student(self, username, email, password, classe, **extra_fields):
        """Créer un nouvel étudiant"""
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        
        # Créer le profil étudiant
        return Student.objects.create(
            user=user,
            classe=classe
        )

    def create_instructor(self, username, email, password, contact, adresse, **extra_fields):
        """Créer un nouvel enseignant"""
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        
        # Créer le profil enseignant
        return Instructor.objects.create(
            user=user,
            contact=contact,
            adresse=adresse
        )

    def assign_instructor_to_class(self, instructor, classe):
        """Assigner un enseignant à une classe"""
        instructor.classe = classe
        instructor.save()

    def assign_instructor_to_matiere(self, instructor, matiere):
        """Assigner une matière à un enseignant"""
        instructor.matieres.add(matiere)

    def change_student_class(self, student, new_classe):
        """Changer la classe d'un étudiant"""
        student.classe = new_classe
        student.save()

    def bulk_create_students(self, student_data_list):
        """Créer plusieurs étudiants à la fois"""
        created_students = []
        for data in student_data_list:
            try:
                student = self.create_student(**data)
                created_students.append(student)
            except Exception as e:
                # Log l'erreur mais continue avec les autres étudiants
                print(f"Erreur lors de la création de l'étudiant {data.get('username')}: {str(e)}")
        return created_students

    def get_class_statistics(self, classe):
        """Obtenir des statistiques pour une classe"""
        students = Student.objects.filter(classe=classe)
        return {
            'total_students': students.count(),
            'active_students': students.filter(status=True).count(),
            'average_score': students.aggregate(models.Avg('studentresponse__score'))['studentresponse__score__avg'] or 0
        }
