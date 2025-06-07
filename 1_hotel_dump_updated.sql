--
-- Обновленный PostgreSQL дамп базы данных
-- Дата: 2025-05-30 22:30:00
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- ===== ОСНОВНЫЕ ДАННЫЕ =====

-- Groups
INSERT INTO public.auth_group VALUES (1, 'Manager');

-- Content Types (обновленные)
INSERT INTO public.django_content_type VALUES (1, 'admin', 'logentry');
INSERT INTO public.django_content_type VALUES (2, 'auth', 'permission');
INSERT INTO public.django_content_type VALUES (3, 'auth', 'group');
INSERT INTO public.django_content_type VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO public.django_content_type VALUES (5, 'sessions', 'session');
INSERT INTO public.django_content_type VALUES (6, 'hotel', 'roomtype');
INSERT INTO public.django_content_type VALUES (7, 'hotel', 'booking');
INSERT INTO public.django_content_type VALUES (8, 'hotel', 'hotel');
INSERT INTO public.django_content_type VALUES (9, 'hotel', 'room');
INSERT INTO public.django_content_type VALUES (10, 'hotel', 'roomservices');
INSERT INTO public.django_content_type VALUES (11, 'hotel', 'hotelgallery');
INSERT INTO public.django_content_type VALUES (12, 'hotel', 'hotelfeatures');
INSERT INTO public.django_content_type VALUES (13, 'hotel', 'hotelfaqs');
INSERT INTO public.django_content_type VALUES (14, 'hotel', 'coupon');
INSERT INTO public.django_content_type VALUES (15, 'hotel', 'couponusers');
INSERT INTO public.django_content_type VALUES (16, 'hotel', 'notification');
INSERT INTO public.django_content_type VALUES (17, 'hotel', 'bookmark');
INSERT INTO public.django_content_type VALUES (18, 'hotel', 'review');
INSERT INTO public.django_content_type VALUES (19, 'hotel', 'roomtypegallery');
INSERT INTO public.django_content_type VALUES (20, 'hotel', 'roomtypefeatures');
INSERT INTO public.django_content_type VALUES (21, 'hotel', 'roomtypedescription');
INSERT INTO public.django_content_type VALUES (22, 'hotel', 'roomtypefeaturesdetailed');
INSERT INTO public.django_content_type VALUES (23, 'booking', 'roomunavailability');
INSERT INTO public.django_content_type VALUES (24, 'userauths', 'user');
INSERT INTO public.django_content_type VALUES (25, 'userauths', 'profile');
INSERT INTO public.django_content_type VALUES (26, 'taggit', 'tag');
INSERT INTO public.django_content_type VALUES (27, 'taggit', 'taggeditem');
INSERT INTO public.django_content_type VALUES (28, 'legal', 'legaldocument');
INSERT INTO public.django_content_type VALUES (29, 'legal', 'documentview');
INSERT INTO public.django_content_type VALUES (30, 'userauths', 'userconsent');

-- Permissions (добавляем новые разрешения)
INSERT INTO public.auth_permission VALUES (109, 'Can add legal document', 28, 'add_legaldocument');
INSERT INTO public.auth_permission VALUES (110, 'Can change legal document', 28, 'change_legaldocument');
INSERT INTO public.auth_permission VALUES (111, 'Can delete legal document', 28, 'delete_legaldocument');
INSERT INTO public.auth_permission VALUES (112, 'Can view legal document', 28, 'view_legaldocument');
INSERT INTO public.auth_permission VALUES (113, 'Can add document view', 29, 'add_documentview');
INSERT INTO public.auth_permission VALUES (114, 'Can change document view', 29, 'change_documentview');
INSERT INTO public.auth_permission VALUES (115, 'Can delete document view', 29, 'delete_documentview');
INSERT INTO public.auth_permission VALUES (116, 'Can view document view', 29, 'view_documentview');
INSERT INTO public.auth_permission VALUES (117, 'Can add user consent', 30, 'add_userconsent');
INSERT INTO public.auth_permission VALUES (118, 'Can change user consent', 30, 'change_userconsent');
INSERT INTO public.auth_permission VALUES (119, 'Can delete user consent', 30, 'delete_userconsent');
INSERT INTO public.auth_permission VALUES (120, 'Can view user consent', 30, 'view_userconsent');

-- Миграции (обновленные)
INSERT INTO public.django_migrations VALUES (120, 'hotel', '0086_hotel_end_date_hotel_start_date', '2025-05-30 22:15:00.000000+05');
INSERT INTO public.django_migrations VALUES (121, 'hotel', '0087_alter_hotelfeatures_name', '2025-05-30 22:15:10.000000+05');
INSERT INTO public.django_migrations VALUES (122, 'hotel', '0088_booking_selection_data', '2025-05-30 22:15:20.000000+05');
INSERT INTO public.django_migrations VALUES (123, 'legal', '0001_initial', '2025-05-30 22:20:00.000000+05');
INSERT INTO public.django_migrations VALUES (124, 'userauths', '0007_alter_profile_image', '2025-05-30 22:21:00.000000+05');
INSERT INTO public.django_migrations VALUES (125, 'userauths', '0008_alter_profile_image', '2025-05-30 22:22:00.000000+05');
INSERT INTO public.django_migrations VALUES (126, 'userauths', '0009_alter_profile_image', '2025-05-30 22:23:00.000000+05');
INSERT INTO public.django_migrations VALUES (127, 'userauths', '0010_userconsent', '2025-05-30 22:24:00.000000+05');

