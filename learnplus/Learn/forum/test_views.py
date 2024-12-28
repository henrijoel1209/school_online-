import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertContains
from forum.models import Sujet, Reponse

pytestmark = pytest.mark.django_db

def test_liste_sujets_view(client, user, sujet):
    """Test la vue de liste des sujets"""
    client.force_login(user)
    
    # Test liste générale
    url = reverse('forum:liste_sujets')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'forum/liste_sujets.html')
    assertContains(response, 'Sujet Test')

    # Test liste par cours
    url = reverse('forum:liste_sujets_cours', args=[sujet.cours.id])
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'Sujet Test')

def test_detail_sujet_view(client, user, sujet, reponse):
    """Test la vue de détail d'un sujet"""
    client.force_login(user)
    url = reverse('forum:detail_sujet', args=[sujet.slug])
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'forum/detail_sujet.html')
    assertContains(response, 'Sujet Test')
    assertContains(response, 'Question test')
    assertContains(response, 'Réponse test')

def test_nouveau_sujet_view(client, user, cours):
    """Test la création d'un nouveau sujet"""
    client.force_login(user)
    
    # Test création dans le forum général
    url = reverse('forum:nouveau_sujet')
    data = {
        'titre': 'Nouveau Sujet',
        'question': 'Nouvelle Question'
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirection après succès
    assert len(Sujet.objects.filter(titre='Nouveau Sujet')) == 1

    # Test création dans un cours
    url = reverse('forum:nouveau_sujet_cours', args=[cours.id])
    data = {
        'titre': 'Nouveau Sujet Cours',
        'question': 'Nouvelle Question Cours',
        'cours': cours.id
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirection après succès
    assert len(Sujet.objects.filter(titre='Nouveau Sujet Cours')) == 1

def test_modifier_sujet_view(client, user, other_user, sujet):
    """Test la modification d'un sujet"""
    client.force_login(user)
    
    # Test modification par le propriétaire
    url = reverse('forum:modifier_sujet', args=[sujet.slug])
    data = {
        'titre': 'Sujet Modifié',
        'question': 'Question modifiée',
        'cours': sujet.cours.id
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirection après succès
    sujet.refresh_from_db()
    assert sujet.titre == 'Sujet Modifié'

    # Test modification par un autre utilisateur (doit échouer)
    client.force_login(other_user)
    response = client.post(url, data)
    assert response.status_code == 404

def test_supprimer_sujet_view(client, user, other_user, sujet, cours):
    """Test la suppression d'un sujet"""
    client.force_login(user)
    
    # Test suppression par le propriétaire
    url = reverse('forum:supprimer_sujet', args=[sujet.slug])
    response = client.post(url)
    assert response.status_code == 302  # Redirection après succès
    sujet.refresh_from_db()
    assert not sujet.status

    # Test suppression par un autre utilisateur (doit échouer)
    client.force_login(other_user)
    new_sujet = Sujet.objects.create(
        user=user,
        cours=cours,
        titre="Autre Sujet Test",
        question="Question test"
    )
    url = reverse('forum:supprimer_sujet', args=[new_sujet.slug])
    response = client.post(url)
    assert response.status_code == 404

def test_reponse_crud(client, user, sujet):
    """Test le CRUD des réponses"""
    client.force_login(user)
    
    # Test création d'une réponse
    url = reverse('forum:detail_sujet', args=[sujet.slug])
    data = {'reponse': 'Nouvelle réponse'}
    response = client.post(url, data)
    assert response.status_code == 302  # Redirection après succès
    assert len(Reponse.objects.filter(reponse='Nouvelle réponse')) == 1

    # Test modification d'une réponse
    reponse = Reponse.objects.get(reponse='Nouvelle réponse')
    url = reverse('forum:modifier_reponse', args=[reponse.id])
    data = {'reponse': 'Réponse modifiée'}
    response = client.post(url, data)
    assert response.status_code == 302  # Redirection après succès
    reponse.refresh_from_db()
    assert reponse.reponse == 'Réponse modifiée'

    # Test suppression d'une réponse
    url = reverse('forum:supprimer_reponse', args=[reponse.id])
    response = client.post(url)
    assert response.status_code == 302  # Redirection après succès
    reponse.refresh_from_db()
    assert not reponse.status

def test_pagination(client, user, cours):
    """Test la pagination des sujets"""
    client.force_login(user)
    
    # Création de 15 sujets
    for i in range(15):
        Sujet.objects.create(
            user=user,
            cours=cours,
            titre=f"Sujet Test {i}",
            question=f"Question test {i}"
        )

    # Test première page
    url = reverse('forum:liste_sujets')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['sujets_page']) == 10

    # Test deuxième page
    response = client.get(f"{url}?page=2")
    assert response.status_code == 200
    assert len(response.context['sujets_page']) > 0

def test_authentication_required(client):
    """Test que les vues nécessitent une authentification"""
    urls = [
        reverse('forum:liste_sujets'),
        reverse('forum:nouveau_sujet'),
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == 302  # Redirection vers login
