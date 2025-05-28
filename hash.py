import bcrypt

passwords = ['admin123', 'engineer123', 'observer123', 'admin456', 'engineer456', 'observer456', 'admin789', 'engineer789', 'observer789', 'engineer101']
for pwd in passwords:
    hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"Пароль: {pwd}, Хеш: {hashed}")