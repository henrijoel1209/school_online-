import pytest
from django.contrib.auth.models import User
from school.models import Niveau, Classe, Matiere, Chapitre, Cours, Filiere
from forum.models import Sujet, Reponse

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )

@pytest.fixture
def other_user():
    return User.objects.create_user(
        username='otheruser',
        password='testpass123'
    )

@pytest.fixture
def niveau():
    return Niveau.objects.create(nom="Niveau Test")

@pytest.fixture
def filiere():
    return Filiere.objects.create(nom="Filière Test")

@pytest.fixture
def classe(niveau, filiere):
    return Classe.objects.create(
        numeroClasse=1,
        niveau=niveau,
        filiere=filiere
    )

@pytest.fixture
def matiere():
    return Matiere.objects.create(nom="Matière Test")

@pytest.fixture
def chapitre(classe, matiere):
    return Chapitre.objects.create(
        titre="Chapitre Test",
        description="Description test",
        classe=classe,
        matiere=matiere
    )

@pytest.fixture
def cours(chapitre):
    return Cours.objects.create(
        titre="Cours Test",
        description="Description test",
        chapitre=chapitre
    )

@pytest.fixture
def sujet(user, cours):
    return Sujet.objects.create(
        user=user,
        cours=cours,
        titre="Sujet Test",
        question="Question test"
    )

@pytest.fixture
def reponse(user, sujet):
    return Reponse.objects.create(
        user=user,
        sujet=sujet,
        reponse="Réponse test"
    )
