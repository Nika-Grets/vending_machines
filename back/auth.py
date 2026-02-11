import bcrypt

def hash_password(password: str) -> str:
    # Превращаем пароль в байты (нужно для bcrypt)
    pwd_bytes = password.encode('utf-8')
    # Генерируем соль
    salt = bcrypt.gensalt()
    # Хешируем
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    # Возвращаем как строку для базы данных
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Проверяем: пароль (байты) против хеша из базы (байты)
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Ошибка верификации: {e}")
        return False