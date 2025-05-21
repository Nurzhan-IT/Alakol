--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-05-19 22:08:22

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5286 (class 0 OID 16409)
-- Dependencies: 224
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.auth_group VALUES (1, 'Manager');


--
-- TOC entry 5288 (class 0 OID 16417)
-- Dependencies: 226
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.auth_group_permissions VALUES (13, 1, 13);
INSERT INTO public.auth_group_permissions VALUES (14, 1, 14);
INSERT INTO public.auth_group_permissions VALUES (15, 1, 15);
INSERT INTO public.auth_group_permissions VALUES (16, 1, 16);
INSERT INTO public.auth_group_permissions VALUES (26, 1, 98);
INSERT INTO public.auth_group_permissions VALUES (28, 1, 100);
INSERT INTO public.auth_group_permissions VALUES (49, 1, 25);
INSERT INTO public.auth_group_permissions VALUES (50, 1, 26);
INSERT INTO public.auth_group_permissions VALUES (52, 1, 28);
INSERT INTO public.auth_group_permissions VALUES (57, 1, 21);
INSERT INTO public.auth_group_permissions VALUES (60, 1, 24);
INSERT INTO public.auth_group_permissions VALUES (61, 1, 29);
INSERT INTO public.auth_group_permissions VALUES (62, 1, 30);
INSERT INTO public.auth_group_permissions VALUES (63, 1, 31);
INSERT INTO public.auth_group_permissions VALUES (64, 1, 32);
INSERT INTO public.auth_group_permissions VALUES (65, 1, 37);
INSERT INTO public.auth_group_permissions VALUES (66, 1, 38);
INSERT INTO public.auth_group_permissions VALUES (67, 1, 39);
INSERT INTO public.auth_group_permissions VALUES (68, 1, 40);
INSERT INTO public.auth_group_permissions VALUES (73, 1, 41);
INSERT INTO public.auth_group_permissions VALUES (74, 1, 42);
INSERT INTO public.auth_group_permissions VALUES (75, 1, 43);
INSERT INTO public.auth_group_permissions VALUES (76, 1, 44);
INSERT INTO public.auth_group_permissions VALUES (81, 1, 49);
INSERT INTO public.auth_group_permissions VALUES (82, 1, 50);
INSERT INTO public.auth_group_permissions VALUES (83, 1, 51);
INSERT INTO public.auth_group_permissions VALUES (84, 1, 52);
INSERT INTO public.auth_group_permissions VALUES (104, 1, 64);
INSERT INTO public.auth_group_permissions VALUES (109, 1, 69);
INSERT INTO public.auth_group_permissions VALUES (110, 1, 70);
INSERT INTO public.auth_group_permissions VALUES (111, 1, 71);
INSERT INTO public.auth_group_permissions VALUES (112, 1, 72);
INSERT INTO public.auth_group_permissions VALUES (117, 1, 73);
INSERT INTO public.auth_group_permissions VALUES (118, 1, 74);
INSERT INTO public.auth_group_permissions VALUES (119, 1, 75);
INSERT INTO public.auth_group_permissions VALUES (120, 1, 76);
INSERT INTO public.auth_group_permissions VALUES (121, 1, 77);
INSERT INTO public.auth_group_permissions VALUES (122, 1, 78);
INSERT INTO public.auth_group_permissions VALUES (123, 1, 79);
INSERT INTO public.auth_group_permissions VALUES (124, 1, 80);
INSERT INTO public.auth_group_permissions VALUES (125, 1, 81);
INSERT INTO public.auth_group_permissions VALUES (126, 1, 82);
INSERT INTO public.auth_group_permissions VALUES (127, 1, 83);
INSERT INTO public.auth_group_permissions VALUES (128, 1, 84);
INSERT INTO public.auth_group_permissions VALUES (129, 1, 45);
INSERT INTO public.auth_group_permissions VALUES (130, 1, 46);
INSERT INTO public.auth_group_permissions VALUES (131, 1, 47);
INSERT INTO public.auth_group_permissions VALUES (132, 1, 48);
INSERT INTO public.auth_group_permissions VALUES (147, 1, 92);
INSERT INTO public.auth_group_permissions VALUES (148, 1, 89);
INSERT INTO public.auth_group_permissions VALUES (149, 1, 90);
INSERT INTO public.auth_group_permissions VALUES (150, 1, 91);


