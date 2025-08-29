from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from models import db, Chat, ChatMessage, ChatParticipant, User, School
from forms.chat_forms import ChatCreationForm, MessageForm
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def chat_list():
    """List user's chats"""
    # Get user's active chats
    chat_participants = ChatParticipant.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    chats = []
    for participant in chat_participants:
        chat = participant.chat
        if chat and chat.is_active:
            # Get last message
            last_message = ChatMessage.query.filter_by(
                chat_id=chat.id
            ).order_by(ChatMessage.created_at.desc()).first()
            
            # Get unread count
            unread_count = participant.get_unread_count()
            
            chats.append({
                'chat': chat,
                'last_message': last_message,
                'unread_count': unread_count,
                'participant': participant
            })
    
    # Sort by last message time
    chats.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else x['chat'].created_at, reverse=True)
    
    return render_template('chat/chat_list.html', 
                         chats=chats,
                         title='Чаты')

@chat_bp.route('/<int:chat_id>')
@login_required
def chat_view(chat_id):
    """View specific chat"""
    chat = Chat.query.get_or_404(chat_id)
    
    # Check if user is participant
    participant = ChatParticipant.query.filter_by(
        user_id=current_user.id,
        chat_id=chat_id,
        is_active=True
    ).first()
    
    if not participant:
        abort(403)
    
    # Get chat messages
    messages = ChatMessage.query.filter_by(
        chat_id=chat_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    # Mark messages as read
    participant.last_read_at = datetime.utcnow()
    db.session.commit()
    
    # Get other participants
    other_participants = ChatParticipant.query.filter(
        ChatParticipant.chat_id == chat_id,
        ChatParticipant.user_id != current_user.id,
        ChatParticipant.is_active == True
    ).all()
    
    return render_template('chat/chat_view.html', 
                         chat=chat,
                         messages=messages,
                         other_participants=other_participants,
                         title=chat.get_display_name())

@chat_bp.route('/create', methods=['GET', 'POST'])
@login_required
def chat_create():
    """Create new chat"""
    form = ChatCreationForm()
    
    # Get user's schools for school-specific chats
    user_schools = current_user.get_schools()
    form.school_id.choices = [('', 'Выберите школу')] + [(s.id, s.name) for s in user_schools]
    
    if form.validate_on_submit():
        # Create chat
        chat = Chat(
            name=form.name.data,
            chat_type=form.chat_type.data,
            description=form.description.data,
            school_id=form.school_id.data if form.school_id.data else None,
            subject_id=form.subject_id.data if form.subject_id.data else None,
            class_group_id=form.class_group_id.data if form.class_group_id.data else None
        )
        
        db.session.add(chat)
        db.session.flush()  # Get the chat ID
        
        # Add creator as participant
        creator_participant = ChatParticipant(
            user_id=current_user.id,
            chat_id=chat.id,
            role='admin'
        )
        db.session.add(creator_participant)
        
        # Add other participants if specified
        if form.participants.data:
            participant_ids = [int(id) for id in form.participants.data.split(',') if id.strip()]
            for user_id in participant_ids:
                if user_id != current_user.id:
                    participant = ChatParticipant(
                        user_id=user_id,
                        chat_id=chat.id
                    )
                    db.session.add(participant)
        
        db.session.commit()
        
        flash(f'Чат "{chat.get_display_name()}" создан!', 'success')
        return redirect(url_for('chat.chat_view', chat_id=chat.id))
    
    return render_template('chat/chat_create.html', 
                         form=form,
                         title='Создание чата')

@chat_bp.route('/<int:chat_id>/add_participant', methods=['POST'])
@login_required
def add_participant(chat_id):
    """Add participant to chat"""
    chat = Chat.query.get_or_404(chat_id)
    
    # Check if user can add participants
    participant = ChatParticipant.query.filter_by(
        user_id=current_user.id,
        chat_id=chat_id,
        is_active=True
    ).first()
    
    if not participant or participant.role not in ['admin', 'moderator']:
        abort(403)
    
    user_id = request.form.get('user_id')
    if not user_id:
        flash('Не указан пользователь для добавления.', 'error')
        return redirect(url_for('chat.chat_view', chat_id=chat_id))
    
    # Check if user is already participant
    existing_participant = ChatParticipant.query.filter_by(
        user_id=user_id,
        chat_id=chat_id
    ).first()
    
    if existing_participant:
        if existing_participant.is_active:
            flash('Пользователь уже является участником чата.', 'error')
        else:
            existing_participant.is_active = True
            db.session.commit()
            flash('Пользователь добавлен в чат!', 'success')
    else:
        new_participant = ChatParticipant(
            user_id=user_id,
            chat_id=chat_id
        )
        db.session.add(new_participant)
        db.session.commit()
        flash('Пользователь добавлен в чат!', 'success')
    
    return redirect(url_for('chat.chat_view', chat_id=chat_id))

@chat_bp.route('/<int:chat_id>/remove_participant', methods=['POST'])
@login_required
def remove_participant(chat_id):
    """Remove participant from chat"""
    chat = Chat.query.get_or_404(chat_id)
    
    # Check if user can remove participants
    participant = ChatParticipant.query.filter_by(
        user_id=current_user.id,
        chat_id=chat_id,
        is_active=True
    ).first()
    
    if not participant or participant.role not in ['admin', 'moderator']:
        abort(403)
    
    user_id = request.form.get('user_id')
    if not user_id:
        flash('Не указан пользователь для удаления.', 'error')
        return redirect(url_for('chat.chat_view', chat_id=chat_id))
    
    # Remove participant
    target_participant = ChatParticipant.query.filter_by(
        user_id=user_id,
        chat_id=chat_id
    ).first()
    
    if target_participant:
        target_participant.is_active = False
        target_participant.left_at = datetime.utcnow()
        db.session.commit()
        flash('Пользователь удален из чата!', 'success')
    
    return redirect(url_for('chat.chat_view', chat_id=chat_id))

@chat_bp.route('/<int:chat_id>/leave', methods=['POST'])
@login_required
def leave_chat(chat_id):
    """Leave chat"""
    participant = ChatParticipant.query.filter_by(
        user_id=current_user.id,
        chat_id=chat_id,
        is_active=True
    ).first()
    
    if participant:
        participant.is_active = False
        participant.left_at = datetime.utcnow()
        db.session.commit()
        flash('Вы покинули чат.', 'info')
    
    return redirect(url_for('chat.chat_list'))

@chat_bp.route('/<int:chat_id>/settings', methods=['GET', 'POST'])
@login_required
def chat_settings(chat_id):
    """Chat settings"""
    chat = Chat.query.get_or_404(chat_id)
    
    # Check if user is admin
    participant = ChatParticipant.query.filter_by(
        user_id=current_user.id,
        chat_id=chat_id,
        is_active=True
    ).first()
    
    if not participant or participant.role != 'admin':
        abort(403)
    
    if request.method == 'POST':
        # Update chat settings
        chat.name = request.form.get('name')
        chat.description = request.form.get('description')
        chat.allow_attachments = 'allow_attachments' in request.form
        chat.require_moderation = 'require_moderation' in request.form
        
        db.session.commit()
        flash('Настройки чата обновлены!', 'success')
        return redirect(url_for('chat.chat_view', chat_id=chat_id))
    
    return render_template('chat/chat_settings.html', 
                         chat=chat,
                         title=f'Настройки чата: {chat.get_display_name()}')

@chat_bp.route('/api/<int:chat_id>/messages')
@login_required
def get_messages(chat_id):
    """API endpoint to get chat messages"""
    # Check if user is participant
    participant = ChatParticipant.query.filter_by(
        user_id=current_user.id,
        chat_id=chat_id,
        is_active=True
    ).first()
    
    if not participant:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get messages
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    messages = ChatMessage.query.filter_by(
        chat_id=chat_id
    ).order_by(ChatMessage.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Format messages for JSON
    message_list = []
    for message in messages.items:
        message_list.append({
            'id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'timestamp': message.created_at.isoformat(),
            'message_type': message.message_type,
            'is_edited': message.is_edited,
            'is_deleted': message.is_deleted
        })
    
    return jsonify({
        'messages': message_list,
        'has_next': messages.has_next,
        'has_prev': messages.has_prev,
        'page': page,
        'pages': messages.pages
    })

@chat_bp.route('/api/<int:chat_id>/send', methods=['POST'])
@login_required
def send_message(chat_id):
    """API endpoint to send message"""
    # Check if user is participant
    participant = ChatParticipant.query.filter_by(
        user_id=current_user.id,
        chat_id=chat_id,
        is_active=True
    ).first()
    
    if not participant:
        return jsonify({'error': 'Access denied'}), 403
    
    content = request.form.get('message')
    if not content:
        return jsonify({'error': 'Message content is required'}), 400
    
    # Create message
    message = ChatMessage(
        content=content,
        sender_id=current_user.id,
        chat_id=chat_id
    )
    
    db.session.add(message)
    
    # Update chat's last message time
    chat = Chat.query.get(chat_id)
    chat.last_message_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message_id': message.id,
        'timestamp': message.created_at.isoformat()
    })