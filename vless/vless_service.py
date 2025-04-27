import requests
import json
import base64
import uuid
import random
import string
import time
import os
from database.models import async_session, VlessKey
from datetime import datetime, timedelta

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

vless_users = {}

vless_url = os.getenv("VLESS_URL")
vless_username = os.getenv("VLESS_USERNAME")
vless_password = os.getenv("VLESS_PASSWORD")


# Авторизация
def login():
    session = requests.Session()
    data = {"username": vless_username, "password": vless_password}  # логин и пароль
    response = session.post(vless_url + "login", data=data)
    if response.status_code == 200 and response.json().get("success"):
        return session
    else:
        raise Exception("❌ Не удалось войти в панель X-UI")


# Получить inbound
def get_inbound(session: requests.Session, inbound_id: int) -> dict:
    url = f"{vless_url}panel/api/inbounds/get/{inbound_id}"
    response = session.get(url)
    if response.status_code == 200:
        return response.json()["obj"]
    else:
        raise Exception(f"❌ Не удалось получить inbound: {response.text}")


# Генерация ссылки
def generate_client_link(client: dict, inbound: dict) -> str:
    protocol = inbound.get("protocol", "")
    settings = json.loads(inbound["settings"])
    stream_settings = json.loads(inbound["streamSettings"])
    server_address = os.getenv("SERVER_ADDRESS")  # только IP или домен без http
    port = inbound["port"]

    # Отладка для streamSettings и realitySettings
    # print("Stream Settings:", stream_settings)

    if protocol == "vmess":
        vmess_config = {
            "v": "2",
            "ps": client["email"],
            "add": server_address,
            "port": str(port),
            "id": client["id"],
            "aid": "0",
            "net": stream_settings.get("network", "tcp"),
            "type": "none",
            "host": stream_settings.get("tlsSettings", {}).get("serverName", ""),
            "path": stream_settings.get("wsSettings", {}).get("path", ""),
            "tls": "tls" if stream_settings.get("security") == "tls" else ""
        }
        return "vmess://" + base64.urlsafe_b64encode(json.dumps(vmess_config).encode()).decode().rstrip("=")

    elif protocol == "vless":
        uuid_ = client["id"]
        email = client["email"]
        network = stream_settings.get("network", "tcp")
        security = stream_settings.get("security", "none")
        flow = client.get("flow", "")

        # По умолчанию пустые значения
        pbk = fp = sni = sid = spx = ""

        # Если используется reality, достаём нужные поля
        if security == "reality":

            reality_settings = stream_settings.get("realitySettings", {})
            # print("Reality Settings:", reality_settings)

            # Доступ к settings внутри realitySettings
            settings = reality_settings.get("settings", {})
            pbk = settings.get("publicKey", "")
            sid = reality_settings.get("shortIds", [""])[0]  # Берём первый из shortIds
            spx = settings.get("spiderX", "")
            sni = settings.get("serverName", "")

            # Если sni пустое, используем значение по умолчанию
            if not sni:
                sni = "google.com"

            fp = settings.get("fingerprint", "")

        # Добавляем "test-" перед email
        email = f"test-{email}"

        # Генерация ссылки
        return (
            f"vless://{uuid_}@{server_address}:{port}"
            f"?type={network}&security={security}"
            f"&pbk={pbk}&fp={fp}&sni={sni}&sid={sid}&spx={spx}"
            f"&flow={flow}#{email}"
        )

    else:
        return f"🔗 Протокол {protocol} пока не поддерживается."


# Функция для генерации уникального email
def generate_unique_email(existing_emails) -> str:
    while True:
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"user_{random_str}@example.com"
        if email not in existing_emails:  # Если email уникален
            return email


async def add_client(inbound_id: int, total_gb: int, expiry_days: int, flow: str = "",
                     chat_id: int = 0, user_name: str = None) -> VlessKey:
    session = login()

    # Получаем актуальные данные о клиенте перед добавлением нового
    inbound = get_inbound(session, inbound_id)

    # Получаем текущих клиентов и их email
    clients = json.loads(inbound["settings"]).get("clients", [])
    existing_emails = [client["email"] for client in clients]

    # print(f"Текущие email: {existing_emails}")

    # Генерация уникального email
    email = generate_unique_email(existing_emails)
    # print(f"Генерируемый email: {email}")

    expiry_time = (int(time.time()) + expiry_days * 86400) * 1000

    new_client = {
        "id": str(uuid.uuid4()),
        "alterId": 0,
        "email": email,
        "limitIp": 0,
        "totalGB": total_gb * 1024 ** 3,
        "expiryTime": expiry_time,
        "enable": True
    }

    if inbound["protocol"] == "vless" and flow:
        new_client["flow"] = flow

    # Отправляем запрос только с новым клиентом, не пересылаем старые данные
    data = {
        "id": inbound_id,
        "up": inbound["up"],
        "down": inbound["down"],
        "total": inbound["total"],
        "remark": inbound["remark"],
        "enable": inbound["enable"],
        "expiryTime": inbound["expiryTime"],
        "clientStats": inbound["clientStats"],
        "listen": inbound["listen"],
        "port": inbound["port"],
        "protocol": inbound["protocol"],
        "settings": json.dumps({
            "clients": [new_client],  # Только новый клиент
            "decryption": "none",
            "fallbacks": []
        }),
        "streamSettings": inbound["streamSettings"],
        "tag": inbound["tag"],
        "sniffing": inbound["sniffing"],
        "allocate": inbound["allocate"]
    }

    # print("Данные, отправляемые на сервер:")
    # print(json.dumps(data, indent=2))

    response = session.post(vless_url + "panel/api/inbounds/addClient", json=data)

    if response.status_code == 200 and response.json().get("success"):
        # Получаем актуальный inbound после добавления клиента
        updated_inbound = get_inbound(session, inbound_id)

        # Берем клиента с нужным email (вдруг X-UI изменил что-то)
        updated_clients = json.loads(updated_inbound["settings"]).get("clients", [])
        matching_client = next((c for c in updated_clients if c["email"] == email), new_client)

        # Генерация ссылки по обновлённым данным
        client_link = generate_client_link(matching_client, updated_inbound)

        key = VlessKey(
            uuid=new_client["id"],
            access_url=client_link,
            chat_id=chat_id,
            key_id=str(uuid.uuid4()),
            user_name=user_name,
            total_limit_gb=total_gb,
            expires_at=datetime.utcnow() + timedelta(days=expiry_days),
            protocol=inbound["protocol"],
            flow=flow
        )

        async with async_session() as db:  # Сохраняем ключ в базу данных
            async with db.begin():
                db.add(key)

        # print("✅ Клиент успешно добавлен!")
        # print("🔑 Ссылка подключения:", client_link)
        return key
    else:
        print(f"Ответ сервера: {response.text}")
        raise Exception(f"❌ Ошибка добавления клиента: {response.text}")


