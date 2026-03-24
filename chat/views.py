from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from accounts.models import User
from .models import Friendship, ChatMessage


def _get_other_username(room_name, current_username):
    participants = room_name.split('_')
    if len(participants) != 2 or current_username not in participants:
        return None
    return participants[1] if participants[0] == current_username else participants[0]


@login_required
def friend_list(request):
    # 내 친구 목록 가져오기
    friends = Friendship.objects.filter(user=request.user)
    
    # 읽지 않은 총 메시지 수
    unread_total = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()

    # 내가 참여한 채팅방 목록 추출
    distinct_rooms = ChatMessage.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values_list('room_name', flat=True).distinct()

    rooms = []
    for r_name in distinct_rooms:
        participants = r_name.split('_')
        if request.user.username not in participants:
            continue
            
        other_username = participants[1] if participants[0] == request.user.username else participants[0]
        try:
            other_user = User.objects.get(username=other_username)
            friendship = Friendship.objects.filter(user=request.user, friend=other_user).first()
            
            # 표시될 이름 결정 (별명 > 이름 > 아이디)
            display_name = friendship.nickname if friendship and friendship.nickname else (other_user.name or other_user.username)
            
            # 해당 방의 읽지 않은 메시지 수
            unread_count = ChatMessage.objects.filter(room_name=r_name, receiver=request.user, is_read=False).count()

            rooms.append({
                'room_name': r_name,
                'display_name': display_name,
                'unread_count': unread_count
            })
        except User.DoesNotExist:
            continue

    return render(request, 'chat/friend_list.html', {
        'friends': friends,
        'rooms': rooms,
        'unread_total': unread_total
    })

@login_required
def room(request, room_name):
    other_username = _get_other_username(room_name, request.user.username)
    if not other_username:
        return HttpResponseForbidden("접근 권한이 없습니다.")
    
    try:
        other_user = User.objects.get(username=other_username)
        friendship = Friendship.objects.filter(user=request.user, friend=other_user).first()
        display_title = friendship.nickname if friendship and friendship.nickname else (other_user.name or other_user.username)
    except User.DoesNotExist:
        display_title = other_username

    # 메시지 로드 및 읽음 처리
    messages = ChatMessage.objects.filter(room_name=room_name).order_by('timestamp')
    ChatMessage.objects.filter(room_name=room_name, receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'chat_messages': messages,
        'display_title': display_title,
        'other_username': other_username
    })

@login_required
def add_friend(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        try:
            friend_user = User.objects.get(username=friend_id)
            if friend_user == request.user:
                return render(request, 'chat/add_friend.html', {'error': '자기 자신은 추가할 수 없습니다.'})
            
            Friendship.objects.get_or_create(user=request.user, friend=friend_user)
            return redirect('chat:friend_list')
        except User.DoesNotExist:
            return render(request, 'chat/add_friend.html', {'error': '존재하지 않는 아이디입니다.'})
            
    return render(request, 'chat/add_friend.html')

# --- 에러가 났던 부분: 별명 수정 함수 추가 ---
@login_required
def update_nickname(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        new_nickname = request.POST.get('nickname')
        friend_user = get_object_or_404(User, username=friend_id)
        
        friendship = Friendship.objects.filter(user=request.user, friend=friend_user).first()
        if friendship:
            friendship.nickname = new_nickname
            friendship.save()
            
    return redirect('chat:friend_list')

@login_required
def delete_friend(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        friend_user = get_object_or_404(User, username=friend_id)
        Friendship.objects.filter(user=request.user, friend=friend_user).delete()
        
    return redirect('chat:friend_list')

@login_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        room_name = request.POST.get('room_name')

        other_username = _get_other_username(room_name, request.user.username)
        if not other_username:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        receiver = get_object_or_404(User, username=other_username)

        msg = ChatMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            room_name=room_name,
            image=image
        )
        return JsonResponse({'image_url': msg.image.url})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
