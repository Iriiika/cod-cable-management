-- Создание таблицы для центров обработки данных
CREATE TABLE data_centers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  short_name VARCHAR(10) NOT NULL UNIQUE
);
CREATE INDEX idx_data_centers_short_name ON data_centers(short_name);

-- Создание таблицы для залов
CREATE TABLE halls (
  id SERIAL PRIMARY KEY,
  data_center_id INTEGER NOT NULL,
  name VARCHAR(10) NOT NULL UNIQUE,
  FOREIGN KEY (data_center_id) REFERENCES data_centers(id) ON DELETE CASCADE
);
CREATE INDEX idx_halls_data_center_id ON halls(data_center_id);

-- Создание таблицы для стоек
CREATE TABLE racks (
  id SERIAL PRIMARY KEY,
  hall_id INTEGER NOT NULL,
  name VARCHAR(10) NOT NULL UNIQUE,
  FOREIGN KEY (hall_id) REFERENCES halls(id) ON DELETE CASCADE
);
CREATE INDEX idx_racks_hall_id ON racks(hall_id);

-- Создание таблицы для коммутаторов
CREATE TABLE switches (
  id SERIAL PRIMARY KEY,
  rack_id INTEGER NOT NULL,
  type VARCHAR(10) NOT NULL,
  hostname VARCHAR(50) NOT NULL UNIQUE,
  unit INTEGER NOT NULL CHECK (unit >= 19 AND unit <= 25),
  port_srvm VARCHAR(10),
  port_data VARCHAR(10),
  FOREIGN KEY (rack_id) REFERENCES racks(id) ON DELETE CASCADE
);
CREATE INDEX idx_switches_rack_id ON switches(rack_id);
CREATE INDEX idx_switches_type ON switches(type);

-- Создание таблицы для серверов
CREATE TABLE servers (
  id SERIAL PRIMARY KEY,
  serial_number VARCHAR(10) NOT NULL UNIQUE,
  rack_id INTEGER NOT NULL,
  unit INTEGER NOT NULL CHECK (unit > 0 AND unit < 41 AND unit NOT BETWEEN 19 AND 25),
  description_srvm VARCHAR(50) NOT NULL,
  description_data1 VARCHAR(50) NOT NULL,
  description_data2 VARCHAR(50) NOT NULL,
  FOREIGN KEY (rack_id) REFERENCES racks(id) ON DELETE CASCADE
);
CREATE INDEX idx_servers_rack_id ON servers(rack_id);
CREATE INDEX idx_servers_unit ON servers(unit);

-- Создание таблицы для подключений
CREATE TABLE connections (
  id SERIAL PRIMARY KEY,
  server_id INTEGER NOT NULL,
  switch_id INTEGER NOT NULL,
  port VARCHAR(10) NOT NULL,
  label VARCHAR(100) NOT NULL,
  FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
  FOREIGN KEY (switch_id) REFERENCES switches(id) ON DELETE CASCADE
);
CREATE INDEX idx_connections_server_id ON connections(server_id);
CREATE INDEX idx_connections_switch_id ON connections(switch_id);

-- Создание таблицы для пользователей
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  role VARCHAR(20) NOT NULL,
  login VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE
);
CREATE INDEX idx_users_login ON users(login);
CREATE INDEX idx_users_role ON users(role);

-- Создание таблицы для ролей
CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  name VARCHAR(20) NOT NULL UNIQUE,
  permissions TEXT NOT NULL
);

-- Создание таблицы для логов действий пользователей
CREATE TABLE logs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  action VARCHAR(50) NOT NULL,
  object VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX idx_logs_created_at ON logs(created_at);

-- Создание таблицы для настроек приложения
CREATE TABLE settings (
  id SERIAL PRIMARY KEY,
  key VARCHAR(50) NOT NULL UNIQUE,
  value TEXT NOT NULL
);

-- Вставка тестовых данных для data_centers
INSERT INTO data_centers (name, short_name) VALUES
  ('QuantumFlow', 'QF'),
  ('DataHub', 'DH'),
  ('TechCore', 'TC'),
  ('SkyNet', 'SN'),
  ('DataWave', 'DW'),
  ('CloudPeak', 'CP'),
  ('InfoGrid', 'IG'),
  ('Nexus', 'NX'),
  ('BitForge', 'BF'),
  ('StreamBase', 'SB');

-- Вставка тестовых данных для halls (уникальные имена с префиксом ЦОД)
INSERT INTO halls (data_center_id, name) VALUES
  (1, 'QF_01'),
  (1, 'QF_02'),
  (2, 'DH_01'),
  (2, 'DH_02'),
  (3, 'TC_01'),
  (4, 'SN_01'),
  (5, 'DW_01'),
  (6, 'CP_01'),
  (7, 'IG_01'),
  (8, 'NX_01');

