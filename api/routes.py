from functools import wraps
from flask import Blueprint, jsonify, request
from flask_login import current_user
from models import db, User, Note

api_bp = Blueprint("api", __name__, url_prefix="/api")


def require_api_key(f):
    """Decorador para autenticación por API Key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API Key requerida. Envía el header X-API-Key'
            }), 401
        
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'API Key inválida'
            }), 401
        
        # Inyectar usuario en el request context
        request.api_user = user
        return f(*args, **kwargs)
    return decorated


@api_bp.route('/notes', methods=['GET'])
@require_api_key
def list_notes():
    """Listar notas del usuario autenticado con paginación"""
    from app import cache
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)
    per_page = min(per_page, 50)  # Limitar máximo de resultados
    
    # Cache key única por usuario y página
    cache_key = f"api_notes_{request.api_user.id}_p{page}_pp{per_page}"
    cached = cache.get(cache_key)
    
    if cached:
        return jsonify(cached)
    
    pagination = Note.query.filter_by(user_id=request.api_user.id)\
        .order_by(Note.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    result = {
        'status': 'success',
        'data': [note.to_dict() for note in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
    
    cache.set(cache_key, result, timeout=30)
    return jsonify(result)


@api_bp.route('/notes/<int:id>', methods=['GET'])
@require_api_key
def get_note(id):
    """Obtener una nota por ID"""
    note = Note.query.get_or_404(id)
    
    if note.user_id != request.api_user.id:
        return jsonify({
            'status': 'error',
            'message': 'No tienes permiso para ver esta nota'
        }), 403
    
    return jsonify({
        'status': 'success',
        'data': note.to_dict()
    })


@api_bp.route('/notes', methods=['POST'])
@require_api_key
def create_note():
    """Crear una nueva nota"""
    from app import cache
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Se requiere un cuerpo JSON'
        }), 400
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    if not title or not content:
        return jsonify({
            'status': 'error',
            'message': 'Título y contenido son requeridos'
        }), 400
    
    if len(title) > 50:
        return jsonify({
            'status': 'error',
            'message': 'El título no puede exceder 50 caracteres'
        }), 400
    
    if len(content) > 100:
        return jsonify({
            'status': 'error',
            'message': 'El contenido no puede exceder 100 caracteres'
        }), 400
    
    note = Note(title=title, content=content, user_id=request.api_user.id)
    db.session.add(note)
    db.session.commit()
    
    # Invalidar caché del usuario
    _invalidate_user_cache(request.api_user.id)
    
    return jsonify({
        'status': 'success',
        'message': 'Nota creada exitosamente',
        'data': note.to_dict()
    }), 201


@api_bp.route('/notes/<int:id>', methods=['PUT'])
@require_api_key
def update_note(id):
    """Actualizar una nota existente"""
    from app import cache
    
    note = Note.query.get_or_404(id)
    
    if note.user_id != request.api_user.id:
        return jsonify({
            'status': 'error',
            'message': 'No tienes permiso para editar esta nota'
        }), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Se requiere un cuerpo JSON'
        }), 400
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    if not title or not content:
        return jsonify({
            'status': 'error',
            'message': 'Título y contenido son requeridos'
        }), 400
    
    if len(title) > 50:
        return jsonify({
            'status': 'error',
            'message': 'El título no puede exceder 50 caracteres'
        }), 400
    
    if len(content) > 100:
        return jsonify({
            'status': 'error',
            'message': 'El contenido no puede exceder 100 caracteres'
        }), 400
    
    note.title = title
    note.content = content
    db.session.commit()
    
    # Invalidar caché del usuario
    _invalidate_user_cache(request.api_user.id)
    
    return jsonify({
        'status': 'success',
        'message': 'Nota actualizada exitosamente',
        'data': note.to_dict()
    })


@api_bp.route('/notes/<int:id>', methods=['DELETE'])
@require_api_key
def delete_note(id):
    """Eliminar una nota"""
    from app import cache
    
    note = Note.query.get_or_404(id)
    
    if note.user_id != request.api_user.id:
        return jsonify({
            'status': 'error',
            'message': 'No tienes permiso para eliminar esta nota'
        }), 403
    
    db.session.delete(note)
    db.session.commit()
    
    # Invalidar caché del usuario
    _invalidate_user_cache(request.api_user.id)
    
    return jsonify({
        'status': 'success',
        'message': 'Nota eliminada exitosamente'
    })


@api_bp.route('/generate-key', methods=['POST'])
@require_api_key
def regenerate_key():
    """Regenerar el API Key del usuario"""
    user = request.api_user
    new_key = user.generate_api_key()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'API Key regenerada exitosamente',
        'data': {'api_key': new_key}
    })


def _invalidate_user_cache(user_id):
    """Invalida todo el caché de notas de un usuario"""
    from app import cache
    # Limpiar todo el caché (SimpleCache no soporta borrado por patrón)
    cache.clear()
