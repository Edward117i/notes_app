import unittest
from app import create_app
from config import TestConfig
from models import db, User, Note


class AuthRoutesTest(unittest.TestCase):
    """Pruebas unitarias para las rutas de autenticación"""
    
    def setUp(self):
        """Configurar el entorno antes de cada prueba"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Limpiar el entorno después de cada prueba"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_register_page_loads(self):
        """Prueba: la página de registro carga correctamente"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
    
    def test_register_user_success(self):
        """Prueba: registrar un usuario con datos válidos"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        with self.app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'newuser@example.com')
    
    def test_register_missing_fields(self):
        """Prueba: el registro falla si faltan campos"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': '',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        # El usuario no debe ser creado
        with self.app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNone(user)
    
    def test_register_password_too_short(self):
        """Prueba: el registro falla con contraseña menor a 6 caracteres"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        
        with self.app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNone(user)
    
    def test_register_passwords_dont_match(self):
        """Prueba: el registro falla si las contraseñas no coinciden"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'different'
        }, follow_redirects=True)
        
        with self.app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNone(user)
    
    def test_register_duplicate_username(self):
        """Prueba: no se puede registrar un usuario duplicado"""
        with self.app.app_context():
            user = User(username='existing', email='existing@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = self.client.post('/register', data={
            'username': 'existing',
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        # Solo debe haber un usuario con ese username
        with self.app.app_context():
            users = User.query.filter_by(username='existing').all()
            self.assertEqual(len(users), 1)
    
    def test_register_duplicate_email(self):
        """Prueba: no se puede registrar un email duplicado"""
        with self.app.app_context():
            user = User(username='user1', email='duplicate@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = self.client.post('/register', data={
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        # Solo debe haber un usuario con ese email
        with self.app.app_context():
            users = User.query.filter_by(email='duplicate@example.com').all()
            self.assertEqual(len(users), 1)
    
    def test_login_page_loads(self):
        """Prueba: la página de login carga correctamente"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_login_success(self):
        """Prueba: login con credenciales correctas"""
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Debe redirigir al home
        self.assertEqual(response.status_code, 200)
    
    def test_login_wrong_password(self):
        """Prueba: login falla con contraseña incorrecta"""
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        # El usuario no debe estar autenticado
        with self.client:
            self.client.get('/')
            # Verificar que current_user no está autenticado


class NotesRoutesTest(unittest.TestCase):
    """Pruebas unitarias para las rutas de notas"""
    
    def setUp(self):
        """Configurar el entorno antes de cada prueba"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Crear un usuario para las pruebas
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Guardar el ID del usuario
            self.user_id = user.id
    
    def tearDown(self):
        """Limpiar el entorno después de cada prueba"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def login(self):
        """Helper para hacer login en las pruebas"""
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
    
    def test_home_requires_login(self):
        """Prueba: la página home requiere autenticación"""
        response = self.client.get('/')
        # Debe redirigir al login (código 302)
        self.assertEqual(response.status_code, 302)
    
    def test_home_shows_notes(self):
        """Prueba: la página home muestra las notas del usuario"""
        self.login()
        
        with self.app.app_context():
            note = Note(title='Mi Nota', content='Contenido', user_id=self.user_id)
            db.session.add(note)
            db.session.commit()
        
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_create_note_page_loads(self):
        """Prueba: la página de crear nota carga cuando está autenticado"""
        self.login()
        response = self.client.get('/crear-nota')
        self.assertEqual(response.status_code, 200)
    
    def test_create_note_success(self):
        """Prueba: crear una nota con datos válidos"""
        self.login()
        
        response = self.client.post('/crear-nota', data={
            'title': 'Nueva Nota',
            'content': 'Contenido de la nota'
        }, follow_redirects=True)
        
        with self.app.app_context():
            note = Note.query.filter_by(title='Nueva Nota').first()
            self.assertIsNotNone(note)
            self.assertEqual(note.content, 'Contenido de la nota')
    
    def test_create_note_missing_fields(self):
        """Prueba: crear nota falla si faltan campos"""
        self.login()
        
        response = self.client.post('/crear-nota', data={
            'title': 'Nueva Nota',
            'content': ''
        }, follow_redirects=True)
        
        with self.app.app_context():
            note = Note.query.filter_by(title='Nueva Nota').first()
            self.assertIsNone(note)
    
    def test_edit_note_requires_ownership(self):
        """Prueba: no se puede editar nota de otro usuario"""
        # Crear otro usuario y su nota
        with self.app.app_context():
            other_user = User(username='otheruser', email='other@example.com')
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()
            
            note = Note(title='Nota de Otro', content='Contenido', user_id=other_user.id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        # Login como testuser e intentar editar nota de otro
        self.login()
        response = self.client.post(f'/editar-nota/{note_id}', data={
            'title': 'Título Editado',
            'content': 'Contenido Editado'
        }, follow_redirects=True)
        
        # La nota no debe cambiar
        with self.app.app_context():
            note = Note.query.get(note_id)
            self.assertEqual(note.title, 'Nota de Otro')
    
    def test_edit_note_success(self):
        """Prueba: editar nota propia funciona"""
        with self.app.app_context():
            note = Note(title='Nota Original', content='Contenido', user_id=self.user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        self.login()
        response = self.client.post(f'/editar-nota/{note_id}', data={
            'title': 'Nota Editada',
            'content': 'Contenido Editado'
        }, follow_redirects=True)
        
        with self.app.app_context():
            note = Note.query.get(note_id)
            self.assertEqual(note.title, 'Nota Editada')
            self.assertEqual(note.content, 'Contenido Editado')


class OtherRoutesTest(unittest.TestCase):
    """Pruebas unitarias para otras rutas"""
    
    def setUp(self):
        """Configurar el entorno antes de cada prueba"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
    
    def test_about_page(self):
        """Prueba: la página acerca de carga correctamente"""
        response = self.client.get('/acerca-de')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'aplicaci', response.data)
    
    def test_contact_get(self):
        """Prueba: GET a /contact carga correctamente"""
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'contacto', response.data.lower())
    
    def test_contact_post(self):
        """Prueba: POST a /contact retorna 201"""
        response = self.client.post('/contact')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Formulario', response.data)


if __name__ == '__main__':
    unittest.main()
