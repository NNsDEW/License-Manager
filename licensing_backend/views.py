from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def auth_register(request):
    """Регистрация: username, password, email -> создаётся пользователь и токен."""
    username = request.data.get("username")
    password = request.data.get("password")
    email = (request.data.get("email") or "").strip() or f"{username}@example.com"
    if not username or not password:
        return Response(
            {"detail": "Укажите username и password"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if User.objects.filter(username=username).exists():
        return Response(
            {"detail": "Пользователь с таким логином уже существует"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = User.objects.create_user(username=username, password=password, email=email, is_staff=False)
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {"token": token.key, "username": user.username, "is_staff": user.is_staff},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def auth_me(request):
    """Текущий пользователь: username, is_staff для ролей на фронте."""
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "is_staff": request.user.is_staff,
        "is_superuser": getattr(request.user, "is_superuser", False),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def auth_users_list(request):
    """Список пользователей (только для staff): id, username, is_staff — чтобы админ мог смотреть данные по каждому пользователю."""
    if not request.user.is_staff:
        return Response({"detail": "Нет прав"}, status=status.HTTP_403_FORBIDDEN)
    users = User.objects.all().order_by("username")
    return Response([
        {"id": u.id, "username": u.username, "is_staff": u.is_staff}
        for u in users
    ])


def home(request):
    html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License Management System</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: system-ui, sans-serif; max-width: 640px; margin: 60px auto; padding: 20px; }
        h1 { color: #1a1a2e; }
        h2 { font-size: 1.1rem; margin-top: 24px; color: #333; }
        .links { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 24px; }
        a { display: inline-block; padding: 12px 20px; background: #4361ee; color: white; text-decoration: none; border-radius: 8px; }
        a:hover { background: #3a56d4; }
        .api { background: #2ec4b6; }
        .api:hover { background: #28a99c; }
        p { color: #555; line-height: 1.6; }
        .muted { font-size: 14px; color: #888; margin-top: 32px; }
    </style>
</head>
<body>
    <h1>License Management System</h1>
    <p><strong>Для чего нужна система:</strong> управление лицензиями ПО — создание продуктов, типов лицензий, клиентов, генерация ключей и проверка ключей. Пользователи работают в веб-интерфейсе; ваши программы проверяют ключи через API.</p>
    <h2>Зачем нужен API</h2>
    <p>API нужен, чтобы ваше приложение могло проверять ключи: программа отправляет ключ и код продукта на <code>POST /api/licenses/validate/</code> и получает ответ «действителен» или причина отказа. Так вы контролируете доступ к программе.</p>
    <h2>Что такое «получить токен»</h2>
    <p><strong>Токен</strong> — ключ авторизации для доступа к API. При входе на сайт (Angular) токен сохраняется автоматически. Если обращаетесь к API из скрипта или приложения: отправьте POST на <code>/api/auth/token/</code> с логином и паролем, в ответ придёт токен; в запросах передавайте заголовок <code>Authorization: Token &lt;токен&gt;</code>.</p>
    <div class="links">
        <a href="http://localhost:4200/">Веб-интерфейс (вход, генерация, проверка)</a>
        <a href="/admin/">Админка Django</a>
        <a href="/api/" class="api">Корень API (REST)</a>
        <a href="/api/auth/token/">Получить токен (POST: username, password)</a>
    </div>
    <p class="muted">Рекомендуется пользоваться веб-интерфейсом по адресу <a href="http://localhost:4200/" style="color: #4361ee;">http://localhost:4200/</a> — там вход, регистрация, генерация и проверка ключей, справка.</p>
</body>
</html>
"""
    return HttpResponse(html)
