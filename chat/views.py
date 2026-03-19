from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max, Count
from django.http import JsonResponse
from accounts.models import User
from .models import Friendship, ChatMessage

@login_required
def friend_list(request):
    # 1. 친구 목록
    friends = Friendship.objects.filter(user=request.user, is_blocked=False)

    # 2. 채팅 목록 및 알림 계산
    rooms_query = ChatMessage.objects.filter(
        Q(room_name__contains=f"_{request.user.username}") | Q(room_name__contains=f"{request.user.username}_")
    ).values('room_name').annotate(
        last_msg_text=Max('message'),
        last_msg_time=Max('timestamp'),
        unread_cnt=Count('id', filter=Q(is_read=False) & ~Q(sender=request.user))
    ).order_by('-last_msg_time')

    processed_rooms = []
    unread_total = 0
    for r in rooms_query:
        participants = r['room_name'].split('_')
        if len(participants) < 2: continue
        other_username = participants[0] if participants[1] == request.user.username else participants[1]
        try:
            other_user = User.objects.get(username=other_username)
            friendship = Friendship.objects.filter(user=request.user, friend=other_user).first()
            display_name = friendship.nickname if friendship and friendship.nickname else other_user.name
        except User.DoesNotExist:
            display_name = other_username
        
        unread_total += r['unread_cnt']
        processed_rooms.append({
            'room_name': r['room_name'], 
            'display_name': display_name, 
            'unread_count': r['unread_cnt'], 
            'last_time': r['last_msg_time']
        })

    return render(request, 'chat/friend_list.html', {
        'friends': friends, 
        'rooms': processed_rooms, 
        'unread_total': unread_total
    })

@login_required
def room(request, room_name):
    participants = room_name.split('_')
    is_friend, other_username = False, None
    if len(participants) == 2:
        other_username = participants[0] if participants[1] == request.user.username else participants[1]
        try:
            other_user = User.objects.get(username=other_username)
            friendship = Friendship.objects.filter(user=request.user, friend=other_user).first()
            is_friend = True if friendship else False
            display_title = f"{friendship.nickname if is_friend and friendship.nickname else other_user.name}({other_user.username})"
        except User.DoesNotExist:
            display_title = room_name
    else:
        display_title = room_name

    ChatMessage.objects.filter(room_name=room_name).exclude(sender=request.user).update(is_read=True)
    chat_messages = ChatMessage.objects.filter(room_name=room_name).order_by('timestamp')
    return render(request, 'chat/room.html', {
        'room_name': room_name, 
        'display_title': display_title, 
        'other_username': other_username, 
        'is_friend': is_friend, 
        'chat_messages': chat_messages
    })

@login_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        room_name = request.POST.get('room_name')
        img_file = request.FILES.get('image')
        msg = ChatMessage.objects.create(sender=request.user, room_name=room_name, image=img_file)
        return JsonResponse({'status': 'success', 'image_url': msg.image.url, 'user': request.user.username})
    return JsonResponse({'status': 'error'})

@login_required
def add_friend_ajax(request):
    if request.method == 'POST':
        friend_username = request.POST.get('friend_username')
        try:
            target_user = User.objects.get(username=friend_username)
            Friendship.objects.get_or_create(user=request.user, friend=target_user)
            return JsonResponse({'status': 'success'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '유저 없음'})
    return JsonResponse({'status': 'error'})

@login_required
def add_friend(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            target_user = User.objects.get(username=username)
            if target_user != request.user and not Friendship.objects.filter(user=request.user, friend=target_user).exists():
                Friendship.objects.create(user=request.user, friend=target_user)
                return redirect('chat:friend_list')
        except User.DoesNotExist:
            messages.error(request, "유저가 없습니다.")
    return render(request, 'chat/add_friend.html')

@login_required
def update_nickname(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        new_nickname = request.POST.get('nickname')
        friendship = get_object_or_404(Friendship, user=request.user, friend__username=friend_id)
        friendship.nickname = new_nickname
        friendship.save()
    return redirect('chat:friend_list')

@login_required
def delete_friend(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        Friendship.objects.filter(user=request.user, friend__username=friend_id).delete()
    return redirect('chat:friend_list')