import pytest
from django.contrib.auth.models import User
from school.models import Filiere, Niveau, Classe, Matiere, Chapitre, Cours
from student.models import Student
from instructor.models import Instructor

@pytest.fixture
def create_user():
    def make_user(username, password='test12345', is_staff=False):
        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=is_staff
        )
        return user
    return make_user

@pytest.fixture
def create_student(create_user):
    def make_student(username='teststudent'):
        user = create_user(username)
        student = Student.objects.create(user=user)
        return student
    return make_student

@pytest.fixture
def create_instructor(create_user):
    def make_instructor(username='testinstructor'):
        user = create_user(username)
        instructor = Instructor.objects.create(user=user)
        return instructor
    return make_instructor

@pytest.fixture
def create_course_structure():
    def make_structure():
        filiere = Filiere.objects.create(nom='Test Filiere')
        niveau = Niveau.objects.create(nom='Test Niveau')
        classe = Classe.objects.create(
            niveau=niveau,
            numeroClasse=1,
            filiere=filiere
        )
        matiere = Matiere.objects.create(nom='Test Matiere')
        chapitre = Chapitre.objects.create(
            matiere=matiere,
            classe=classe,
            titre='Test Chapitre'
        )
        cours = Cours.objects.create(
            titre='Test Cours',
            chapitre=chapitre
        )
        return {
            'filiere': filiere,
            'niveau': niveau,
            'classe': classe,
            'matiere': matiere,
            'chapitre': chapitre,
            'cours': cours
        }
    return make_structure