-- Пользователи (обновленные)
INSERT INTO public.userauths_user VALUES (1, 'pbkdf2_sha256$600000$um0lXqXrUP4A1PdjqPPNOJ$6Kxx5/WjwGHZbKx8YLh7YqIsxJkLtC6K46Gp/ducoh8=', '2025-05-19 19:43:55.109241+05', true, '', '', true, true, '2025-05-19 19:19:53.6198+05', NULL, 'admin', 'admin@gmail.com', NULL, NULL, NULL);
INSERT INTO public.userauths_user VALUES (4, 'pbkdf2_sha256$600000$um0lXqXrUP4A1PdjqPPNOJ$6Kxx5/WjwGHZbKx8YLh7YqIsxJkLtC6K46Gp/ducoh8=', NULL, false, '', '', false, true, '2025-05-19 20:18:49+05', 'Manager Manager', 'Manager', 'manager@gmail.com', NULL, NULL, NULL);

-- Профили пользователей (обновленные)
INSERT INTO public.userauths_profile VALUES (1, 'aidsf3i', 'default.jpg', 'admin', NULL, NULL, NULL, NULL, NULL, true, '2025-05-19 19:19:54.007413+05', 1, 0.00);
INSERT INTO public.userauths_profile VALUES (4, 'dcpquoq', 'default.jpg', 'Manager', NULL, NULL, NULL, NULL, NULL, false, '2025-05-19 20:19:58.355597+05', 4, 0.00);

-- Отели (с новыми полями start_date и end_date)
INSERT INTO public.hotel_hotel VALUES (1, 'grand-hyat-hotel', 'Описание отеля...', 'hotel_gallery/test_image_hotel_D5gtCKK.jpeg', 'Кабанбай ауыл, шоссейное 15', '877777777777', 'Manager@gmail.com', 'Live', 142, false, 'btukidoopc', 'grand-hyat-hotel', '2025-05-19 20:29:01.296337+05', 4, 'Описание на русском...', 'Описание на казахском...', 'Описание на английском...', 'grand-hyat-hotel', 'grand-hyat-hotel', 'grand-hyat-hotel', '14:00:00', '12:00:00', '2025-06-01', '2025-12-31');

-- Типы комнат (с полем dynamic_pricing)
INSERT INTO public.hotel_roomtype VALUES (1, 'Basic', 10000.00, 'EyRhoRMQ5F', '2025-05-19 20:29:01.323301+05', 1, 1, 'basic-7hpv', 1, 10, '{"2025-05-19": 10000, "2025-05-20": 10000, "2025-05-21": 10000, "2025-05-22": 10000, "2025-05-23": 10000, "2025-05-24": 10000, "2025-05-25": 10000, "2025-05-26": 11000, "2025-05-27": 11000, "2025-05-28": 11000, "2025-05-29": 11000, "2025-05-30": 11000, "2025-05-31": 11000, "2025-06-01": 11000, "2025-06-02": 12000, "2025-06-03": 12000}');
INSERT INTO public.hotel_roomtype VALUES (2, 'Standard', 20000.00, 'ZVrj4TEH8Y', '2025-05-19 20:29:01.327327+05', 1, 2, 'standard-dwt6', 2, 20, '{"2025-05-19": 24000, "2025-05-20": 24000, "2025-05-21": 24000, "2025-05-22": 24000, "2025-05-23": 24000, "2025-05-24": 24000, "2025-05-25": 24000, "2025-05-26": 26400, "2025-05-27": 26400}');

-- Галерея отеля
INSERT INTO public.hotel_hotelgallery VALUES (1, 'hotel_gallery/Houghton-Hotel-3-20-scaled_20t8Bl0.jpg', 'ZKRdWHAskS', 1);
INSERT INTO public.hotel_hotelgallery VALUES (2, 'hotel_gallery/istockphoto-119926339-612x612_0SoS3eE.jpg', 'Ksi4bw5UR9', 1);
INSERT INTO public.hotel_hotelgallery VALUES (3, 'hotel_gallery/1407953244000-177513283_H2AmFQq.webp', '3vqh9sgbJu', 1);

-- Особенности отеля
INSERT INTO public.hotel_hotelfeatures VALUES (1, 'wifi.png', 'wifi', 'F5HLaC8Mps', 1);
INSERT INTO public.hotel_hotelfeatures VALUES (2, 'fan.png', 'fan', 'dzjFUgc5Ji', 1);