--
-- TOC entry 5284 (class 0 OID 16403)
-- Dependencies: 222
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.auth_permission VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO public.auth_permission VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO public.auth_permission VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO public.auth_permission VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO public.auth_permission VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO public.auth_permission VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO public.auth_permission VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO public.auth_permission VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO public.auth_permission VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO public.auth_permission VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO public.auth_permission VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO public.auth_permission VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO public.auth_permission VALUES (13, 'Can add content type', 4, 'add_contenttype');
INSERT INTO public.auth_permission VALUES (14, 'Can change content type', 4, 'change_contenttype');
INSERT INTO public.auth_permission VALUES (15, 'Can delete content type', 4, 'delete_contenttype');
INSERT INTO public.auth_permission VALUES (16, 'Can view content type', 4, 'view_contenttype');
INSERT INTO public.auth_permission VALUES (17, 'Can add session', 5, 'add_session');
INSERT INTO public.auth_permission VALUES (18, 'Can change session', 5, 'change_session');
INSERT INTO public.auth_permission VALUES (19, 'Can delete session', 5, 'delete_session');
INSERT INTO public.auth_permission VALUES (20, 'Can view session', 5, 'view_session');
INSERT INTO public.auth_permission VALUES (21, 'Can add booking', 7, 'add_booking');
INSERT INTO public.auth_permission VALUES (22, 'Can change booking', 7, 'change_booking');
INSERT INTO public.auth_permission VALUES (23, 'Can delete booking', 7, 'delete_booking');
INSERT INTO public.auth_permission VALUES (24, 'Can view booking', 7, 'view_booking');
INSERT INTO public.auth_permission VALUES (25, 'Can add hotel', 8, 'add_hotel');
INSERT INTO public.auth_permission VALUES (26, 'Can change hotel', 8, 'change_hotel');
INSERT INTO public.auth_permission VALUES (27, 'Can delete hotel', 8, 'delete_hotel');
INSERT INTO public.auth_permission VALUES (28, 'Can view hotel', 8, 'view_hotel');
INSERT INTO public.auth_permission VALUES (29, 'Can add room', 9, 'add_room');
INSERT INTO public.auth_permission VALUES (30, 'Can change room', 9, 'change_room');
INSERT INTO public.auth_permission VALUES (31, 'Can delete room', 9, 'delete_room');
INSERT INTO public.auth_permission VALUES (32, 'Can view room', 9, 'view_room');
INSERT INTO public.auth_permission VALUES (33, 'Can add room services', 10, 'add_roomservices');
INSERT INTO public.auth_permission VALUES (34, 'Can change room services', 10, 'change_roomservices');
INSERT INTO public.auth_permission VALUES (35, 'Can delete room services', 10, 'delete_roomservices');
INSERT INTO public.auth_permission VALUES (36, 'Can view room services', 10, 'view_roomservices');
INSERT INTO public.auth_permission VALUES (37, 'Can add hotel gallery', 11, 'add_hotelgallery');
INSERT INTO public.auth_permission VALUES (38, 'Can change hotel gallery', 11, 'change_hotelgallery');
INSERT INTO public.auth_permission VALUES (39, 'Can delete hotel gallery', 11, 'delete_hotelgallery');
INSERT INTO public.auth_permission VALUES (40, 'Can view hotel gallery', 11, 'view_hotelgallery');
INSERT INTO public.auth_permission VALUES (41, 'Can add hotel features', 12, 'add_hotelfeatures');
INSERT INTO public.auth_permission VALUES (42, 'Can change hotel features', 12, 'change_hotelfeatures');
INSERT INTO public.auth_permission VALUES (43, 'Can delete hotel features', 12, 'delete_hotelfeatures');
INSERT INTO public.auth_permission VALUES (44, 'Can view hotel features', 12, 'view_hotelfeatures');
INSERT INTO public.auth_permission VALUES (45, 'Can add hotel fa qs', 13, 'add_hotelfaqs');
INSERT INTO public.auth_permission VALUES (46, 'Can change hotel fa qs', 13, 'change_hotelfaqs');
INSERT INTO public.auth_permission VALUES (47, 'Can delete hotel fa qs', 13, 'delete_hotelfaqs');
INSERT INTO public.auth_permission VALUES (48, 'Can view hotel fa qs', 13, 'view_hotelfaqs');
INSERT INTO public.auth_permission VALUES (49, 'Can add Тип комнаты', 6, 'add_roomtype');
INSERT INTO public.auth_permission VALUES (50, 'Can change Тип комнаты', 6, 'change_roomtype');
INSERT INTO public.auth_permission VALUES (51, 'Can delete Тип комнаты', 6, 'delete_roomtype');
INSERT INTO public.auth_permission VALUES (52, 'Can view Тип комнаты', 6, 'view_roomtype');
INSERT INTO public.auth_permission VALUES (53, 'Can add coupon', 14, 'add_coupon');
INSERT INTO public.auth_permission VALUES (54, 'Can change coupon', 14, 'change_coupon');
INSERT INTO public.auth_permission VALUES (55, 'Can delete coupon', 14, 'delete_coupon');
INSERT INTO public.auth_permission VALUES (56, 'Can view coupon', 14, 'view_coupon');
INSERT INTO public.auth_permission VALUES (57, 'Can add coupon users', 15, 'add_couponusers');
INSERT INTO public.auth_permission VALUES (58, 'Can change coupon users', 15, 'change_couponusers');
INSERT INTO public.auth_permission VALUES (59, 'Can delete coupon users', 15, 'delete_couponusers');
INSERT INTO public.auth_permission VALUES (60, 'Can view coupon users', 15, 'view_couponusers');
INSERT INTO public.auth_permission VALUES (61, 'Can add notification', 16, 'add_notification');
INSERT INTO public.auth_permission VALUES (62, 'Can change notification', 16, 'change_notification');
INSERT INTO public.auth_permission VALUES (63, 'Can delete notification', 16, 'delete_notification');
INSERT INTO public.auth_permission VALUES (64, 'Can view notification', 16, 'view_notification');
INSERT INTO public.auth_permission VALUES (65, 'Can add bookmark', 17, 'add_bookmark');
INSERT INTO public.auth_permission VALUES (66, 'Can change bookmark', 17, 'change_bookmark');
INSERT INTO public.auth_permission VALUES (67, 'Can delete bookmark', 17, 'delete_bookmark');
INSERT INTO public.auth_permission VALUES (68, 'Can view bookmark', 17, 'view_bookmark');
INSERT INTO public.auth_permission VALUES (69, 'Can add review', 18, 'add_review');
INSERT INTO public.auth_permission VALUES (70, 'Can change review', 18, 'change_review');
INSERT INTO public.auth_permission VALUES (71, 'Can delete review', 18, 'delete_review');
INSERT INTO public.auth_permission VALUES (72, 'Can view review', 18, 'view_review');
INSERT INTO public.auth_permission VALUES (73, 'Can add room type gallery', 19, 'add_roomtypegallery');
INSERT INTO public.auth_permission VALUES (74, 'Can change room type gallery', 19, 'change_roomtypegallery');
INSERT INTO public.auth_permission VALUES (75, 'Can delete room type gallery', 19, 'delete_roomtypegallery');
INSERT INTO public.auth_permission VALUES (76, 'Can view room type gallery', 19, 'view_roomtypegallery');
INSERT INTO public.auth_permission VALUES (77, 'Can add room type features', 20, 'add_roomtypefeatures');
INSERT INTO public.auth_permission VALUES (78, 'Can change room type features', 20, 'change_roomtypefeatures');
INSERT INTO public.auth_permission VALUES (79, 'Can delete room type features', 20, 'delete_roomtypefeatures');
INSERT INTO public.auth_permission VALUES (80, 'Can view room type features', 20, 'view_roomtypefeatures');
INSERT INTO public.auth_permission VALUES (81, 'Can add room type description', 21, 'add_roomtypedescription');
INSERT INTO public.auth_permission VALUES (82, 'Can change room type description', 21, 'change_roomtypedescription');
INSERT INTO public.auth_permission VALUES (83, 'Can delete room type description', 21, 'delete_roomtypedescription');
INSERT INTO public.auth_permission VALUES (84, 'Can view room type description', 21, 'view_roomtypedescription');
INSERT INTO public.auth_permission VALUES (85, 'Can add room type features detailed', 22, 'add_roomtypefeaturesdetailed');
INSERT INTO public.auth_permission VALUES (86, 'Can change room type features detailed', 22, 'change_roomtypefeaturesdetailed');
INSERT INTO public.auth_permission VALUES (87, 'Can delete room type features detailed', 22, 'delete_roomtypefeaturesdetailed');
INSERT INTO public.auth_permission VALUES (88, 'Can view room type features detailed', 22, 'view_roomtypefeaturesdetailed');
INSERT INTO public.auth_permission VALUES (89, 'Can add Недоступность номера', 23, 'add_roomunavailability');
INSERT INTO public.auth_permission VALUES (90, 'Can change Недоступность номера', 23, 'change_roomunavailability');
INSERT INTO public.auth_permission VALUES (91, 'Can delete Недоступность номера', 23, 'delete_roomunavailability');
INSERT INTO public.auth_permission VALUES (92, 'Can view Недоступность номера', 23, 'view_roomunavailability');
INSERT INTO public.auth_permission VALUES (93, 'Can add user', 24, 'add_user');
INSERT INTO public.auth_permission VALUES (94, 'Can change user', 24, 'change_user');
INSERT INTO public.auth_permission VALUES (95, 'Can delete user', 24, 'delete_user');
INSERT INTO public.auth_permission VALUES (96, 'Can view user', 24, 'view_user');
INSERT INTO public.auth_permission VALUES (97, 'Can add profile', 25, 'add_profile');
INSERT INTO public.auth_permission VALUES (98, 'Can change profile', 25, 'change_profile');
INSERT INTO public.auth_permission VALUES (99, 'Can delete profile', 25, 'delete_profile');
INSERT INTO public.auth_permission VALUES (100, 'Can view profile', 25, 'view_profile');
INSERT INTO public.auth_permission VALUES (101, 'Can add tag', 26, 'add_tag');
INSERT INTO public.auth_permission VALUES (102, 'Can change tag', 26, 'change_tag');
INSERT INTO public.auth_permission VALUES (103, 'Can delete tag', 26, 'delete_tag');
INSERT INTO public.auth_permission VALUES (104, 'Can view tag', 26, 'view_tag');
INSERT INTO public.auth_permission VALUES (105, 'Can add tagged item', 27, 'add_taggeditem');
INSERT INTO public.auth_permission VALUES (106, 'Can change tagged item', 27, 'change_taggeditem');
INSERT INTO public.auth_permission VALUES (107, 'Can delete tagged item', 27, 'delete_taggeditem');
INSERT INTO public.auth_permission VALUES (108, 'Can view tagged item', 27, 'view_taggeditem');


