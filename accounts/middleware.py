# ĐỒNG BỘ session['role'] VỚI ROLE THẬT TRONG DB Ở MỌI REQUEST
# (tránh session cũ / login qua /admin/ làm role trong session lệch với tài khoản)
class SyncRoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            if request.session.get('role') != user.role:
                request.session['role'] = user.role
        elif 'role' in request.session:
            del request.session['role']
        return self.get_response(request)