-- FAQ отеля (с мультиязычными полями)
INSERT INTO public.hotel_hotelfaqs VALUES (1, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit...', '2025-05-19 20:32:22.393566+05', 'VjKjunASE7', 1, 'Ответ на русском...', 'Жауап қазақ тілінде...', 'Answer in English...', 'Вопрос на русском?', 'Сұрақ қазақ тілінде?', 'Question in English?');

-- Комнаты
INSERT INTO public.hotel_room VALUES (1, '101', 1, true, 'bSR2wbzBRK', '2025-05-19 20:32:22.388474+05', 1);
INSERT INTO public.hotel_room VALUES (2, '102', 1, true, 'oFeMJSUTKP', '2025-05-19 20:32:22.390498+05', 1);

-- Описания типов комнат (мультиязычные)
INSERT INTO public.hotel_roomtypedescription VALUES (1, 'Описание базового номера...', 1, 1, 'Описание на русском...', 'Сипаттама қазақ тілінде...', 'Description in English...');
INSERT INTO public.hotel_roomtypedescription VALUES (2, 'Описание стандартного номера...', 1, 2, 'Описание на русском...', 'Сипаттама қазақ тілінде...', 'Description in English...');

-- Галерея типов комнат
INSERT INTO public.hotel_roomtypegallery VALUES (1, 'room_type_images/376785918.jpg', 1, 1);
INSERT INTO public.hotel_roomtypegallery VALUES (2, 'room_type_images/376785930_Mf9DI2h.jpg', 1, 1);
INSERT INTO public.hotel_roomtypegallery VALUES (3, 'room_type_images/Bellagio-Hotel-Casino-Las-Vegas_P3bRrwX.webp', 1, 1);
INSERT INTO public.hotel_roomtypegallery VALUES (4, 'room_type_images/marquis-3-min.jpg', 1, 1);

-- Особенности типов комнат
INSERT INTO public.hotel_roomtypefeatures VALUES (1, 'wifi.png', 'Free wifi in room', 'P2Wijw7Lm3', 1, 1);

-- Детальные особенности типов комнат (мультиязычные)
INSERT INTO public.hotel_roomtypefeaturesdetailed VALUES (1, 'private_bathroom', 'Особенность в частной ванной', 'TK2oQjNa5L', 1, 1, 'Особенность на русском', 'Ерекшелік қазақ тілінде', 'Feature in English');

-- ===== НОВЫЕ ТАБЛИЦЫ =====

-- Недоступность номеров (новая таблица)
-- Пока пустая

-- Юридические документы (новая таблица)
INSERT INTO public.legal_legaldocument VALUES (1, 'terms_of_use', '1.0', 'Настоящие Условия использования определяют правила пользования сайтом...', '2025-05-30 22:00:00.000000+05', '2025-05-30 22:00:00.000000+05', true, 'ru');
INSERT INTO public.legal_legaldocument VALUES (2, 'privacy_policy', '1.0', 'Политика конфиденциальности описывает принципы обработки персональных данных...', '2025-05-30 22:00:00.000000+05', '2025-05-30 22:00:00.000000+05', true, 'ru');
INSERT INTO public.legal_legaldocument VALUES (3, 'public_offer', '1.0', 'Публичная оферта содержит условия предоставления услуг...', '2025-05-30 22:00:00.000000+05', '2025-05-30 22:00:00.000000+05', true, 'ru');

-- Просмотры документов (новая таблица)
-- Пока пустая

-- Согласия пользователей (новая таблица)
-- Пока пустая

-- ===== ПОСЛЕДОВАТЕЛЬНОСТИ =====

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, true);
SELECT pg_catalog.setval('public.auth_permission_id_seq', 120, true);
SELECT pg_catalog.setval('public.django_content_type_id_seq', 30, true);
SELECT pg_catalog.setval('public.django_migrations_id_seq', 127, true);
SELECT pg_catalog.setval('public.userauths_user_id_seq', 4, true);
SELECT pg_catalog.setval('public.userauths_profile_id_seq', 4, true);
SELECT pg_catalog.setval('public.hotel_hotel_id_seq', 1, true);
SELECT pg_catalog.setval('public.hotel_roomtype_id_seq', 2, true);
SELECT pg_catalog.setval('public.hotel_room_id_seq', 2, true);
SELECT pg_catalog.setval('public.hotel_hotelgallery_id_seq', 3, true);
SELECT pg_catalog.setval('public.hotel_hotelfeatures_id_seq', 2, true);
SELECT pg_catalog.setval('public.hotel_hotelfaqs_id_seq', 1, true);
SELECT pg_catalog.setval('public.hotel_roomtypedescription_id_seq', 2, true);
SELECT pg_catalog.setval('public.hotel_roomtypegallery_id_seq', 4, true);
SELECT pg_catalog.setval('public.hotel_roomtypefeatures_id_seq', 1, true);
SELECT pg_catalog.setval('public.hotel_roomtypefeaturesdetailed_id_seq', 1, true);
SELECT pg_catalog.setval('public.legal_legaldocument_id_seq', 3, true);
SELECT pg_catalog.setval('public.booking_roomunavailability_id_seq', 1, false);
SELECT pg_catalog.setval('public.legal_documentview_id_seq', 1, false);
SELECT pg_catalog.setval('public.userauths_userconsent_id_seq', 1, false);

-- Конец дампа 