import json
import unittest
from app import create_app
from config import TestConfig
from models import db, User, Note


class APIRoutesTest(unittest.TestCase):
    """Pruebas unitarias para la API RESTful"""
    
    def setUp(self):
        """Configurar el entorno antes de cada prueba"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Crear usuario con API key
            user = User(username='apiuser', email='api@example.com')
            user.set_password('password123')
            user.generate_api_key()
            db.session.add(user)
            db.session.commit()
            
            self.user_id = user.id
            self.api_key = user.api_key
            
            # Crear otro usuario para tests de permisos
            other_user = User(username='otheruser', email='other@example.com')
            other_user.set_password('password123')
            other_user.generate_api_key()
            db.session.add(other_user)
            db.session.commit()
            
            self.other_user_id = other_user.id
            self.other_api_key = other_user.api_key
    
    def tearDown(self):
        """Limpiar el entorno después de cada prueba"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def get_headers(self, api_key=None):
        """Helper para construir headers de autenticación"""
        return {
            'X-API-Key': api_key or self.api_key,
            'Content-Type': 'application/json'
        }
    
    # ========================
    # Tests de Autenticación
    # ========================
    
    def test_api_requires_key(self):
        """Prueba: la API requiere X-API-Key"""
        response = self.client.get('/api/notes')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
    
    def test_api_invalid_key(self):
        """Prueba: rechaza API keys inválidas"""
        response = self.client.get('/api/notes', headers={
            'X-API-Key': 'invalid-key-12345'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_api_valid_key(self):
        """Prueba: acepta API keys válidas"""
        response = self.client.get('/api/notes', headers=self.get_headers())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    # ========================
    # Tests de Listar Notas
    # ========================
    
    def test_list_notes_empty(self):
        """Prueba: listar notas cuando no hay ninguna"""
        response = self.client.get('/api/notes', headers=self.get_headers())
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 0)
        self.assertEqual(data['pagination']['total'], 0)
    
    def test_list_notes_with_data(self):
        """Prueba: listar notas devuelve las notas del usuario"""
        with self.app.app_context():
            note = Note(title='Test', content='Contenido', user_id=self.user_id)
            db.session.add(note)
            db.session.commit()
        
        response = self.client.get('/api/notes', headers=self.get_headers())
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['title'], 'Test')
    
    def test_list_notes_only_own(self):
        """Prueba: solo muestra notas del usuario autenticado"""
        with self.app.app_context():
            # Nota del otro usuario
            note = Note(title='Nota Ajena', content='Contenido', user_id=self.other_user_id)
            db.session.add(note)
            db.session.commit()
        
        response = self.client.get('/api/notes', headers=self.get_headers())
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 0)
    
    def test_list_notes_pagination(self):
        """Prueba: paginación funciona correctamente"""
        with self.app.app_context():
            for i in range(15):
                note = Note(title=f'Nota {i}', content=f'Contenido {i}', user_id=self.user_id)
                db.session.add(note)
            db.session.commit()
        
        # Primera página
        response = self.client.get('/api/notes?page=1&per_page=9', headers=self.get_headers())
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 9)
        self.assertTrue(data['pagination']['has_next'])
        self.assertFalse(data['pagination']['has_prev'])
        
        # Segunda página
        response = self.client.get('/api/notes?page=2&per_page=9', headers=self.get_headers())
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 6)
        self.assertFalse(data['pagination']['has_next'])
        self.assertTrue(data['pagination']['has_prev'])
    
    # ========================
    # Tests de Obtener Nota
    # ========================
    
    def test_get_note_success(self):
        """Prueba: obtener nota por ID"""
        with self.app.app_context():
            note = Note(title='Mi Nota', content='Detalle', user_id=self.user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        response = self.client.get(f'/api/notes/{note_id}', headers=self.get_headers())
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['title'], 'Mi Nota')
    
    def test_get_note_not_found(self):
        """Prueba: nota inexistente retorna 404"""
        response = self.client.get('/api/notes/999', headers=self.get_headers())
        self.assertEqual(response.status_code, 404)
    
    def test_get_note_forbidden(self):
        """Prueba: no se puede ver nota de otro usuario"""
        with self.app.app_context():
            note = Note(title='Nota Ajena', content='Secreto', user_id=self.other_user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        response = self.client.get(f'/api/notes/{note_id}', headers=self.get_headers())
        self.assertEqual(response.status_code, 403)
    
    # ========================
    # Tests de Crear Nota
    # ========================
    
    def test_create_note_success(self):
        """Prueba: crear nota con datos válidos"""
        response = self.client.post('/api/notes',
            headers=self.get_headers(),
            data=json.dumps({'title': 'Nueva Nota', 'content': 'Contenido nuevo'}))
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['title'], 'Nueva Nota')
    
    def test_create_note_missing_fields(self):
        """Prueba: crear nota sin campos requeridos"""
        response = self.client.post('/api/notes',
            headers=self.get_headers(),
            data=json.dumps({'title': 'Solo Título'}))
        
        self.assertEqual(response.status_code, 400)
    
    def test_create_note_no_body(self):
        """Prueba: crear nota sin cuerpo JSON retorna error"""
        response = self.client.post('/api/notes',
            headers={'X-API-Key': self.api_key})
        
        # Flask retorna 415 (Unsupported Media Type) cuando no se envía Content-Type: application/json
        self.assertIn(response.status_code, [400, 415])
    
    def test_create_note_title_too_long(self):
        """Prueba: título demasiado largo"""
        response = self.client.post('/api/notes',
            headers=self.get_headers(),
            data=json.dumps({'title': 'A' * 51, 'content': 'Contenido'}))
        
        self.assertEqual(response.status_code, 400)
    
    # ========================
    # Tests de Actualizar Nota
    # ========================
    
    def test_update_note_success(self):
        """Prueba: actualizar nota propia"""
        with self.app.app_context():
            note = Note(title='Original', content='Contenido', user_id=self.user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        response = self.client.put(f'/api/notes/{note_id}',
            headers=self.get_headers(),
            data=json.dumps({'title': 'Editada', 'content': 'Nuevo contenido'}))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['title'], 'Editada')
    
    def test_update_note_forbidden(self):
        """Prueba: no se puede actualizar nota de otro usuario"""
        with self.app.app_context():
            note = Note(title='Ajena', content='Contenido', user_id=self.other_user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        response = self.client.put(f'/api/notes/{note_id}',
            headers=self.get_headers(),
            data=json.dumps({'title': 'Hacked', 'content': 'Hacked'}))
        
        self.assertEqual(response.status_code, 403)
    
    # ========================
    # Tests de Eliminar Nota
    # ========================
    
    def test_delete_note_success(self):
        """Prueba: eliminar nota propia"""
        with self.app.app_context():
            note = Note(title='Para Borrar', content='Contenido', user_id=self.user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        response = self.client.delete(f'/api/notes/{note_id}', headers=self.get_headers())
        self.assertEqual(response.status_code, 200)
        
        # Verificar que fue eliminada
        with self.app.app_context():
            note = Note.query.get(note_id)
            self.assertIsNone(note)
    
    def test_delete_note_forbidden(self):
        """Prueba: no se puede eliminar nota de otro usuario"""
        with self.app.app_context():
            note = Note(title='Ajena', content='Contenido', user_id=self.other_user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        response = self.client.delete(f'/api/notes/{note_id}', headers=self.get_headers())
        self.assertEqual(response.status_code, 403)
        
        # Verificar que NO fue eliminada
        with self.app.app_context():
            note = Note.query.get(note_id)
            self.assertIsNotNone(note)


class SearchRoutesTest(unittest.TestCase):
    """Pruebas para el endpoint de búsqueda"""
    
    def setUp(self):
        """Configurar el entorno antes de cada prueba"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            user = User(username='searchuser', email='search@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
    
    def tearDown(self):
        """Limpiar el entorno después de cada prueba"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def login(self):
        """Helper para hacer login"""
        self.client.post('/login', data={
            'username': 'searchuser',
            'password': 'password123'
        })
    
    def test_search_requires_login(self):
        """Prueba: búsqueda requiere autenticación"""
        response = self.client.get('/buscar-notas?q=test')
        self.assertEqual(response.status_code, 302)
    
    def test_search_by_title(self):
        """Prueba: búsqueda por título funciona"""
        self.login()
        
        with self.app.app_context():
            note = Note(title='Flask Tutorial', content='Aprender Flask', user_id=self.user_id)
            db.session.add(note)
            db.session.commit()
        
        response = self.client.get('/buscar-notas?q=Flask')
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 1)
    
    def test_search_by_content(self):
        """Prueba: búsqueda por contenido funciona"""
        self.login()
        
        with self.app.app_context():
            note = Note(title='Nota', content='Python es genial', user_id=self.user_id)
            db.session.add(note)
            db.session.commit()
        
        response = self.client.get('/buscar-notas?q=Python')
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 1)
    
    def test_search_no_results(self):
        """Prueba: búsqueda sin resultados retorna lista vacía"""
        self.login()
        
        response = self.client.get('/buscar-notas?q=inexistente')
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 0)


if __name__ == '__main__':
    unittest.main()
