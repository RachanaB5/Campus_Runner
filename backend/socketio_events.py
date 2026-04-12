from __future__ import annotations

from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import join_room, leave_room

from models import db, Runner


def _get_socket_user_id() -> str | None:
    auth = request.args.get('token') or request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()
    if not token:
        auth_payload = getattr(request, 'args', {})
        token = auth_payload.get('token') if hasattr(auth_payload, 'get') else None
    if not token:
        return None

    try:
        decoded = decode_token(token)
        return decoded.get('sub')
    except Exception:
        return None


def register_socketio_events(socketio):
    @socketio.on('connect')
    def handle_connect(auth=None):
        user_id = None
        if isinstance(auth, dict):
            token = auth.get('token')
            if token:
                try:
                    decoded = decode_token(token)
                    user_id = decoded.get('sub')
                except Exception:
                    user_id = None
        if not user_id:
            user_id = _get_socket_user_id()
        if user_id:
            join_room(f'user:{user_id}')

    @socketio.on('join_user_room')
    def handle_join_user_room(data=None):
        user_id = _get_socket_user_id()
        if user_id:
            join_room(f'user:{user_id}')

    @socketio.on('runner_online')
    def handle_runner_online(data=None):
        user_id = _get_socket_user_id()
        if not user_id:
            return
        join_room('runners_online')
        runner = Runner.query.filter_by(user_id=user_id).first()
        if runner:
            runner.is_available = True
            runner.status = 'online'
            db.session.commit()
        socketio.emit('runner_status', {'status': 'online'}, room=f'user:{user_id}')

    @socketio.on('runner_offline')
    def handle_runner_offline(data=None):
        user_id = _get_socket_user_id()
        if not user_id:
            return
        leave_room('runners_online')
        runner = Runner.query.filter_by(user_id=user_id).first()
        if runner:
            runner.is_available = False
            runner.status = 'offline'
            db.session.commit()
        socketio.emit('runner_status', {'status': 'offline'}, room=f'user:{user_id}')

    @socketio.on('disconnect')
    def handle_disconnect():
        user_id = _get_socket_user_id()
        if not user_id:
            return
        runner = Runner.query.filter_by(user_id=user_id).first()
        if runner and runner.status != 'on_delivery':
            runner.is_available = False
            runner.status = 'offline'
            db.session.commit()
