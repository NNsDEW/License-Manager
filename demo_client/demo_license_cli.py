import sys
import getpass
import requests

BASE_URL = "http://127.0.0.1:8000/api"


def get_token(username: str, password: str) -> str:
    """Получить токен по логину/паролю."""
    url = f"{BASE_URL}/auth/token/"
    resp = requests.post(url, json={"username": username, "password": password})
    if resp.status_code != 200:
        print("Не удалось получить токен:")
        print(resp.status_code, resp.text)
        sys.exit(1)
    data = resp.json()
    token = data.get("token")
    if not token:
        print("Сервер не вернул токен:", data)
        sys.exit(1)
    return token


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Token {token}", "Content-Type": "application/json"}


def generate_license(token: str, client_id: int, product_id: int, license_type_id: int) -> dict:
    """Вызов /api/support-tickets/generate/ для создания лицензии."""
    import json

    url = f"{BASE_URL}/support-tickets/generate/"
    payload = {
        "client_id": client_id,
        "product_id": product_id,
        "license_type_id": license_type_id,
    }
    print("\n=== Запрос генерации лицензии ===")
    print("POST", url)
    print("Тело:", json.dumps(payload, ensure_ascii=False))

    resp = requests.post(url, json=payload, headers=auth_headers(token))
    print("\n=== Ответ генерации лицензии ===")
    print(resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()


def validate_by_key(token: str, key: str) -> dict:
    """Проверка по ключу через /api/support-tickets/validate-key/."""
    import json

    url = f"{BASE_URL}/support-tickets/validate-key/"
    payload = {"key": key}
    print("\n=== Запрос проверки ключа ===")
    print("POST", url)
    print("Тело:", json.dumps(payload, ensure_ascii=False))

    resp = requests.post(url, json=payload, headers=auth_headers(token))
    print("\n=== Ответ проверки ключа ===")
    print(resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()


def main():
    print("ДЕМО: генерация и проверка лицензии через API\n")
    print("Перед комиссией:")
    print("  1) Убедитесь, что backend запущен: python manage.py runserver")
    print("  2) В веб-интерфейсе создайте хотя бы одного клиента, продукт и тип лицензии.")
    print("  3) Запускайте этот скрипт из корня проекта или папки demo_client.\n")

    username = input("Логин (например admin): ").strip()
    password = getpass.getpass("Пароль: ")

    print("\nПолучаю токен...")
    try:
        token = get_token(username, password)
    except Exception as e:
        print("Ошибка при получении токена:", e)
        sys.exit(1)
    print("Токен получен.\n")

    print("Теперь укажите ID объектов, которые уже есть в системе.")
    print("ID можно посмотреть в веб-интерфейсе (разделы Клиенты / Продукты / Типы лицензий).\n")

    try:
        client_id = int(input("ID клиента: ").strip())
        product_id = int(input("ID продукта: ").strip())
        license_type_id = int(input("ID типа лицензии: ").strip())
    except ValueError:
        print("ID должны быть числами.")
        sys.exit(1)

    # Генерация
    try:
        license_data = generate_license(token, client_id, product_id, license_type_id)
    except Exception as e:
        print("\nОшибка генерации лицензии:", e)
        sys.exit(1)

    key = license_data.get("key")
    if not key:
        print("\nКлюч не найден в ответе, показать комиссии можно только сам факт генерации.")
        sys.exit(0)

    print("\nСгенерированный ключ:", key)

    # Проверка
    try:
        validation = validate_by_key(token, key)
    except Exception as e:
        print("\nОшибка проверки ключа:", e)
        sys.exit(1)

    print("\nКраткий вывод для комиссии:")
    print("  Ключ:", key)
    print("  valid:", validation.get("valid"))
    print("  reason:", validation.get("reason"))
    print("  product:", validation.get("product"))
    print("  license_type:", validation.get("license_type"))
    print("\nДемо завершено.")


if __name__ == "__main__":
    main()

