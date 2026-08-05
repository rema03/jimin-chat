from django.db.models import Q

from accounts.models import User
from .models import ChatMessage, Friendship


ROOM_PREFIX = 'dm'


def build_room_name(user_a, user_b):
    """두 유저의 ID 기반으로 고유 채팅방 이름 생성"""
    first_id, second_id = sorted((user_a.id, user_b.id))
    return f'{ROOM_PREFIX}-{first_id}-{second_id}'


def parse_room_name(room_name):
    """채팅방 이름을 파싱하여 참가자 정보를 반환"""
    if room_name.startswith(f'{ROOM_PREFIX}-'):
        parts = room_name.split('-')
        if len(parts) != 3:
            return None
        _, first_id, second_id = parts
        if not first_id.isdigit() or not second_id.isdigit():
            return None
        return {
            'type': 'ids',
            'participant_ids': (int(first_id), int(second_id)),
        }

    # 레거시 username 기반 채팅방 (username1_username2)
    participants = room_name.split('_')
    if len(participants) != 2:
        return None
    return {
        'type': 'usernames',
        'participant_usernames': tuple(participants),
    }


def is_room_participant(room_name, user):
    """해당 유저가 채팅방 참여자인지 확인"""
    room_info = parse_room_name(room_name)
    if not room_info or not user.is_authenticated:
        return False

    if room_info['type'] == 'ids':
        return user.id in room_info['participant_ids']
    return user.username in room_info['participant_usernames']


def get_other_user_for_room(room_name, current_user):
    """채팅방의 상대방 유저 객체를 반환"""
    room_info = parse_room_name(room_name)
    if not room_info:
        return None

    if room_info['type'] == 'ids':
        if current_user.id not in room_info['participant_ids']:
            return None
        other_id = (
            room_info['participant_ids'][1]
            if room_info['participant_ids'][0] == current_user.id
            else room_info['participant_ids'][0]
        )
        return User.objects.filter(id=other_id).first()

    usernames = room_info['participant_usernames']
    if current_user.username not in usernames:
        return None
    other_username = usernames[1] if usernames[0] == current_user.username else usernames[0]
    return User.objects.filter(username=other_username).first()


def get_or_create_room_name(current_user, other_user):
    """기존 채팅방이 있으면 반환, 없으면 새 이름 생성"""
    existing_room_name = (
        ChatMessage.objects.filter(
            Q(sender=current_user, receiver=other_user)
            | Q(sender=other_user, receiver=current_user)
        )
        .order_by('-timestamp')
        .values_list('room_name', flat=True)
        .first()
    )
    return existing_room_name or build_room_name(current_user, other_user)


def get_display_name(current_user, other_user, friendship=None):
    """친구 별명이 있으면 별명을, 없으면 이름/username을 반환"""
    if friendship is None:
        friendship = Friendship.objects.filter(user=current_user, friend=other_user).first()
    return friendship.nickname if friendship and friendship.nickname else (other_user.name or other_user.username)


def get_websocket_path(room_name):
    return f'/ws/chat/{room_name}/'
