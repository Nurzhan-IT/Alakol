-- Insert 10 users into userauths_user
INSERT INTO userauths_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, full_name, phone, gender) VALUES
(1, 'pbkdf2_sha256$260000$salt1234567890$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '1', '', '', '1@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User One', '+12345678901', 'male'),
(2, 'pbkdf2_sha256$260000$salt1234567891$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '2', '', '', '2@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User Two', '+12345678902', 'female'),
(3, 'pbkdf2_sha256$260000$salt1234567892$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '3', '', '', '3@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User Three', '+12345678903', 'male'),
(4, 'pbkdf2_sha256$260000$salt1234567893$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '4', '', '', '4@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User Four', '+12345678904', 'female'),
(5, 'pbkdf2_sha256$260000$salt1234567894$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '5', '', '', '5@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User Five', '+12345678905', 'male'),
(6, 'pbkdf2_sha256$260000$salt1234567895$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '6', '', '', '6@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User Six', '+12345678906', 'female'),
(7, 'pbkdf2_sha256$260000$salt1234567896$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '7', '', '', '7@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User Seven', '+12345678907', 'male'),
(8, 'pbkdf2_sha256$260000$salt1234567897$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '8', '', '', '8@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User Eight', '+12345678908', 'female'),
(9, 'pbkdf2_sha256$260000$salt1234567898$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '9', '', '', '9@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User Nine', '+12345678909', 'male'),
(10, 'pbkdf2_sha256$260000$salt1234567899$+z5z5o5y5x5w5v5u5t5s5r5q5p5o5n5m5l5k5j5i5h5g5f5e5d5c5b5a5', NULL, false, '10', '', '', '10@gmail.com', false, true, '2025-05-13 12:00:00+00', 'User Ten', '+12345678910', 'female');

-- Insert profiles for each user into userauths_profile
INSERT INTO userauths_profile (pid, image, user_id, full_name, phone, gender, country, city, state, address, identity_type, identity_image, facebook, twitter, wallet, verified, date) VALUES
('abcdef1', 'user_1/default.jpg', 1, 'User One', '+12345678901', 'male', 'Kazakhstan', 'Almaty', 'Almaty Region', '123 Main St', 'national_id_card', 'user_1/id.jpg', 'https://facebook.com/user1', 'https://twitter.com/user1', 0.00, true, '2025-05-13 12:00:00+00'),
('abcdef2', 'user_2/default.jpg', 2, 'User Two', '+12345678902', 'female', 'Kazakhstan', 'Astana', 'Astana Region', '456 Oak St', 'drivers_licence', 'user_2/id.jpg', 'https://facebook.com/user2', 'https://twitter.com/user2', 0.00, true, '2025-05-13 12:00:00+00'),
('abcdef3', 'user_3/default.jpg', 3, 'User Three', '+12345678903', 'male', 'Kazakhstan', 'Almaty', 'Almaty Region', '789 Pine St', 'international_passport', 'user_3/id.jpg', 'https://facebook.com/user3', 'https://twitter.com/user3', 0.00, true, '2025-05-13 12:00:00+00'),
('abcdef4', 'user_4/default.jpg', 4, 'User Four', '+12345678904', 'female', 'Kazakhstan', 'Astana', 'Astana Region', '101 Maple St', 'national_id_card', 'user_4/id.jpg', 'https://facebook.com/user4', 'https://twitter.com/user4', 0.00, true, '2025-05-13 12:00:00+00'),
('abcdef5', 'user_5/default.jpg', 5, 'User Five', '+12345678905', 'male', 'Kazakhstan', 'Almaty', 'Almaty Region', '202 Birch St', 'drivers_licence', 'user_5/id.jpg', 'https://facebook.com/user5', 'https://twitter.com/user5', 0.00, true, '2025-05-13 12:00:00+00'),
('abcdef6', 'user_6/default.jpg', 6, 'User Six', '+12345678906', 'female', 'Kazakhstan', 'Astana', 'Astana Region', '303 Cedar St', 'international_passport', 'user_6/id.jpg', 'https://facebook.com/user6', 'https://twitter.com/user6', 0.00, true, '2025-05-13 12:00:00+00'),
('abcdef7', 'user_7/default.jpg', 7, 'User Seven', '+12345678907', 'male', 'Kazakhstan', 'Almaty', 'Almaty Region', '404 Elm St', 'national_id_card', 'user_7/id.jpg', 'https://facebook.com/user7', 'https://twitter.com/user7', 0.00, true, '2025-05-13 12:00:00+00'),
('abcdef8', 'user_8/default.jpg', 8, 'User Eight', '+12345678908', 'female', 'Kazakhstan', 'Astana', 'Astana Region', '505 Spruce St', 'drivers_licence', 'user_8/id.jpg', 'https://facebook.com/user8', 'https://twitter.com/user8', 0.00, true, '2025-05-13 12:00:00+00'),
('abcdef9', 'user_9/default.jpg', 9, 'User Nine', '+12345678909', 'male', 'Kazakhstan', 'Almaty', 'Almaty Region', '606 Willow St', 'international_passport', 'user_9/id.jpg', 'https://facebook.com/user9', 'https://twitter.com/user9', 0.00, true, '2025-05-13 12:00:00+00'),
('abcdef0', 'user_10/default.jpg', 10, 'User Ten', '+12345678910', 'female', 'Kazakhstan', 'Astana', 'Astana Region', '707 Sycamore St', 'national_id_card', 'user_10/id.jpg', 'https://facebook.com/user10', 'https://twitter.com/user10', 0.00, true, '2025-05-13 12:00:00+00');

-- Insert 10 hotels into hotel_hotel
INSERT INTO hotel_hotel (user_id, name, description, image, address, mobile, email, status, check_in_time, check_out_time, views, featured, hid, slug, date) VALUES
(1, 'Hotel One', 'A cozy hotel in Almaty', 'hotel_gallery/test_image.jpeg', '123 Main St, Almaty', '+12345678901', 'hotel1@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'abcdefghij', 'hotel-one-abcd', '2025-05-13 12:00:00+00'),
(2, 'Hotel Two', 'Luxury stay in Astana', 'hotel tym/test_image.jpeg', '456 Oak St, Astana', '+12345678902', 'hotel2@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'bcdefghijk', 'hotel-two-efgh', '2025-05-13 12:00:00+00'),
(3, 'Hotel Three', 'Budget-friendly in Almaty', 'hotel_gallery/test_image.jpeg', '789 Pine St, Almaty', '+12345678903', 'hotel3@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'cdefghijkl', 'hotel-three-ijkl', '2025-05-13 12:00:00+00'),
(4, 'Hotel Four', 'Modern hotel in Astana', 'hotel_gallery/test_image.jpeg', '101 Maple St, Astana', '+12345678904', 'hotel4@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'defghijklm', 'hotel-four-mnop', '2025-05-13 12:00:00+00'),
(5, 'Hotel Five', 'Scenic views in Almaty', 'hotel_gallery/test_image.jpeg', '202 Birch St, Almaty', '+12345678905', 'hotel5@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'efghijklmn', 'hotel-five-qrst', '2025-05-13 12:00:00+00'),
(6, 'Hotel Six', 'Comfort in Astana', 'hotel_gallery/test_image.jpeg', '303 Cedar St, Astana', '+12345678906', 'hotel6@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'fghijklmno', 'hotel-six-uvwx', '2025-05-13 12:00:00+00'),
(7, 'Hotel Seven', 'Affordable stay in Almaty', 'hotel_gallery/test_image.jpeg', '404 Elm St, Almaty', '+12345678907', 'hotel7@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'ghijklmnop', 'hotel-seven-yzab', '2025-05-13 12:00:00+00'),
(8, 'Hotel Eight', 'Elegant hotel in Astana', 'hotel_gallery/test_image.jpeg', '505 Spruce St, Astana', '+12345678908', 'hotel8@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'hijklmnopq', 'hotel-eight-cdef', '2025-05-13 12:00:00+00'),
(9, 'Hotel Nine', 'Relaxing retreat in Almaty', 'hotel_gallery/test_image.jpeg', '606 Willow St, Almaty', '+12345678909', 'hotel9@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'ijklmnopqr', 'hotel-nine-ijkl', '2025-05-13 12:00:00+00'),
(10, 'Hotel Ten', 'Premium stay in Astana', 'hotel_gallery/test_image.jpeg', '707 Sycamore St, Astana', '+12345678910', 'hotel10@example.com', 'Live', '14:00:00', '12:00:00', 0, false, 'jklmnopqrs', 'hotel-ten-qrst', '2025-05-13 12:00:00+00');

-- Insert hotel gallery images into hotel_hotelgallery
INSERT INTO hotel_hotelgallery (hotel_id, image, hgid) VALUES
(1, 'hotel_gallery/test_image.jpeg', 'hgid000001'),
(2, 'hotel_gallery/test_image.jpeg', 'hgid000002'),
(3, 'hotel_gallery/test_image.jpeg', 'hgid000003'),
(4, 'hotel_gallery/test_image.jpeg', 'hgid000004'),
(5, 'hotel_gallery/test_image.jpeg', 'hgid000005'),
(6, 'hotel_gallery/test_image.jpeg', 'hgid000006'),
(7, 'hotel_gallery/test_image.jpeg', 'hgid000007'),
(8, 'hotel_gallery/test_image.jpeg', 'hgid000008'),
(9, 'hotel_gallery/test_image.jpeg', 'hgid000009'),
(10, 'hotel_gallery/test_image.jpeg', 'hgid000010');

-- Insert hotel features into hotel_hotelfeatures
INSERT INTO hotel_hotelfeatures (hotel_id, icon, name, hfid) VALUES
(1, 'wifi.png', 'Free WiFi', 'hfid000001'),
(1, 'house-solid.svg', 'Parking', 'hfid000002'),
(2, 'wifi.png', 'Free WiFi', 'hfid000003'),
(2, 'house-solid.svg', 'Parking', 'hfid000004'),
(3, 'wifi.png', 'Free WiFi', 'hfid000005'),
(3, 'house-solid.svg', 'Parking', 'hfid000006'),
(4, 'wifi.png', 'Free WiFi', 'hfid000007'),
(4, 'house-solid.svg', 'Parking', 'hfid000008'),
(5, 'wifi.png', 'Free WiFi', 'hfid000009'),
(5, 'house-solid.svg', 'Parking', 'hfid000010'),
(6, 'wifi.png', 'Free WiFi', 'hfid000011'),
(6, 'house-solid.svg', 'Parking', 'hfid000012'),
(7, 'wifi.png', 'Free WiFi', 'hfid000013'),
(7, 'house-solid.svg', 'Parking', 'hfid000014'),
(8, 'wifi.png', 'Free WiFi', 'hfid000015'),
(8, 'house-solid.svg', 'Parking', 'hfid000016'),
(9, 'wifi.png', 'Free WiFi', 'hfid000017'),
(9, 'house-solid.svg', 'Parking', 'hfid000018'),
(10, 'wifi.png', 'Free WiFi', 'hfid000019'),
(10, 'house-solid.svg', 'Parking', 'hfid000020');

-- Insert hotel FAQs into hotel_hotelfaqs
INSERT INTO hotel_hotelfaqs (hotel_id, question, answer, date, hfid) VALUES
(1, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000001'),
(2, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000002'),
(3, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000003'),
(4, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000004'),
(5, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000005'),
(6, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000006'),
(7, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000007'),
(8, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000008'),
(9, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000009'),
(10, 'Is breakfast included?', 'Yes, breakfast is included.', '2025-05-13 12:00:00+00', 'faq000010');

-- Insert room types into hotel_roomtype
INSERT INTO hotel_roomtype (hotel_id, type, price, number_of_beds, room_capacity, room_size, rtid, slug, date) VALUES
(1, 'Normal', 100.00, 2, 4, 30, 'rtid000001', 'normal-abcd', '2025-05-13 12:00:00+00'),
(2, 'Normal', 120.00, 2, 4, 32, 'rtid000002', 'normal-efgh', '2025-05-13 12:00:00+00'),
(3, 'Normal', 90.00, 2, 4, 28, 'rtid000003', 'normal-ijkl', '2025-05-13 12:00:00+00'),
(4, 'Normal', 110.00, 2, 4, 30, 'rtid000004', 'normal-mnop', '2025-05-13 12:00:00+00'),
(5, 'Normal', 105.00, 2, 4, 31, 'rtid000005', 'normal-qrst', '2025-05-13 12:00:00+00'),
(6, 'Normal', 115.00, 2, 4, 29, 'rtid000006', 'normal-uvwx', '2025-05-13 12:00:00+00'),
(7, 'Normal', 95.00, 2, 4, 30, 'rtid000007', 'normal-yzab', '2025-05-13 12:00:00+00'),
(8, 'Normal', 125.00, 2, 4, 33, 'rtid000008', 'normal-cdef', '2025-05-13 12:00:00+00'),
(9, 'Normal', 100.00, 2, 4, 30, 'rtid000009', 'normal-ijkl', '2025-05-13 12:00:00+00'),
(10, 'Normal', 130.00, 2, 4, 34, 'rtid000010', 'normal-qrst', '2025-05-13 12:00:00+00');

-- Insert room type descriptions into hotel_roomtypedescription
INSERT INTO hotel_roomtypedescription (hotel_id, room_type_id, description) VALUES
(1, 1, 'Spacious room with modern amenities.'),
(2, 2, 'Comfortable room with city views.'),
(3, 3, 'Cozy room for budget travelers.'),
(4, 4, 'Modern room with free WiFi.'),
(5, 5, 'Room with scenic mountain views.'),
(6, 6, 'Comfortable stay with great service.'),
(7, 7, 'Affordable room with all basics.'),
(8, 8, 'Elegant room with luxury touches.'),
(9, 9, 'Relaxing room for a peaceful stay.'),
(10, 10, 'Premium room with top amenities.');

-- Insert room type gallery images into hotel_roomtypegallery
INSERT INTO hotel_roomtypegallery (hotel_id, room_type_id, image) VALUES
(1, 1, 'room_type_images/test_image.jpeg'),
(2, 2, 'room_type_images/test_image.jpeg'),
(3, 3, 'room_type_images/test_image.jpeg'),
(4, 4, 'room_type_images/test_image.jpeg'),
(5, 5, 'room_type_images/test_image.jpeg'),
(6, 6, 'room_type_images/test_image.jpeg'),
(7, 7, 'room_type_images/test_image.jpeg'),
(8, 8, 'room_type_images/test_image.jpeg'),
(9, 9, 'room_type_images/test_image.jpeg'),
(10, 10, 'room_type_images/test_image.jpeg');

-- Insert room type features into hotel_roomtypefeatures
INSERT INTO hotel_roomtypefeatures (hotel_id, room_type_id, icon, name, hfid) VALUES
(1, 1, 'wifi.png', 'Free WiFi', 'rfid000001'),
(1, 1, 'fan.png', 'Air Conditioning', 'rfid000002'),
(2, 2, 'wifi.png', 'Free WiFi', 'rfid000003'),
(2, 2, 'fan.png', 'Air Conditioning', 'rfid000004'),
(3, 3, 'wifi.png', 'Free WiFi', 'rfid000005'),
(3, 3, 'fan.png', 'Air Conditioning', 'rfid000006'),
(4, 4, 'wifi.png', 'Free WiFi', 'rfid000007'),
(4, 4, 'fan.png', 'Air Conditioning', 'rfid000008'),
(5, 5, 'wifi.png', 'Free WiFi', 'rfid000009'),
(5, 5, 'fan.png', 'Air Conditioning', 'rfid000010'),
(6, 6, 'wifi.png', 'Free WiFi', 'rfid000011'),
(6, 6, 'fan.png', 'Air Conditioning', 'rfid000012'),
(7, 7, 'wifi.png', 'Free WiFi', 'rfid000013'),
(7, 7, 'fan.png', 'Air Conditioning', 'rfid000014'),
(8, 8, 'wifi.png', 'Free WiFi', 'rfid000015'),
(8, 8, 'fan.png', 'Air Conditioning', 'rfid000016'),
(9, 9, 'wifi.png', 'Free WiFi', 'rfid000017'),
(9, 9, 'fan.png', 'Air Conditioning', 'rfid000018'),
(10, 10, 'wifi.png', 'Free WiFi', 'rfid000019'),
(10, 10, 'fan.png', 'Air Conditioning', 'rfid000020');

-- Insert room type detailed features into hotel_roomtypefeaturesdetailed
INSERT INTO hotel_roomtypefeaturesdetailed (hotel_id, room_type_id, type_of_amenity, text, hfid) VALUES
(1, 1, 'private_bathroom', 'Shower and bathtub', 'dfd000001'),
(2, 2, 'view', 'City view', 'dfd000002'),
(3, 3, 'services_amenities', 'Daily housekeeping', 'dfd000003'),
(4, 4, 'private_bathroom', 'Shower and toiletries', 'dfd000004'),
(5, 5, 'view', 'Mountain view', 'dfd000005'),
(6, 6, 'services_amenities', 'Room service', 'dfd000006'),
(7, 7, 'privatevek_bathroom', 'Basic bathroom', 'dfd000007'),
(8, 8, 'view', 'Panoramic view', 'dfd000008'),
(9, 9, 'services_amenities', 'Free breakfast', 'dfd000009'),
(10, 10, 'private_bathroom', 'Luxury bathroom', 'dfd000010');

-- Insert rooms into hotel_room
INSERT INTO hotel_room (hotel_id, room_type_id, room_number, is_available, rid, date) VALUES
(1, 1, '101', true, 'rid000001', '2025-05-13 12:00:00+00'),
(2, 2, '102', true, 'rid000002', '2025-05-13 12:00:00+00'),
(3, 3, '103', true, 'rid000003', '2025-05-13 12:00:00+00'),
(4, 4, '104', true, 'rid000004', '2025-05-13 12:00:00+00'),
(5, 5, '105', true, 'rid000005', '2025-05-13 12:00:00+00'),
(6, 6, '106', true, 'rid000006', '2025-05-13 12:00:00+00'),
(7, 7, '107', true, 'rid000007', '2025-05-13 12:00:00+00'),
(8, 8, '108', true, 'rid000008', '2025-05-13 12:00:00+00'),
(9, 9, '109', true, 'rid000009', '2025-05-13 12:00:00+00'),
(10, 10, '110', true, 'rid000010', '2025-05-13 12:00:00+00');