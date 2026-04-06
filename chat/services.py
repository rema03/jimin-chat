from django.db.models import Q

from accounts.models import User

from .models import ChatMessage, Friendship


ROOM_PREFIX = 'dm'


def build_room_name(user_a, user_b):
    first_id, second_id = sorted((user_a.id, user_b.id))
    return f'{ROOM_PREFIX}-{first_id}-{second_id}'


def parse_room_name(room_name):
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

    participants = room_name.split('_')
    if len(participants) != 2:
        return None
    return {
        'type': 'usernames',
        'participant_usernames': tuple(participants),
    }


def is_room_participant(room_name, user):
    room_info = parse_room_name(room_name)
    if not room_info or not user.is_authenticated:
        return False

    if room_info['type'] == 'ids':
        return user.id in room_info['participant_ids']

    return user.username in room_info['participant_usernames']


def get_other_user_for_room(room_name, current_user):
    room_info = parse_room_name(room_name)
    if not room_info:
        return None

    if room_info['type'] == 'ids':
        if current_user.id not in room_info['participant_ids']:
            return None
        other_id = room_info['participant_ids'][1] if room_info['participant_ids'][0] == current_user.id else room_info['participant_ids'][0]
        return User.objects.filter(id=other_id).first()

    usernames = room_info['participant_usernames']
    if current_user.username not in usernames:
        return None
    other_username = usernames[1] if usernames[0] == current_user.username else usernames[0]
    return User.objects.filter(username=other_username).first()


def get_or_create_room_name(current_user, other_user):
    existing_room_name = (
        ChatMessage.objects.filter(
            Q(sender=current_user, receiver=other_user) | Q(sender=other_user, receiver=current_user)
        )
        .order_by('-timestamp')
        .values_list('room_name', flat=True)
        .first()
    )
    return existing_room_name or build_room_name(current_user, other_user)


def get_display_name(current_user, other_user, friendship=None):
    if friendship is None:
        friendship = Friendship.objects.filter(user=current_user, friend=other_user).first()
    return friendship.nickname if friendship and friendship.nickname else (other_user.name or other_user.username)


def get_websocket_path(room_name):
    return f'/ws/chat/{room_name}/'