-- Вставка тестовых данных для racks (уникальные имена с префиксом зала)
INSERT INTO racks (hall_id, name) VALUES
  (1, 'QF_01_A01'),
  (1, 'QF_01_A05'),
  (1, 'QF_01_A09'),
  (2, 'QF_02_A01'),
  (3, 'DH_01_A01'),
  (4, 'DH_02_A01'),
  (5, 'TC_01_A01'),
  (6, 'SN_01_A01'),
  (7, 'DW_01_A01'),
  (8, 'CP_01_A01');

-- Вставка тестовых данных для switches
INSERT INTO switches (rack_id, type, hostname, unit, port_srvm, port_data) VALUES
  (1, 'SRVM', 'SRVM_QF_01_A01', 19, 'G01', NULL),
  (1, 'DATA1', 'DATA1_QF_01_A01', 21, NULL, 'G01/01'),
  (2, 'SRVM', 'SRVM_QF_01_A05', 19, 'G01', NULL),
  (3, 'DATA1', 'DATA1_QF_01_A09', 21, NULL, 'G01/01'),
  (4, 'SRVM', 'SRVM_QF_02_A01', 19, 'G01', NULL),
  (5, 'DATA1', 'DATA1_DH_01_A01', 21, NULL, 'G01/01'),
  (6, 'SRVM', 'SRVM_DH_02_A01', 19, 'G01', NULL),
  (7, 'DATA1', 'DATA1_TC_01_A01', 21, NULL, 'G01/01'),
  (8, 'SRVM', 'SRVM_SN_01_A01', 19, 'G01', NULL),
  (9, 'DATA1', 'DATA1_DW_01_A01', 21, NULL, 'G01/01');

-- Вставка тестовых данных для servers
INSERT INTO servers (serial_number, rack_id, unit, description_srvm, description_data1, description_data2) VALUES
  ('V6JGQ2SX', 1, 3, 'SRVM_V6JGQ2SX_unit-3', 'DATA1_V6JGQ2SX_unit-3', 'DATA2_V6JGQ2SX_unit-3'),
  ('X7KLP9TY', 1, 4, 'SRVM_X7KLP9TY_unit-4', 'DATA1_X7KLP9TY_unit-4', 'DATA2_X7KLP9TY_unit-4'),
  ('Z8MQR1UV', 2, 5, 'SRVM_Z8MQR1UV_unit-5', 'DATA1_Z8MQR1UV_unit-5', 'DATA2_Z8MQR1UV_unit-5'),
  ('A9NWS2VW', 3, 6, 'SRVM_A9NWS2VW_unit-6', 'DATA1_A9NWS2VW_unit-6', 'DATA2_A9NWS2VW_unit-6'),
  ('B1PXT3WX', 4, 7, 'SRVM_B1PXT3WX_unit-7', 'DATA1_B1PXT3WX_unit-7', 'DATA2_B1PXT3WX_unit-7'),
  ('C2QYU4XY', 5, 8, 'SRVM_C2QYU4XY_unit-8', 'DATA1_C2QYU4XY_unit-8', 'DATA2_C2QYU4XY_unit-8'),
  ('D3RZV5YZ', 6, 9, 'SRVM_D3RZV5YZ_unit-9', 'DATA1_D3RZV5YZ_unit-9', 'DATA2_D3RZV5YZ_unit-9'),
  ('E4SAW6ZA', 7, 10, 'SRVM_E4SAW6ZA_unit-10', 'DATA1_E4SAW6ZA_unit-10', 'DATA2_E4SAW6ZA_unit-10'),
  ('F5TBX7AB', 8, 11, 'SRVM_F5TBX7AB_unit-11', 'DATA1_F5TBX7AB_unit-11', 'DATA2_F5TBX7AB_unit-11'),
  ('G6UCY8BC', 9, 12, 'SRVM_G6UCY8BC_unit-12', 'DATA1_G6UCY8BC_unit-12', 'DATA2_G6UCY8BC_unit-12');