--
-- TOC entry 5344 (class 0 OID 17172)
-- Dependencies: 282
-- Data for Name: booking_roomunavailability; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5298 (class 0 OID 16515)
-- Dependencies: 236
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.django_admin_log VALUES (1, '2025-05-19 19:21:30.229038+05', '1', 'admin', 2, '[{"changed": {"fields": ["Verified"]}}]', 25, 1);
INSERT INTO public.django_admin_log VALUES (2, '2025-05-19 20:08:25.243605+05', '1', 'Manager', 2, '[]', 3, 1);
INSERT INTO public.django_admin_log VALUES (3, '2025-05-19 20:19:58.370298+05', '4', 'manager@gmail.com', 1, '[{"added": {}}]', 24, 1);
INSERT INTO public.django_admin_log VALUES (4, '2025-05-19 20:21:15.242161+05', '4', 'Manager', 2, '[{"changed": {"fields": ["Groups", "Full name", "Username", "Email"]}}]', 24, 1);
INSERT INTO public.django_admin_log VALUES (5, '2025-05-19 20:29:01.328325+05', '1', 'grand-hyat-hotel', 1, '[{"added": {}}, {"added": {"name": "hotel gallery", "object": "grand-hyat-hotel"}}, {"added": {"name": "hotel gallery", "object": "grand-hyat-hotel"}}, {"added": {"name": "hotel gallery", "object": "grand-hyat-hotel"}}, {"added": {"name": "hotel features", "object": "grand-hyat-hotel"}}, {"added": {"name": "hotel features", "object": "grand-hyat-hotel"}}, {"added": {"name": "\u0422\u0438\u043f \u043a\u043e\u043c\u043d\u0430\u0442\u044b", "object": "Basic - grand-hyat-hotel - 10000"}}, {"added": {"name": "\u0422\u0438\u043f \u043a\u043e\u043c\u043d\u0430\u0442\u044b", "object": "Standard - grand-hyat-hotel - 20000"}}]', 8, 1);
INSERT INTO public.django_admin_log VALUES (6, '2025-05-19 20:32:22.403566+05', '1', 'grand-hyat-hotel', 2, '[{"added": {"name": "room type description", "object": "grand-hyat-hotel"}}, {"added": {"name": "room type description", "object": "grand-hyat-hotel"}}, {"added": {"name": "room type gallery", "object": "Basic - grand-hyat-hotel - 10000.00"}}, {"added": {"name": "room type gallery", "object": "Basic - grand-hyat-hotel - 10000.00"}}, {"added": {"name": "room type gallery", "object": "Basic - grand-hyat-hotel - 10000.00"}}, {"added": {"name": "room type gallery", "object": "Basic - grand-hyat-hotel - 10000.00"}}, {"added": {"name": "room type features", "object": "grand-hyat-hotel"}}, {"added": {"name": "room type features detailed", "object": "grand-hyat-hotel"}}, {"added": {"name": "room", "object": "grand-hyat-hotel - Basic -  Room 101"}}, {"added": {"name": "room", "object": "grand-hyat-hotel - Basic -  Room 102"}}, {"added": {"name": "hotel fa qs", "object": "grand-hyat-hotel"}}, {"added": {"name": "hotel fa qs", "object": "grand-hyat-hotel"}}, {"added": {"name": "hotel fa qs", "object": "grand-hyat-hotel"}}]', 8, 1);
INSERT INTO public.django_admin_log VALUES (7, '2025-05-19 20:55:26.970783+05', '1', 'grand-hyat-hotel', 2, '[{"changed": {"fields": ["User"]}}]', 8, 1);


--
-- TOC entry 5282 (class 0 OID 16395)
-- Dependencies: 220
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

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


