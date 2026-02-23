def user_profile(request):
    """Добавляет user в контекст как user_profile для навбара (role, is_administrator)."""
    if request.user.is_authenticated:
        unread_student_chat_messages = 0
        if request.user.role_name in ('psychologist', 'admin'):
            from django.db.models import OuterRef, Exists
            from consultations.models import ChatMessage, ChatMessageRead
            qs = (
                ChatMessage.objects
                .filter(author__role__name='student')
                .exclude(author_id=request.user.id)
                .annotate(
                    read_by_me=Exists(
                        ChatMessageRead.objects.filter(
                            message_id=OuterRef('pk'),
                            user_id=request.user.id,
                        )
                    )
                )
                .filter(read_by_me=False)
            )
            if request.user.role_name == 'psychologist':
                qs = qs.filter(chat__psychologist_id=request.user.id)
            unread_student_chat_messages = qs.count()
        return {
            'user_profile': request.user,
            'unread_student_chat_messages': unread_student_chat_messages,
        }
    return {'user_profile': None, 'unread_student_chat_messages': 0}
