from locust import HttpUser, task, between
from django.urls import reverse

class SchoolUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Exécuté lors du démarrage de chaque utilisateur"""
        # Connexion de l'utilisateur
        response = self.client.post("/school/login/", {
            "username": "testuser",
            "password": "testpass123"
        })
        if response.status_code != 200:
            print("Échec de la connexion")
    
    @task(2)
    def view_dashboard(self):
        """Test de performance du tableau de bord"""
        self.client.get("/student/")
    
    @task(3)
    def view_course_list(self):
        """Test de performance de la liste des cours"""
        self.client.get("/school/cours/")
    
    @task(1)
    def view_course_detail(self):
        """Test de performance du détail d'un cours"""
        # Supposons que nous avons un cours avec le slug 'test-course'
        self.client.get("/school/cours/test-course/")
    
    @task(1)
    def view_chapter_list(self):
        """Test de performance de la liste des chapitres"""
        self.client.get("/school/chapitres/")

class InstructorUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Exécuté lors du démarrage de chaque utilisateur"""
        # Connexion de l'instructeur
        response = self.client.post("/school/login/", {
            "username": "testinstructor",
            "password": "testpass123"
        })
        if response.status_code != 200:
            print("Échec de la connexion de l'instructeur")
    
    @task(2)
    def view_instructor_dashboard(self):
        """Test de performance du tableau de bord instructeur"""
        self.client.get("/instructor/")
    
    @task(1)
    def view_course_management(self):
        """Test de performance de la gestion des cours"""
        self.client.get("/instructor/courses/")
    
    @task(1)
    def add_course(self):
        """Test de performance de l'ajout de cours"""
        self.client.post("/instructor/courses/add/", {
            "titre": "Nouveau Cours Test",
            "description": "Description du cours de test",
            "chapitre": 1,
            "ordre": 1,
            "status": True
        })

class AdminUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        """Exécuté lors du démarrage de chaque utilisateur admin"""
        # Connexion de l'administrateur
        response = self.client.post("/school/login/", {
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            print("Échec de la connexion admin")
    
    @task
    def view_admin_dashboard(self):
        """Test de performance du tableau de bord admin"""
        self.client.get("/admin/")
    
    @task
    def view_user_list(self):
        """Test de performance de la liste des utilisateurs"""
        self.client.get("/admin/auth/user/")