--
-- TOC entry 5280 (class 0 OID 16387)
-- Dependencies: 218
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.django_migrations VALUES (1, 'contenttypes', '0001_initial', '2025-05-19 19:15:39.315904+05');
INSERT INTO public.django_migrations VALUES (2, 'contenttypes', '0002_remove_content_type_name', '2025-05-19 19:15:39.32497+05');
INSERT INTO public.django_migrations VALUES (3, 'auth', '0001_initial', '2025-05-19 19:15:39.373345+05');
INSERT INTO public.django_migrations VALUES (4, 'auth', '0002_alter_permission_name_max_length', '2025-05-19 19:15:39.380896+05');
INSERT INTO public.django_migrations VALUES (5, 'auth', '0003_alter_user_email_max_length', '2025-05-19 19:15:39.387173+05');
INSERT INTO public.django_migrations VALUES (6, 'auth', '0004_alter_user_username_opts', '2025-05-19 19:15:39.393477+05');
INSERT INTO public.django_migrations VALUES (7, 'auth', '0005_alter_user_last_login_null', '2025-05-19 19:15:39.399567+05');
INSERT INTO public.django_migrations VALUES (8, 'auth', '0006_require_contenttypes_0002', '2025-05-19 19:15:39.403059+05');
INSERT INTO public.django_migrations VALUES (9, 'auth', '0007_alter_validators_add_error_messages', '2025-05-19 19:15:39.411051+05');
INSERT INTO public.django_migrations VALUES (10, 'auth', '0008_alter_user_username_max_length', '2025-05-19 19:15:39.417034+05');
INSERT INTO public.django_migrations VALUES (11, 'auth', '0009_alter_user_last_name_max_length', '2025-05-19 19:15:39.423828+05');
INSERT INTO public.django_migrations VALUES (12, 'auth', '0010_alter_group_name_max_length', '2025-05-19 19:15:39.431124+05');
INSERT INTO public.django_migrations VALUES (13, 'auth', '0011_update_proxy_permissions', '2025-05-19 19:15:39.439637+05');
INSERT INTO public.django_migrations VALUES (14, 'auth', '0012_alter_user_first_name_max_length', '2025-05-19 19:15:39.444937+05');
INSERT INTO public.django_migrations VALUES (15, 'userauths', '0001_initial', '2025-05-19 19:15:39.510194+05');
INSERT INTO public.django_migrations VALUES (16, 'admin', '0001_initial', '2025-05-19 19:15:39.540768+05');
INSERT INTO public.django_migrations VALUES (17, 'admin', '0002_logentry_remove_auto_add', '2025-05-19 19:15:39.551985+05');
INSERT INTO public.django_migrations VALUES (18, 'admin', '0003_logentry_add_action_flag_choices', '2025-05-19 19:15:39.560751+05');
INSERT INTO public.django_migrations VALUES (19, 'taggit', '0001_initial', '2025-05-19 19:15:39.604435+05');
INSERT INTO public.django_migrations VALUES (20, 'taggit', '0002_auto_20150616_2121', '2025-05-19 19:15:39.614353+05');
INSERT INTO public.django_migrations VALUES (21, 'taggit', '0003_taggeditem_add_unique_index', '2025-05-19 19:15:39.666293+05');
INSERT INTO public.django_migrations VALUES (22, 'taggit', '0004_alter_taggeditem_content_type_alter_taggeditem_tag', '2025-05-19 19:15:39.683213+05');
INSERT INTO public.django_migrations VALUES (23, 'taggit', '0005_auto_20220424_2025', '2025-05-19 19:15:39.688909+05');
INSERT INTO public.django_migrations VALUES (24, 'hotel', '0001_initial', '2025-05-19 19:15:39.875387+05');
INSERT INTO public.django_migrations VALUES (25, 'hotel', '0002_auto_20230731_1533', '2025-05-19 19:15:39.903698+05');
INSERT INTO public.django_migrations VALUES (26, 'hotel', '0003_auto_20230731_1623', '2025-05-19 19:15:39.953067+05');
INSERT INTO public.django_migrations VALUES (27, 'hotel', '0004_auto_20230731_1950', '2025-05-19 19:15:39.983449+05');
INSERT INTO public.django_migrations VALUES (28, 'hotel', '0005_auto_20230731_2001', '2025-05-19 19:15:40.063842+05');
INSERT INTO public.django_migrations VALUES (29, 'hotel', '0006_alter_room_room_type', '2025-05-19 19:15:40.102849+05');
INSERT INTO public.django_migrations VALUES (30, 'hotel', '0007_alter_room_room_type', '2025-05-19 19:15:40.146026+05');
INSERT INTO public.django_migrations VALUES (31, 'hotel', '0008_remove_room_price', '2025-05-19 19:15:40.165806+05');
INSERT INTO public.django_migrations VALUES (32, 'hotel', '0009_auto_20230731_2015', '2025-05-19 19:15:40.189656+05');
INSERT INTO public.django_migrations VALUES (33, 'hotel', '0010_rename_rid_roomtype_rtid', '2025-05-19 19:15:40.201535+05');
INSERT INTO public.django_migrations VALUES (34, 'hotel', '0011_roomtype_slug', '2025-05-19 19:15:40.216925+05');
INSERT INTO public.django_migrations VALUES (35, 'hotel', '0012_remove_booking_guest_booking_booking_id_booking_date_and_more', '2025-05-19 19:15:40.393914+05');
INSERT INTO public.django_migrations VALUES (36, 'hotel', '0013_booking_total', '2025-05-19 19:15:40.410405+05');
INSERT INTO public.django_migrations VALUES (37, 'hotel', '0014_booking_total_days', '2025-05-19 19:15:40.427967+05');
INSERT INTO public.django_migrations VALUES (38, 'hotel', '0015_booking_room_type', '2025-05-19 19:15:40.450486+05');
INSERT INTO public.django_migrations VALUES (39, 'hotel', '0016_booking_checked_in_booking_checked_out', '2025-05-19 19:15:40.485521+05');
INSERT INTO public.django_migrations VALUES (40, 'hotel', '0017_staffonduty_activitylog', '2025-05-19 19:15:40.546922+05');
INSERT INTO public.django_migrations VALUES (41, 'hotel', '0018_booking_email_booking_full_name_booking_phone', '2025-05-19 19:15:40.663875+05');
INSERT INTO public.django_migrations VALUES (42, 'hotel', '0019_coupon', '2025-05-19 19:15:40.710267+05');
INSERT INTO public.django_migrations VALUES (43, 'hotel', '0020_booking_coupons', '2025-05-19 19:15:40.751639+05');
INSERT INTO public.django_migrations VALUES (44, 'hotel', '0021_remove_coupon_used_by_couponusers', '2025-05-19 19:15:40.812998+05');
INSERT INTO public.django_migrations VALUES (45, 'hotel', '0022_booking_before_discount_booking_saved', '2025-05-19 19:15:40.856966+05');
INSERT INTO public.django_migrations VALUES (46, 'hotel', '0023_booking_stripe_payment_intent_booking_success_id', '2025-05-19 19:15:40.897524+05');
INSERT INTO public.django_migrations VALUES (47, 'hotel', '0024_booking_payment_status', '2025-05-19 19:15:40.920803+05');
INSERT INTO public.django_migrations VALUES (48, 'hotel', '0025_alter_booking_success_id', '2025-05-19 19:15:40.947022+05');
INSERT INTO public.django_migrations VALUES (49, 'hotel', '0026_alter_booking_user', '2025-05-19 19:15:40.968701+05');
INSERT INTO public.django_migrations VALUES (50, 'hotel', '0027_notification', '2025-05-19 19:15:41.00796+05');
INSERT INTO public.django_migrations VALUES (51, 'hotel', '0028_bookmark', '2025-05-19 19:15:41.052589+05');
INSERT INTO public.django_migrations VALUES (52, 'hotel', '0029_review', '2025-05-19 19:15:41.108337+05');
INSERT INTO public.django_migrations VALUES (53, 'hotel', '0030_booking_checked_in_tracker_and_more', '2025-05-19 19:15:41.157066+05');
INSERT INTO public.django_migrations VALUES (54, 'hotel', '0031_roomtype_image', '2025-05-19 19:15:41.174354+05');
INSERT INTO public.django_migrations VALUES (55, 'hotel', '0032_room_image', '2025-05-19 19:15:41.191737+05');
INSERT INTO public.django_migrations VALUES (56, 'hotel', '0033_remove_roomtype_image', '2025-05-19 19:15:41.209371+05');
INSERT INTO public.django_migrations VALUES (57, 'hotel', '0034_alter_room_image', '2025-05-19 19:15:41.237721+05');
INSERT INTO public.django_migrations VALUES (58, 'hotel', '0035_alter_room_image', '2025-05-19 19:15:41.268687+05');
INSERT INTO public.django_migrations VALUES (59, 'hotel', '0036_roomtype_images', '2025-05-19 19:15:41.287845+05');
INSERT INTO public.django_migrations VALUES (60, 'hotel', '0037_remove_roomtype_images_roomtypeimage', '2025-05-19 19:15:41.334513+05');
INSERT INTO public.django_migrations VALUES (61, 'hotel', '0038_roomtypegallery_delete_roomtypeimage', '2025-05-19 19:15:41.377707+05');
INSERT INTO public.django_migrations VALUES (62, 'hotel', '0039_alter_roomtypegallery_options_remove_room_image', '2025-05-19 19:15:41.408386+05');
INSERT INTO public.django_migrations VALUES (63, 'hotel', '0040_alter_roomtypegallery_room_type', '2025-05-19 19:15:41.507501+05');
INSERT INTO public.django_migrations VALUES (64, 'hotel', '0041_hotel_address_en_hotel_address_kz_hotel_address_ru_and_more', '2025-05-19 19:15:41.754464+05');
INSERT INTO public.django_migrations VALUES (65, 'hotel', '0042_remove_hotel_address_en_remove_hotel_address_kz_and_more', '2025-05-19 19:15:41.828044+05');
INSERT INTO public.django_migrations VALUES (66, 'hotel', '0043_rename_description_kz_hotel_description_kk_and_more', '2025-05-19 19:15:41.899361+05');
INSERT INTO public.django_migrations VALUES (67, 'hotel', '0044_roomtype_description', '2025-05-19 19:15:41.917728+05');
INSERT INTO public.django_migrations VALUES (68, 'hotel', '0045_rename_description_roomtype_room_description', '2025-05-19 19:15:41.936066+05');
INSERT INTO public.django_migrations VALUES (69, 'hotel', '0046_roomtype_room_description_en_and_more', '2025-05-19 19:15:42.022192+05');
INSERT INTO public.django_migrations VALUES (70, 'hotel', '0047_remove_roomtype_type_en_remove_roomtype_type_kk_and_more', '2025-05-19 19:15:42.138851+05');
INSERT INTO public.django_migrations VALUES (71, 'hotel', '0048_remove_hotelfeatures_icon_type', '2025-05-19 19:15:42.15831+05');
INSERT INTO public.django_migrations VALUES (72, 'hotel', '0049_roomtypefeatures', '2025-05-19 19:15:42.201566+05');
INSERT INTO public.django_migrations VALUES (73, 'hotel', '0050_roomtype_room_size', '2025-05-19 19:15:42.220446+05');
INSERT INTO public.django_migrations VALUES (74, 'hotel', '0051_alter_roomtype_room_size', '2025-05-19 19:15:42.238849+05');
INSERT INTO public.django_migrations VALUES (75, 'hotel', '0052_remove_roomtype_room_description_and_more', '2025-05-19 19:15:42.307085+05');
INSERT INTO public.django_migrations VALUES (76, 'hotel', '0053_roomtypedescription', '2025-05-19 19:15:42.350167+05');
INSERT INTO public.django_migrations VALUES (77, 'hotel', '0054_roomtypedescription_description_en_and_more', '2025-05-19 19:15:42.414383+05');
INSERT INTO public.django_migrations VALUES (78, 'hotel', '0055_alter_hotel_name_alter_hotel_name_en_and_more', '2025-05-19 19:15:42.501084+05');
INSERT INTO public.django_migrations VALUES (79, 'hotel', '0056_alter_hotelgallery_hgid', '2025-05-19 19:15:42.517352+05');
INSERT INTO public.django_migrations VALUES (80, 'hotel', '0057_alter_hotelgallery_hgid', '2025-05-19 19:15:42.533582+05');
INSERT INTO public.django_migrations VALUES (81, 'hotel', '0058_alter_hotelfeatures_hfid_alter_hotelgallery_hgid', '2025-05-19 19:15:42.577058+05');
INSERT INTO public.django_migrations VALUES (82, 'hotel', '0059_alter_roomtype_slug', '2025-05-19 19:15:42.606355+05');
INSERT INTO public.django_migrations VALUES (83, 'hotel', '0060_alter_hotelfaqs_hfid_alter_hotelfeatures_hfid_and_more', '2025-05-19 19:15:42.698902+05');
INSERT INTO public.django_migrations VALUES (84, 'hotel', '0061_alter_hotelfaqs_hfid_alter_hotelfeatures_hfid_and_more', '2025-05-19 19:15:42.804767+05');
INSERT INTO public.django_migrations VALUES (85, 'hotel', '0062_alter_hotelfaqs_hfid', '2025-05-19 19:15:42.916682+05');
INSERT INTO public.django_migrations VALUES (86, 'hotel', '0063_alter_roomtype_rtid', '2025-05-19 19:15:42.943395+05');
INSERT INTO public.django_migrations VALUES (87, 'hotel', '0064_alter_room_rid_alter_roomtypefeatures_hfid', '2025-05-19 19:15:42.995705+05');
INSERT INTO public.django_migrations VALUES (88, 'hotel', '0065_roomtypefeaturesdetailed', '2025-05-19 19:15:43.040403+05');
INSERT INTO public.django_migrations VALUES (89, 'hotel', '0066_roomtypefeaturesdetailed_text_en_and_more', '2025-05-19 19:15:43.098716+05');
INSERT INTO public.django_migrations VALUES (90, 'hotel', '0067_hotel_check_in_time_hotel_check_out_time', '2025-05-19 19:15:43.154041+05');
INSERT INTO public.django_migrations VALUES (91, 'hotel', '0068_remove_payment_fields', '2025-05-19 19:15:43.208207+05');
INSERT INTO public.django_migrations VALUES (92, 'hotel', '0069_booking_inv_id', '2025-05-19 19:15:43.236003+05');
INSERT INTO public.django_migrations VALUES (93, 'hotel', '0070_remove_booking_inv_id_booking_robokassa_inv_id', '2025-05-19 19:15:43.294112+05');
INSERT INTO public.django_migrations VALUES (94, 'hotel', '0071_alter_booking_robokassa_inv_id', '2025-05-19 19:15:43.333649+05');
INSERT INTO public.django_migrations VALUES (95, 'hotel', '0072_alter_booking_robokassa_inv_id', '2025-05-19 19:15:43.382406+05');
INSERT INTO public.django_migrations VALUES (96, 'hotel', '0073_booked_rooms', '2025-05-19 19:15:43.453944+05');
INSERT INTO public.django_migrations VALUES (97, 'hotel', '0074_delete_booked_rooms', '2025-05-19 19:15:43.460153+05');
INSERT INTO public.django_migrations VALUES (98, 'hotel', '0075_booking_created_at_booking_expires_at_and_more', '2025-05-19 19:15:43.555841+05');
INSERT INTO public.django_migrations VALUES (99, 'booking', '0001_initial', '2025-05-19 19:15:43.593971+05');
INSERT INTO public.django_migrations VALUES (100, 'hotel', '0076_room_creator', '2025-05-19 19:15:43.624105+05');
INSERT INTO public.django_migrations VALUES (101, 'hotel', '0077_remove_room_creator', '2025-05-19 19:15:43.743722+05');
INSERT INTO public.django_migrations VALUES (102, 'hotel', '0078_booking_country_code', '2025-05-19 19:15:43.774142+05');
INSERT INTO public.django_migrations VALUES (103, 'hotel', '0079_remove_staffonduty_booking_remove_hotel_tags_and_more', '2025-05-19 19:15:43.842645+05');
INSERT INTO public.django_migrations VALUES (104, 'hotel', '0080_roomtype_dynamic_pricing', '2025-05-19 19:15:43.881804+05');
INSERT INTO public.django_migrations VALUES (105, 'hotel', '0081_alter_roomtype_dynamic_pricing', '2025-05-19 19:15:43.902195+05');
INSERT INTO public.django_migrations VALUES (106, 'hotel', '0082_priceondate_alter_roomtype_options', '2025-05-19 19:15:43.92621+05');
INSERT INTO public.django_migrations VALUES (107, 'hotel', '0083_delete_priceondate', '2025-05-19 19:15:43.930082+05');
INSERT INTO public.django_migrations VALUES (108, 'hotel', '0084_roomtypedescription_unique_room_type_description', '2025-05-19 19:15:43.955115+05');
INSERT INTO public.django_migrations VALUES (109, 'hotel', '0085_alter_roomtype_type', '2025-05-19 19:15:43.979749+05');
INSERT INTO public.django_migrations VALUES (110, 'robokassa', '0001_initial', '2025-05-19 19:15:43.997864+05');
INSERT INTO public.django_migrations VALUES (111, 'robokassa', '0002_delete_robokassapayment', '2025-05-19 19:15:44.001983+05');
INSERT INTO public.django_migrations VALUES (112, 'search', '0001_initial', '2025-05-19 19:15:44.050299+05');
INSERT INTO public.django_migrations VALUES (113, 'search', '0002_delete_searchhistory', '2025-05-19 19:15:44.05716+05');
INSERT INTO public.django_migrations VALUES (114, 'sessions', '0001_initial', '2025-05-19 19:15:44.078609+05');
INSERT INTO public.django_migrations VALUES (115, 'userauths', '0002_profile_wallet', '2025-05-19 19:15:44.097276+05');
INSERT INTO public.django_migrations VALUES (116, 'userauths', '0003_remove_profile_about_me', '2025-05-19 19:15:44.117593+05');
INSERT INTO public.django_migrations VALUES (117, 'userauths', '0004_remove_profile_postal_code_remove_profile_title', '2025-05-19 19:15:44.160584+05');
INSERT INTO public.django_migrations VALUES (118, 'userauths', '0005_remove_profile_facebook_and_more', '2025-05-19 19:15:44.240419+05');
INSERT INTO public.django_migrations VALUES (119, 'userauths', '0006_alter_user_username', '2025-05-19 20:22:59.677521+05');