-- Вставка тестовых данных для connections
INSERT INTO connections (server_id, switch_id, port, label) VALUES
  (1, 1, 'G01', 'SRVM_QF_01_A01 G01 -> 022 QF_01_A01 3(V6JGQ2SX)'),
  (2, 3, 'G02', 'SRVM_QF_01_A05 G02 -> 022 QF_01_A05 4(X7KLP9TY)'),
  (3, 5, 'G03', 'SRVM_QF_02_A01 G03 -> 022 QF_02_A01 5(Z8MQR1UV)'),
  (4, 7, 'G04', 'SRVM_DH_02_A01 G04 -> 022 DH_02_A01 6(A9NWS2VW)'),
  (5, 9, 'G05', 'SRVM_SN_01_A01 G05 -> 022 SN_01_A01 7(B1PXT3WX)'),
  (6, 1, 'G06', 'SRVM_QF_01_A01 G06 -> 022 QF_01_A01 8(C2QYU4XY)'),
  (7, 3, 'G07', 'SRVM_QF_01_A05 G07 -> 022 QF_01_A05 9(D3RZV5YZ)'),
  (8, 5, 'G08', 'SRVM_QF_02_A01 G08 -> 022 QF_02_A01 10(E4SAW6ZA)'),
  (9, 7, 'G09', 'SRVM_DH_02_A01 G09 -> 022 DH_02_A01 11(F5TBX7AB)'),
  (10, 9, 'G10', 'SRVM_SN_01_A01 G10 -> 022 SN_01_A01 12(G6UCY8BC)');

-- Вставка тестовых данных для users
INSERT INTO users (full_name, role, login, password, email) VALUES
  ('Иванов Сергей', 'Администратор', 'SergeyAIvanov', '$2b$12$dyxTC0V8BYZ55x/fd9PUhOJz.VOQdyadN842jUe09aLcrZiZqrFm6', 'SergeyAIvanov@dom.ru'),
  ('Петров Алексей', 'Инженер ЛВС', 'AlexeyPetrov', '$2b$12$HUI.2RP94/Pvti8Gvx46COOI7WWVXJ5ISdWupQ/6/pxxg2yRVIxk6', 'PetrovA@dom.ru'),
  ('Сидоров Иван', 'Наблюдатель', 'IvanSidorov', '$2b$12$4vtwG5Dxi/0sxDJsQQJrZeMDV1oaDqe8ADQcponaNW2pgZbtb/vm.', 'SidorovI@dom.ru'),
  ('Смирнова Анна', 'Администратор', 'AnnaSmirnova', '$2b$12$1pdOgpAoDsnp6TsuU14I4e5Y4F1KAU43F/37wsvnOj25sTL6mkL4e', 'SmirnovaA@dom.ru'),
  ('Козлов Дмитрий', 'Инженер ЛВС', 'DmitryKozlov', '$2b$12$9.zNlBvQkHEofcIGo/QkBulsdvy6oEGDW67Cels5Z9sak.7pUm27q', 'KozlovD@dom.ru'),
  ('Морозова Елена', 'Наблюдатель', 'ElenaMorozova', '$2b$12$nOgvRqQgnpn4iYGByDKB.e1/iR4TAUNIkBxfpmnh84LobOP0fasyq', 'MorozovaE@dom.ru'),
  ('Васильев Павел', 'Администратор', 'PavelVasiliev', '$2b$12$mcgoXl6P0lAlzppXx7f3NujbWcaDQj2jrfIzpKdTW3bSQwsr878Qm', 'VasilievP@dom.ru'),
  ('Лебедева Ольга', 'Инженер ЛВС', 'OlgaLebedeva', '$2b$12$q94YfLrprCGO1.h4pGzH7.JLK2ir5xMit.nUNZ2lKed9bwFWfqSA.', 'LebedevaO@dom.ru'),
  ('Попов Михаил', 'Наблюдатель', 'MikhailPopov', '$2b$12$gG4sVwlHztjC2lQSVgbAWOLpCsqMZgsA2SE06fw2Z6aA/IA/3tHM2', 'PopovM@dom.ru'),
  ('Федоров Никита', 'Инженер ЛВС', 'NikitaFedorov', '$2b$12$y8l6ToKH4sJh.jVUKYUDE.mQQS.X9K9OpB2ePo01NMRwdAcrt5pS6', 'FedorovN@dom.ru');

-- Вставка тестовых данных для roles
INSERT INTO roles (name, permissions) VALUES
  ('Администратор', 'Полные права: добавление, редактирование, удаление всех объектов, управление пользователями, отчеты'),
  ('Инженер ЛВС', 'Добавление/удаление подключений и коммутаторов, просмотр справочников, выгрузка в Excel'),
  ('Наблюдатель', 'Только просмотр справочников и отчетов');

-- Вставка тестовых данных для settings
INSERT INTO settings (key, value) VALUES
  ('label_format', 'SRVM_{dc_short}_{hall}_{rack} {port} -> {unit} {rack} {server_sn}'),
  ('export_limit', '1000');