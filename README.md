generate RSA keys:

openssl genpkey -algorithm RSA -out src/core/secrets/private_key.pem -pkeyopt rsa_keygen_bits:4096

openssl rsa -pubout -in src/core/secrets/private_key.pem -out src/core/secrets/public_key.pem

argon2:

echo -n "test" | argon2 "somesalt" -id -t 3 -m 16 -p 4

$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$Eyo2xYv1fdJwRTeT/xFWS3c6SYqZhlYVI9gRUvcUdSc

insert into staffs (firstname, login, active, hashed_password) values ('max', 'admin', true, '
);