--
-- TOC entry 5345 (class 0 OID 17217)
-- Dependencies: 283
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.django_session VALUES ('me201wfy0nm002v3fjam6kjngovcmooj', '.eJxVjDsOwjAQRO_iGkVeO2sWShAFp7DWn8gW4IJNaBB3J5ZSQDfzRvPeyvMyF79Ifvqa1FGB2v2ywPGWWx967VyGjclwZsnXJrlJnesrXx5c76ft8GcpLGVVHAwacgmjDiOFQGwcTqgdmWj3ZjQY15QyEMbRIrGFAKg12AATx4Tq8wU9xzlx:1uH1MS:KS4y3uFxHLwCM7CDCihal9ObK_aA0iVuCSbq5aL6k-c', '2025-06-02 19:21:00.823853+05');
INSERT INTO public.django_session VALUES ('qsc2dxhmloulsmiowa4t9ex6oss3k7y5', '.eJytUcuOwiAU_RfWtgEqWl269xvI5WGptmCATmJM_30Aq9PJbKeLpj3n3HPu44k4TNHwKWjPe4WOiKDNGhMgb9pmQl3Bdq6WzkbfizpL6oUN9dkpPZwW7S8DA8Gk6gNltN0pJrHYtkK0QHfswvCupbLZ0y1lMn0pTVomtw1roSGCMIxJI8gFpGLJ1Ds38vi4ax40eGm4gqgDOj6RNFreeptiKKaswqwih1RQYDfFFU5xwkFNQwGLph-U17kWo3mDhHPJqePSjaOzOQL-OSHoQcvYL-bciWsOIPllXNTDzxlevxZGnYDOg1WVeUCsCv5eyEKfIPTyjd19LzNIcHpqnDuy0yjSNdyFC63CEvAyKExRk_WW15pPS6sbDFOXQJFzq725f6F5XvHhs7oyWTYgafY_Ramz9QDzPH8DEBjPng:1uH3g1:3GEpK77q3dU6jttdcTPzxn-I14BkL0Jn9NxgVnx5Z-Y', '2025-06-02 21:49:21.149939+05');
INSERT INTO public.django_session VALUES ('rypaebce1xvsj7wjf67wjp7124ph0lmy', '.eJytkcFuwyAMht-Fc5lM1qxNj3sRZMBN2JIQAalUVXn3AcmiSLuOAxKf7f-3zYt55wYZnxPJQOh1Jw1GCuz2Yroj_W1HdmMVVDWHmouGnVbs5njgFSSOZu4LLDm2N55yLbDlxJRzSamV2g2DG7MF_rNDoJ50tJu4dOorG4h8dS5SL61JqSJVrs8RB0qg9Tga3j0x8sJTvCxkC39isPqXTd7qDAWk8wa5o3EeFHnp7lKRCZvBKlAiJXtnecvHnL2lwx_0c5ugyr780k0PtiyHeNhXVybLAiLN_qcodXYcIGs8bLDR-c0UAVX9DlxU1ZmfQTf82hjgKGogMB_mcr-y5Qe32qeY:1uH3gA:xe0Thbhz2ECvha5_9vQPq-rvix-Z6yI4AGt_3MnQ6qg', '2025-06-02 21:49:30.754462+05');


