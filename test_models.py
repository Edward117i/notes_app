import unittest
from app import create_app
from config import TestConfig
from models import db, User, Note


class UserModelTest(unittest.TestCase):
    """Pruebas unitarias para el modelo User"""
    
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
    
    def test_create_user(self):
        """Prueba: crear un usuario correctamente"""
        with self.app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            
            db.session.add(user)
            db.session.commit()
            
            saved_user = User.query.filter_by(username="testuser").first()
            
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.username, "testuser")
            self.assertEqual(saved_user.email, "test@example.com")
    
    def test_password_hashing(self):
        """Prueba: la contraseña se hashea correctamente"""
        with self.app.app_context():
            user = User(username="hashtest", email="hash@example.com")
            user.set_password("mypassword")
            
            # La contraseña hasheada no debe ser igual a la original
            self.assertNotEqual(user.password_hash, "mypassword")
            # Pero el hash debe ser válido
            self.assertTrue(user.check_password("mypassword"))
    
    def test_password_verification(self):
        """Prueba: verificar contraseña funciona correctamente"""
        with self.app.app_context():
            user = User(username="verifytest", email="verify@example.com")
            user.set_password("correctpassword")
            
            # Contraseña correcta
            self.assertTrue(user.check_password("correctpassword"))
            # Contraseña incorrecta
            self.assertFalse(user.check_password("wrongpassword"))
    
    def test_user_unique_username(self):
        """Prueba: los usernames deben ser únicos"""
        with self.app.app_context():
            user1 = User(username="duplicate", email="email1@example.com")
            user1.set_password("password")
            db.session.add(user1)
            db.session.commit()
            
            # Intentar crear otro usuario con el mismo username
            user2 = User(username="duplicate", email="email2@example.com")
            user2.set_password("password")
            db.session.add(user2)
            
            # Debe lanzar una excepción
            with self.assertRaises(Exception):
                db.session.commit()
    
    def test_user_unique_email(self):
        """Prueba: los emails deben ser únicos"""
        with self.app.app_context():
            user1 = User(username="user1", email="duplicate@example.com")
            user1.set_password("password")
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(username="user2", email="duplicate@example.com")
            user2.set_password("password")
            db.session.add(user2)
            
            with self.assertRaises(Exception):
                db.session.commit()


class NoteModelTest(unittest.TestCase):
    """Pruebas unitarias para el modelo Note"""
    
    def setUp(self):
        """Configurar el entorno antes de cada prueba"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Crear un usuario para las pruebas
            user = User(username="noteuser", email="noteuser@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            # Guardar el ID del usuario para usarlo después
            self.user_id = user.id
            self.user = user
    
    def tearDown(self):
        """Limpiar el entorno después de cada prueba"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_create_note(self):
        """Prueba: crear una nota correctamente"""
        with self.app.app_context():
            note = Note(
                title="Título de prueba",
                content="Contenido de prueba",
                user_id=self.user_id
            )
            
            db.session.add(note)
            db.session.commit()
            
            saved_note = Note.query.first()
            
            self.assertIsNotNone(saved_note)
            self.assertEqual(saved_note.title, "Título de prueba")
            self.assertEqual(saved_note.content, "Contenido de prueba")
            self.assertEqual(saved_note.user_id, self.user_id)
    
    def test_note_user_relationship(self):
        """Prueba: la relación entre nota y usuario funciona"""
        with self.app.app_context():
            note = Note(
                title="Nota de relación",
                content="Contenido",
                user_id=self.user_id
            )
            
            db.session.add(note)
            db.session.commit()
            
            # Verificar que podemos acceder al usuario desde la nota
            user = User.query.get(self.user_id)
            self.assertEqual(note.author.username, "noteuser")
            # Verificar que podemos acceder a las notas desde el usuario
            self.assertEqual(len(user.notes), 1)
            self.assertEqual(user.notes[0].title, "Nota de relación")
    
    def test_multiple_notes_per_user(self):
        """Prueba: un usuario puede tener múltiples notas"""
        with self.app.app_context():
            note1 = Note(title="Nota 1", content="Contenido 1", user_id=self.user_id)
            note2 = Note(title="Nota 2", content="Contenido 2", user_id=self.user_id)
            note3 = Note(title="Nota 3", content="Contenido 3", user_id=self.user_id)
            
            db.session.add_all([note1, note2, note3])
            db.session.commit()
            
            user_notes = Note.query.filter_by(user_id=self.user_id).all()
            
            self.assertEqual(len(user_notes), 3)
    
    def test_note_repr(self):
        """Prueba: la representación de la nota es correcta"""
        with self.app.app_context():
            note = Note(title="Test Note", content="Content", user_id=self.user_id)
            db.session.add(note)
            db.session.commit()
            
            # Verificar la representación
            self.assertEqual(repr(note), f"<Note {note.id}: Test Note>")


if __name__ == '__main__':
    unittest.main()
