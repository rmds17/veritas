CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}' WITH GRANT OPTION;
FLUSH PRIVILEGES;
-- GRANT ALL PRIVILEGES ON *.* TO 'flask_user'@'%' IDENTIFIED BY 'flask_password' WITH GRANT OPTION;
-- FLUSH PRIVILEGES;


-- Criação do banco de dados e tabela para o CRUD
CREATE DATABASE IF NOT EXISTS veritas_db;
USE veritas_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    photo VARCHAR(255) DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO users (username, email, password, photo, is_active)
VALUES (
    'admin',
    'joao.silva@example.com',
    '1234',
    NULL,
    TRUE
);

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    categoria VARCHAR(255) NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
INSERT INTO categorias (categoria) VALUES
('História'),
('Desporto'),
('Futebol'),
('Política'),
('Música');


CREATE TABLE fatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fato TEXT NOT NULL,
    categoria_id INT NOT NULL,
    data_fato DATE,
    localizacao VARCHAR(255),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
-- 1. História: Queda do Muro de Berlim
INSERT INTO fatos (fato, categoria_id, data_fato, localizacao)
VALUES (
    'A queda do Muro de Berlim ocorreu a 9 de novembro de 1989, simbolizando o fim da Guerra Fria e a reunificação da Alemanha.',
    1,
    '1989-11-09',
    'Berlim, Alemanha'
);
/* Fonte: BBC, DW */

-- 2. Desporto: Usain Bolt recorde dos 100 metros
INSERT INTO fatos (fato, categoria_id, data_fato, localizacao)
VALUES (
    'Usain Bolt estabeleceu o recorde mundial dos 100 metros em 9,58 segundos no Campeonato do Mundo de Atletismo de 2009.',
    2,
    '2009-08-16',
    'Berlim, Alemanha'
);
/* Fonte: World Athletics, Olympic.org */

-- 3. Futebol: Portugal vence o Euro 2016
INSERT INTO fatos (fato, categoria_id, data_fato, localizacao)
VALUES (
    'Portugal venceu o Campeonato Europeu de Futebol (Euro 2016) ao derrotar a França por 1–0, com um golo de Éder no prolongamento.',
    3,
    '2016-07-10',
    'Paris, França'
);
/* Fonte: UEFA, RTP */

-- 4. Política: Barack Obama eleito presidente dos EUA
INSERT INTO fatos (fato, categoria_id, data_fato, localizacao)
VALUES (
    'Barack Obama foi eleito o 44.º presidente dos Estados Unidos em 2008, tornando-se o primeiro afro-americano a ocupar o cargo.',
    4,
    '2008-11-04',
    'Washington, D.C., EUA'
);
/* Fonte: White House Archives, CNN, New York Times */

-- 5. Música: Lançamento do álbum "Thriller" de Michael Jackson
INSERT INTO fatos (fato, categoria_id, data_fato, localizacao)
VALUES (
    'O álbum "Thriller" de Michael Jackson foi lançado a 30 de novembro de 1982 e tornou-se o álbum mais vendido da história da música.',
    5,
    '1982-11-30',
    'Estados Unidos'
);
/* Fonte: Billboard, Guinness World Records */


);
);