--
-- TOC entry 5304 (class 0 OID 16570)
-- Dependencies: 242
-- Data for Name: hotel_booking; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5324 (class 0 OID 16877)
-- Dependencies: 262
-- Data for Name: hotel_booking_coupons; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5320 (class 0 OID 16787)
-- Dependencies: 258
-- Data for Name: hotel_booking_room; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5330 (class 0 OID 16943)
-- Dependencies: 268
-- Data for Name: hotel_bookmark; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5322 (class 0 OID 16849)
-- Dependencies: 260
-- Data for Name: hotel_coupon; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5326 (class 0 OID 16897)
-- Dependencies: 264
-- Data for Name: hotel_couponusers; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5306 (class 0 OID 16582)
-- Dependencies: 244
-- Data for Name: hotel_hotel; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_hotel VALUES (1, 'grand-hyat-hotel', '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', 'hotel_gallery/test_image_hotel_D5gtCKK.jpeg', 'Кабанбай ауыл, шоссейное 15', '877777777777', 'Manager@gmail.com', 'Live', 142, false, 'btukidoopc', 'grand-hyat-hotel', '2025-05-19 20:29:01.296337+05', 4, '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', 'grand-hyat-hotel', 'grand-hyat-hotel', 'grand-hyat-hotel', '14:00:00', '12:00:00');


--
-- TOC entry 5316 (class 0 OID 16698)
-- Dependencies: 254
-- Data for Name: hotel_hotelfaqs; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_hotelfaqs VALUES (1, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', '2025-05-19 20:32:22.393566+05', 'VjKjunASE7', 1, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?');
INSERT INTO public.hotel_hotelfaqs VALUES (2, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?|', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', '2025-05-19 20:32:22.396568+05', 'YBgQa7wBzF', 1, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?|', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?');
INSERT INTO public.hotel_hotelfaqs VALUES (3, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', '2025-05-19 20:32:22.397566+05', '9H5Lgt5t8c', 1, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus?');


