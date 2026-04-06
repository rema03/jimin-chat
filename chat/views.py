from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.views.decorators.http import require_POST
from accounts.models import User
from .models import Friendship, ChatMessage
from .services import (
    get_display_name,
    get_or_create_room_name,
    get_other_user_for_room,
    get_websocket_path,
    is_room_participant,
)

@login_required
def friend_list(request):
    friendships = Friendship.objects.filter(user=request.user).select_related('friend').order_by('friend__username')
    friendship_map = {friendship.friend_id: friendship for friendship in friendships}
    unread_total = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()

    unread_counts = {
        item['room_name']: item['total']
        for item in (
            ChatMessage.objects.filter(receiver=request.user, is_read=False)
            .values('room_name')
            .annotate(total=Count('id'))
        )
    }

    recent_messages = ChatMessage.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').order_by('-timestamp')

    rooms = []
    seen_rooms = set()
    for last_message in recent_messages:
        if last_message.room_name in seen_rooms:
            continue

        seen_rooms.add(last_message.room_name)
        other_user = last_message.receiver if last_message.sender_id == request.user.id else last_message.sender
        friendship = friendship_map.get(other_user.id)

        rooms.append({
            'room_name': last_message.room_name,
            'display_name': get_display_name(request.user, other_user, friendship),
            'unread_count': unread_counts.get(last_message.room_name, 0),
            'is_friend': other_user.id in friendship_map,
            'last_message': last_message.message if last_message.message else '(사진)',
            'last_time': last_message.timestamp,
        })

    return render(request, 'chat/friend_list.html', {
        'friends': friendships,
        'rooms': rooms,
        'unread_total': unread_total,
    })

@login_required
def room(request, room_name):
    other_user = get_other_user_for_room(room_name, request.user)
    if not other_user:
        return HttpResponseForbidden("해당 채팅방에 접근 권한이 없습니다.")

    friendship = Friendship.objects.filter(user=request.user, friend=other_user).first()
    messages = ChatMessage.objects.filter(room_name=room_name).select_related('sender').order_by('timestamp')
    ChatMessage.objects.filter(room_name=room_name, receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'chat_messages': messages,
        'display_title': get_display_name(request.user, other_user, friendship),
        'other_user': other_user,
        'upload_url': 'chat:upload_image',
        'ws_path': get_websocket_path(room_name),
    })

@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect('chat:friend_list')

    room_name = get_or_create_room_name(request.user, other_user)
    return redirect('chat:room', room_name=room_name)

@login_required
def add_friend(request):
    if request.method == 'POST':
        friend_id = (request.POST.get('friend_id') or '').strip()
        try:
            friend_user = User.objects.get(username=friend_id)
            if friend_user == request.user:
                return render(request, 'chat/add_friend.html', {'error': '자기 자신은 추가할 수 없습니다.'})
            Friendship.objects.get_or_create(user=request.user, friend=friend_user)
            return redirect('chat:friend_list')
        except User.DoesNotExist:
            return render(request, 'chat/add_friend.html', {'error': '아이디가 존재하지 않습니다.'})
    return render(request, 'chat/add_friend.html')

@login_required
@require_POST
def update_nickname(request):
    friend_id = request.POST.get('friend_id')
    new_nickname = (request.POST.get('nickname') or '').strip()
    friendship = get_object_or_404(Friendship, user=request.user, friend__username=friend_id)
    friendship.nickname = new_nickname or None
    friendship.save(update_fields=['nickname'])
    return redirect('chat:friend_list')

@login_required
@require_POST
def delete_friend(request):
    friend_id = request.POST.get('friend_id')
    Friendship.objects.filter(user=request.user, friend__username=friend_id).delete()
    return redirect('chat:friend_list')

@login_required
@require_POST
def upload_image(request):
    if request.FILES.get('image'):
        room_name = request.POST.get('room_name', '')
        if not is_room_participant(room_name, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        receiver = get_other_user_for_room(room_name, request.user)
        if not receiver:
            return JsonResponse({'error': 'Invalid room'}, status=400)

        image = request.FILES['image']
        msg = ChatMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            room_name=room_name,
            image=image,
        )
        return JsonResponse({'image_url': msg.image.url, 'sender': request.user.username})

    return JsonResponse({'error': 'Invalid request'}, status=400)
