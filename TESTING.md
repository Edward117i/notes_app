# Pruebas Unitarias - Aplicación Flask Notes App

## Resumen

Se han implementado **29 pruebas unitarias** que cubren:
- **Modelos**: Usuarios y Notas (seguridad, relaciones, validaciones)
- **Rutas de Autenticación**: Registro, login, validaciones
- **Rutas de Notas**: Crear, editar, eliminar, permisos
- **Otras Rutas**: Páginas estáticas (acerca de, contacto)

## Cambios Realizados

### 1. **Refactorización de `app.py` - Patrón Application Factory**
Se implementó el patrón Application Factory que permite:
- ✅ Crear instancias de la app con diferentes configuraciones
- ✅ Facilitar las pruebas unitarias
- ✅ Mejor estructura y mantenibilidad

```python
def create_app(config_class=Config):
    """Factory pattern para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ... resto de inicialización
    return app
```

### 2. **Mejora de `config.py`**
Se optimizó la configuración de pruebas:
- Base de datos en memoria (`:memory:`) para pruebas más rápidas
- `TESTING = True` para modo de prueba
- `WTF_CSRF_ENABLED = False` para facilitar pruebas de formularios

### 3. **Archivos de Pruebas Creados**

#### `test_models.py` - Pruebas de Modelos (13 pruebas)

**Pruebas del modelo User:**
- ✅ Crear usuario correctamente
- ✅ Hash de contraseña funciona
- ✅ Verificación de contraseña correcta
- ✅ Validación de usernames únicos
- ✅ Validación de emails únicos

**Pruebas del modelo Note:**
- ✅ Crear nota correctamente
- ✅ Relación usuario-nota funciona
- ✅ Un usuario puede tener múltiples notas
- ✅ Representación correcta de la nota

#### `test_routes.py` - Pruebas de Rutas (16 pruebas)

**Pruebas de Autenticación:**
- ✅ Página de registro carga correctamente
- ✅ Registro exitoso con datos válidos
- ✅ Faltan campos en registro
- ✅ Contraseña muy corta
- ✅ Las contraseñas no coinciden
- ✅ No permite usuarios duplicados
- ✅ No permite emails duplicados
- ✅ Página de login carga correctamente
- ✅ Login exitoso
- ✅ Login falla con contraseña incorrecta

**Pruebas de Notas:**
- ✅ Home requiere autenticación
- ✅ Home muestra las notas del usuario
- ✅ Página de crear nota carga
- ✅ Crear nota exitosa
- ✅ Crear nota falla si faltan campos
- ✅ No se puede editar nota de otro usuario
- ✅ Editar nota propia funciona

**Otras Rutas:**
- ✅ Página acerca de carga
- ✅ GET a contacto funciona
- ✅ POST a contacto funciona

#### `run_tests.py` - Script para Ejecutar Pruebas

Script útil para ejecutar todas las pruebas de forma sencilla.

## Cómo Ejecutar las Pruebas

### Opción 1: Ejecutar todas las pruebas
```bash
python run_tests.py
```

### Opción 2: Modo verbose (más detalles)
```bash
python run_tests.py verbose
```

### Opción 3: Ejecutar un archivo específico
```bash
python -m unittest test_models.py
python -m unittest test_routes.py
```

### Opción 4: Ejecutar una prueba específica
```bash
python -m unittest test_models.UserModelTest.test_create_user
```

## Estructura de Pruebas

### Flujo de Cada Prueba

```
setUp()          # Configurar entorno (crear app, base de datos)
    ↓
test_xxx()       # Ejecutar la prueba
    ↓
tearDown()       # Limpiar recursos (limpiar BD, eliminar datos)
```

### Contexto de Aplicación

Las pruebas utilizan correctamente el contexto de aplicación de Flask:

```python
with self.app.app_context():
    # Operaciones que requieren contexto de app
    db.create_all()
    note = Note(...)
    db.session.add(note)
    db.session.commit()
```

## Resultados de la Ejecución

```
Ran 29 tests in 9.814s

OK ✓
```

- ✅ **29 tests passed**
- ❌ **0 tests failed**
- ⏭️ **0 tests skipped**

## Mejoras Futuras (Opcionales)

1. **Coverage (Cobertura de Código)**
   ```bash
   pip install coverage
   coverage run -m unittest discover
   coverage report
   coverage html  # Genera reporte HTML
   ```

2. **Test de Validaciones Adicionales**
   - Longitud máxima de título/contenido
   - Caracteres especiales en datos de entrada
   - Ejecución concurrente de operaciones

3. **Test de Rendimiento**
   - Tiempo de respuesta de rutas
   - Consultas a base de datos optimizadas

4. **Integración Continua**
   - GitHub Actions para ejecutar pruebas automáticamente
   - SonarQube para análisis de código

## Notas Importantes

### Base de Datos de Prueba
- Se utiliza una base de datos en memoria (SQLite `:memory:`)
- Cada prueba tiene su propio contexto limpio
- No afecta los datos de producción

### Aislamiento de Pruebas
- Cada prueba es independiente
- Los datos creados en una prueba no afectan otras pruebas
- Garantiza resultados reproducibles

### Mejores Prácticas Implementadas
- ✅ Uso correcto del contexto de aplicación
- ✅ Limpieza de recursos (tearDown)
- ✅ Nombres descriptivos de pruebas
- ✅ Docstrings explicativos
- ✅ Assertions específicas
- ✅ Pruebas de casos positivos y negativos

## Troubleshooting

### Error: "Instance not bound to a Session"
**Solución**: Asegurate de acceder a los atributos dentro del contexto de aplicación o guarda el ID antes de salir del contexto.

### Error: "No module named 'app'"
**Solución**: Ejecuta los tests desde el directorio raíz del proyecto.

### Base de datos no se limpia
**Solución**: Verifica que `tearDown()` se ejecute correctamente llamando a `db.drop_all()`.

---

**Últimas actualizaciones**: 2024-06-09
**Estado**: ✅ Todas las pruebas pasando