--
-- TOC entry 5314 (class 0 OID 16616)
-- Dependencies: 252
-- Data for Name: hotel_hotelfeatures; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_hotelfeatures VALUES (1, 'wifi.png', 'wifi', 'F5HLaC8Mps', 1);
INSERT INTO public.hotel_hotelfeatures VALUES (2, 'fan.png', 'fan', 'dzjFUgc5Ji', 1);


--
-- TOC entry 5312 (class 0 OID 16608)
-- Dependencies: 250
-- Data for Name: hotel_hotelgallery; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_hotelgallery VALUES (1, 'hotel_gallery/Houghton-Hotel-3-20-scaled_20t8Bl0.jpg', 'ZKRdWHAskS', 1);
INSERT INTO public.hotel_hotelgallery VALUES (2, 'hotel_gallery/istockphoto-119926339-612x612_0SoS3eE.jpg', 'Ksi4bw5UR9', 1);
INSERT INTO public.hotel_hotelgallery VALUES (3, 'hotel_gallery/1407953244000-177513283_H2AmFQq.webp', '3vqh9sgbJu', 1);


--
-- TOC entry 5328 (class 0 OID 16922)
-- Dependencies: 266
-- Data for Name: hotel_notification; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5332 (class 0 OID 16964)
-- Dependencies: 270
-- Data for Name: hotel_review; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5334 (class 0 OID 16972)
-- Dependencies: 272
-- Data for Name: hotel_review_helpful; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5308 (class 0 OID 16593)
-- Dependencies: 246
-- Data for Name: hotel_room; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_room VALUES (1, '101', 1, true, 'bSR2wbzBRK', '2025-05-19 20:32:22.388474+05', 1);
INSERT INTO public.hotel_room VALUES (2, '102', 1, true, 'oFeMJSUTKP', '2025-05-19 20:32:22.390498+05', 1);


--
-- TOC entry 5310 (class 0 OID 16602)
-- Dependencies: 248
-- Data for Name: hotel_roomservices; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5318 (class 0 OID 16715)
-- Dependencies: 256
-- Data for Name: hotel_roomtype; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_roomtype VALUES (1, 'Basic', 10000.00, 'EyRhoRMQ5F', '2025-05-19 20:29:01.323301+05', 1, 1, 'basic-7hpv', 1, 10, '{"2025-05-19": 10000, "2025-05-20": 10000, "2025-05-21": 10000, "2025-05-22": 10000, "2025-05-23": 10000, "2025-05-24": 10000, "2025-05-25": 10000, "2025-05-26": 11000, "2025-05-27": 11000, "2025-05-28": 11000, "2025-05-29": 11000, "2025-05-30": 11000, "2025-05-31": 11000, "2025-06-01": 11000, "2025-06-02": 12000, "2025-06-03": 12000, "2025-06-04": 12000, "2025-06-05": 12000, "2025-06-06": 12000, "2025-06-07": 12000, "2025-06-08": 12000, "2025-06-09": 13000, "2025-06-10": 13000, "2025-06-11": 13000, "2025-06-12": 13000, "2025-06-13": 13000, "2025-06-14": 13000, "2025-06-15": 13000, "2025-06-16": 14000, "2025-06-17": 14000, "2025-06-18": 14000, "2025-06-19": 14000, "2025-06-20": 14000, "2025-06-21": 14000, "2025-06-22": 14000}');
INSERT INTO public.hotel_roomtype VALUES (2, 'Standard', 20000.00, 'ZVrj4TEH8Y', '2025-05-19 20:29:01.327327+05', 1, 2, 'standard-dwt6', 2, 20, '{"2025-05-19": 24000, "2025-05-20": 24000, "2025-05-21": 24000, "2025-05-22": 24000, "2025-05-23": 24000, "2025-05-24": 24000, "2025-05-25": 24000, "2025-05-26": 26400, "2025-05-27": 26400, "2025-05-28": 26400, "2025-05-29": 26400, "2025-05-30": 26400, "2025-05-31": 26400, "2025-06-01": 26400, "2025-06-02": 28800, "2025-06-03": 28800, "2025-06-04": 28800, "2025-06-05": 28800, "2025-06-06": 28800, "2025-06-07": 28800, "2025-06-08": 28800, "2025-06-09": 31200, "2025-06-10": 31200, "2025-06-11": 31200, "2025-06-12": 31200, "2025-06-13": 31200, "2025-06-14": 31200, "2025-06-15": 31200, "2025-06-16": 33600, "2025-06-17": 33600, "2025-06-18": 33600, "2025-06-19": 33600, "2025-06-20": 33600, "2025-06-21": 33600, "2025-06-22": 33600}');


--
-- TOC entry 5340 (class 0 OID 17061)
-- Dependencies: 278
-- Data for Name: hotel_roomtypedescription; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_roomtypedescription VALUES (1, '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', 1, 1, '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>');
INSERT INTO public.hotel_roomtypedescription VALUES (2, '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', 1, 2, '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>', '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>

<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec at metus in ex fringilla molestie. Vestibulum ultricies dui sit amet justo iaculis, quis lacinia nunc facilisis. Sed porttitor tempus purus.</p>');


--
-- TOC entry 5338 (class 0 OID 17039)
-- Dependencies: 276
-- Data for Name: hotel_roomtypefeatures; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_roomtypefeatures VALUES (1, 'wifi.png', 'Free wifi in room', 'P2Wijw7Lm3', 1, 1);


--
-- TOC entry 5342 (class 0 OID 17094)
-- Dependencies: 280
-- Data for Name: hotel_roomtypefeaturesdetailed; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_roomtypefeaturesdetailed VALUES (1, 'private_bathroom', 'olor leo. Donec scelerisque sapien sed eros vehicula accumsan. Sed porta egestas scelerisque. Intege', 'TK2oQjNa5L', 1, 1, 'olor leo. Donec scelerisque sapien sed eros vehicula accumsan. Sed porta egestas scelerisque. Intege', 'olor leo. Donec scelerisque sapien sed eros vehicula accumsan. Sed porta egestas scelerisque. Intege', 'olor leo. Donec scelerisque sapien sed eros vehicula accumsan. Sed porta egestas scelerisque. Intege');


--
-- TOC entry 5336 (class 0 OID 17021)
-- Dependencies: 274
-- Data for Name: hotel_roomtypegallery; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.hotel_roomtypegallery VALUES (1, 'room_type_images/376785918.jpg', 1, 1);
INSERT INTO public.hotel_roomtypegallery VALUES (2, 'room_type_images/376785930_Mf9DI2h.jpg', 1, 1);
INSERT INTO public.hotel_roomtypegallery VALUES (3, 'room_type_images/Bellagio-Hotel-Casino-Las-Vegas_P3bRrwX.webp', 1, 1);
INSERT INTO public.hotel_roomtypegallery VALUES (4, 'room_type_images/marquis-3-min.jpg', 1, 1);


--
-- TOC entry 5300 (class 0 OID 16536)
-- Dependencies: 238
-- Data for Name: taggit_tag; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5302 (class 0 OID 16546)
-- Dependencies: 240
-- Data for Name: taggit_taggeditem; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5296 (class 0 OID 16471)
-- Dependencies: 234
-- Data for Name: userauths_profile; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.userauths_profile VALUES (1, 'aidsf3i', 'default.jpg', 'admin', NULL, NULL, NULL, NULL, NULL, true, '2025-05-19 19:19:54.007413+05', 1, 0.00);
INSERT INTO public.userauths_profile VALUES (4, 'dcpquoq', 'default.jpg', 'Manager', NULL, NULL, NULL, NULL, NULL, false, '2025-05-19 20:19:58.355597+05', 4, 0.00);


--
-- TOC entry 5290 (class 0 OID 16449)
-- Dependencies: 228
-- Data for Name: userauths_user; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.userauths_user VALUES (1, 'pbkdf2_sha256$600000$um0lXqXrUP4A1PdjqPPNOJ$6Kxx5/WjwGHZbKx8YLh7YqIsxJkLtC6K46Gp/ducoh8=', '2025-05-19 19:43:55.109241+05', true, '', '', true, true, '2025-05-19 19:19:53.6198+05', NULL, 'admin', 'admin@gmail.com', NULL, NULL, NULL);
INSERT INTO public.userauths_user VALUES (4, 'pbkdf2_sha256$600000$um0lXqXrUP4A1PdjqPPNOJ$6Kxx5/WjwGHZbKx8YLh7YqIsxJkLtC6K46Gp/ducoh8=', NULL, false, '', '', false, true, '2025-05-19 20:18:49+05', 'Manager Manager', 'Manager', 'manager@gmail.com', NULL, NULL, NULL);


--
-- TOC entry 5292 (class 0 OID 16459)
-- Dependencies: 230
-- Data for Name: userauths_user_groups; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--

INSERT INTO public.userauths_user_groups VALUES (2, 4, 1);


--
-- TOC entry 5294 (class 0 OID 16465)
-- Dependencies: 232
-- Data for Name: userauths_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: alakol_admin
--



--
-- TOC entry 5352 (class 0 OID 0)
-- Dependencies: 223
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, true);


