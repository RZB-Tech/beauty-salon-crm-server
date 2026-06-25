generate RSA keys:

openssl genpkey -algorithm RSA -out src/core/secrets/private_key.pem -pkeyopt rsa_keygen_bits:4096

openssl rsa -pubout -in src/core/secrets/private_key.pem -out src/core/secrets/public_key.pem

argon2:

echo -n "test" | argon2 "somesalt" -id -t 3 -m 16 -p 4

$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$Eyo2xYv1fdJwRTeT/xFWS3c6SYqZhlYVI9gRUvcUdSc

insert into staffs (firstname, login, active, hashed_password) values ('max', 'admin', true, '
);

Docker instruction:

ВАЖНО! Если Docker запускается на Windows, необходимо перевостепенно открыть файл entrypoint.sh через VSCode (или другой редактор кода поддерживающий данную функцию), снизу справа нажать на CRLF и в верхнем модульном окне появится выбор - нужно выбрать LF и сохранить.

1. Настройте .env взяв за пример .env.docker-example
2. Сделайте build: docker compose build --no-cache
3. Запустите контейнеры: docker compose up -d
4. Если это первый запуск, требуется сделать миграцию моделей таблиц:
   4.1 docker exec -it salonBackend uv run migrate.py
5. Проверьте готовность сервера: docker logs salonBackend
6. Готово
