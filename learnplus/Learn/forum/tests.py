from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Sujet, Reponse
from school.models import Cours, Chapitre, Matiere, Classe, Niveau, Filiere

class ForumTests(TestCase):
    def setUp(self):
        # Création d'un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        # Création d'un autre utilisateur pour tester les permissions
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        # Création des objets nécessaires pour le cours
        self.niveau = Niveau.objects.create(nom="Niveau Test")
        self.filiere = Filiere.objects.create(nom="Filière Test")
        self.classe = Classe.objects.create(
            numeroClasse=1,
            niveau=self.niveau,
            filiere=self.filiere
        )
        self.matiere = Matiere.objects.create(nom="Matière Test")
        self.chapitre = Chapitre.objects.create(
            titre="Chapitre Test",
            description="Description test",
            classe=self.classe,
            matiere=self.matiere
        )
        self.cours = Cours.objects.create(
            titre="Cours Test",
            description="Description test",
            chapitre=self.chapitre
        )

        # Création d'un sujet de test
        self.sujet = Sujet.objects.create(
            user=self.user,
            cours=self.cours,
            titre="Sujet Test",
            question="Question test"
        )

        # Création d'une réponse de test
        self.reponse = Reponse.objects.create(
            user=self.user,
            sujet=self.sujet,
            reponse="Réponse test"
        )

    def test_liste_sujets_view(self):
        """Test la vue de liste des sujets"""
        # Test liste générale
        response = self.client.get(reverse('forum:liste_sujets'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/liste_sujets.html')
        self.assertContains(response, 'Sujet Test')

        # Test liste par cours
        response = self.client.get(reverse('forum:liste_sujets_cours', args=[self.cours.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sujet Test')

    def test_detail_sujet_view(self):
        """Test la vue de détail d'un sujet"""
        response = self.client.get(reverse('forum:detail_sujet', args=[self.sujet.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/detail_sujet.html')
        self.assertContains(response, 'Sujet Test')
        self.assertContains(response, 'Question test')
        self.assertContains(response, 'Réponse test')

    def test_nouveau_sujet_view(self):
        """Test la création d'un nouveau sujet"""
        # Test création dans le forum général
        response = self.client.post(reverse('forum:nouveau_sujet'), {
            'titre': 'Nouveau Sujet',
            'question': 'Nouvelle Question'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertEqual(Sujet.objects.filter(titre='Nouveau Sujet').count(), 1)

        # Test création dans un cours
        response = self.client.post(reverse('forum:nouveau_sujet_cours', args=[self.cours.id]), {
            'titre': 'Nouveau Sujet Cours',
            'question': 'Nouvelle Question Cours',
            'cours': self.cours.id
        })
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertEqual(Sujet.objects.filter(titre='Nouveau Sujet Cours').count(), 1)

    def test_modifier_sujet_view(self):
        """Test la modification d'un sujet"""
        # Test modification par le propriétaire
        response = self.client.post(
            reverse('forum:modifier_sujet', args=[self.sujet.slug]),
            {
                'titre': 'Sujet Modifié',
                'question': 'Question modifiée',
                'cours': self.cours.id
            }
        )
        self.sujet.refresh_from_db()
        self.assertEqual(self.sujet.titre, 'Sujet Modifié')

        # Test modification par un autre utilisateur (doit échouer)
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.post(
            reverse('forum:modifier_sujet', args=[self.sujet.slug]),
            {
                'titre': 'Sujet Modifié Par Autre',
                'question': 'Question modifiée par autre',
                'cours': self.cours.id
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_supprimer_sujet_view(self):
        """Test la suppression d'un sujet"""
        # Test suppression par le propriétaire
        response = self.client.post(reverse('forum:supprimer_sujet', args=[self.sujet.slug]))
        self.sujet.refresh_from_db()
        self.assertFalse(self.sujet.status)

        # Test suppression par un autre utilisateur (doit échouer)
        self.client.login(username='otheruser', password='testpass123')
        new_sujet = Sujet.objects.create(
            user=self.user,
            cours=self.cours,
            titre="Autre Sujet Test",
            question="Question test"
        )
        response = self.client.post(reverse('forum:supprimer_sujet', args=[new_sujet.slug]))
        self.assertEqual(response.status_code, 404)

    def test_reponse_crud(self):
        """Test le CRUD des réponses"""
        # Test création d'une réponse
        response = self.client.post(
            reverse('forum:detail_sujet', args=[self.sujet.slug]),
            {'reponse': 'Nouvelle réponse'}
        )
        self.assertEqual(Reponse.objects.filter(reponse='Nouvelle réponse').count(), 1)

        # Test modification d'une réponse
        reponse = Reponse.objects.get(reponse='Nouvelle réponse')
        response = self.client.post(
            reverse('forum:modifier_reponse', args=[reponse.id]),
            {'reponse': 'Réponse modifiée'}
        )
        reponse.refresh_from_db()
        self.assertEqual(reponse.reponse, 'Réponse modifiée')

        # Test suppression d'une réponse
        response = self.client.post(reverse('forum:supprimer_reponse', args=[reponse.id]))
        reponse.refresh_from_db()
        self.assertFalse(reponse.status)

    def test_pagination(self):
        """Test la pagination des sujets"""
        # Création de 15 sujets supplémentaires
        for i in range(15):
            Sujet.objects.create(
                user=self.user,
                cours=self.cours,
                titre=f"Sujet Test {i}",
                question=f"Question test {i}"
            )

        # Test première page
        response = self.client.get(reverse('forum:liste_sujets'))
        self.assertEqual(len(response.context['sujets_page']), 10)

        # Test deuxième page
        response = self.client.get(f"{reverse('forum:liste_sujets')}?page=2")
        self.assertTrue(len(response.context['sujets_page']) > 0)

    def test_authentication_required(self):
        """Test que les vues nécessitent une authentification"""
        self.client.logout()
        urls = [
            reverse('forum:liste_sujets'),
            reverse('forum:detail_sujet', args=[self.sujet.slug]),
            reverse('forum:nouveau_sujet'),
            reverse('forum:modifier_sujet', args=[self.sujet.slug]),
            reverse('forum:supprimer_sujet', args=[self.sujet.slug]),
            reverse('forum:modifier_reponse', args=[self.reponse.id]),
            reverse('forum:supprimer_reponse', args=[self.reponse.id])
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirection vers login