--
-- TOC entry 5353 (class 0 OID 0)
-- Dependencies: 225
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 4, true);


--
-- TOC entry 5354 (class 0 OID 0)
-- Dependencies: 221
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 108, true);


--
-- TOC entry 5355 (class 0 OID 0)
-- Dependencies: 281
-- Name: booking_roomunavailability_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.booking_roomunavailability_id_seq', 1, false);


--
-- TOC entry 5356 (class 0 OID 0)
-- Dependencies: 235
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 7, true);


--
-- TOC entry 5357 (class 0 OID 0)
-- Dependencies: 219
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 27, true);


--
-- TOC entry 5358 (class 0 OID 0)
-- Dependencies: 217
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 119, true);


--
-- TOC entry 5359 (class 0 OID 0)
-- Dependencies: 261
-- Name: hotel_booking_coupons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_booking_coupons_id_seq', 1, false);


--
-- TOC entry 5360 (class 0 OID 0)
-- Dependencies: 241
-- Name: hotel_booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_booking_id_seq', 1, false);


--
-- TOC entry 5361 (class 0 OID 0)
-- Dependencies: 257
-- Name: hotel_booking_room_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_booking_room_id_seq', 1, false);


--
-- TOC entry 5362 (class 0 OID 0)
-- Dependencies: 267
-- Name: hotel_bookmark_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_bookmark_id_seq', 1, false);


--
-- TOC entry 5363 (class 0 OID 0)
-- Dependencies: 259
-- Name: hotel_coupon_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_coupon_id_seq', 1, false);


--
-- TOC entry 5364 (class 0 OID 0)
-- Dependencies: 263
-- Name: hotel_couponusers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_couponusers_id_seq', 1, false);


--
-- TOC entry 5365 (class 0 OID 0)
-- Dependencies: 243
-- Name: hotel_hotel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_hotel_id_seq', 1, true);


--
-- TOC entry 5366 (class 0 OID 0)
-- Dependencies: 253
-- Name: hotel_hotelfaqs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_hotelfaqs_id_seq', 3, true);


--
-- TOC entry 5367 (class 0 OID 0)
-- Dependencies: 251
-- Name: hotel_hotelfeatures_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_hotelfeatures_id_seq', 2, true);


--
-- TOC entry 5368 (class 0 OID 0)
-- Dependencies: 249
-- Name: hotel_hotelgallery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_hotelgallery_id_seq', 3, true);


--
-- TOC entry 5369 (class 0 OID 0)
-- Dependencies: 265
-- Name: hotel_notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_notification_id_seq', 1, false);


--
-- TOC entry 5370 (class 0 OID 0)
-- Dependencies: 271
-- Name: hotel_review_helpful_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_review_helpful_id_seq', 1, false);


--
-- TOC entry 5371 (class 0 OID 0)
-- Dependencies: 269
-- Name: hotel_review_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_review_id_seq', 1, false);


--
-- TOC entry 5372 (class 0 OID 0)
-- Dependencies: 245
-- Name: hotel_room_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_room_id_seq', 2, true);


--
-- TOC entry 5373 (class 0 OID 0)
-- Dependencies: 247
-- Name: hotel_roomservices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_roomservices_id_seq', 1, false);


--
-- TOC entry 5374 (class 0 OID 0)
-- Dependencies: 255
-- Name: hotel_roomtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_roomtype_id_seq', 2, true);


--
-- TOC entry 5375 (class 0 OID 0)
-- Dependencies: 277
-- Name: hotel_roomtypedescription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_roomtypedescription_id_seq', 2, true);


--
-- TOC entry 5376 (class 0 OID 0)
-- Dependencies: 275
-- Name: hotel_roomtypefeatures_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_roomtypefeatures_id_seq', 1, true);


--
-- TOC entry 5377 (class 0 OID 0)
-- Dependencies: 279
-- Name: hotel_roomtypefeaturesdetailed_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_roomtypefeaturesdetailed_id_seq', 1, true);


--
-- TOC entry 5378 (class 0 OID 0)
-- Dependencies: 273
-- Name: hotel_roomtypegallery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.hotel_roomtypegallery_id_seq', 4, true);


--
-- TOC entry 5379 (class 0 OID 0)
-- Dependencies: 237
-- Name: taggit_tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.taggit_tag_id_seq', 1, false);


--
-- TOC entry 5380 (class 0 OID 0)
-- Dependencies: 239
-- Name: taggit_taggeditem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.taggit_taggeditem_id_seq', 1, false);


--
-- TOC entry 5381 (class 0 OID 0)
-- Dependencies: 233
-- Name: userauths_profile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.userauths_profile_id_seq', 4, true);


--
-- TOC entry 5382 (class 0 OID 0)
-- Dependencies: 229
-- Name: userauths_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.userauths_user_groups_id_seq', 2, true);


--
-- TOC entry 5383 (class 0 OID 0)
-- Dependencies: 227
-- Name: userauths_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.userauths_user_id_seq', 4, true);


--
-- TOC entry 5384 (class 0 OID 0)
-- Dependencies: 231
-- Name: userauths_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: alakol_admin
--

SELECT pg_catalog.setval('public.userauths_user_user_permissions_id_seq', 1, false);


-- Completed on 2025-05-19 22:08:23

--
-- PostgreSQL database dump complete
--

