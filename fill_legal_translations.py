#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

def create_translation_mappings():
    """Создает сопоставления переводов на основе русских .txt файлов"""
    
    # Основные переводы из русских .txt файлов
    translations = {
        # Основные заголовки
        "HOTEL BOOKING AND CANCELLATION RULES": "ПРАВИЛА БРОНИРОВАНИЯ И ОТМЕНЫ БРОНИРОВАНИЯ",
        "eKol HOTEL BOOKING SYSTEM": "СИСТЕМЫ БРОНИРОВАНИЯ ОТЕЛЕЙ eKol",
        "PAYMENT AND REFUND RULES": "ПРАВИЛА ОПЛАТЫ И ВОЗВРАТА СРЕДСТВ",
        "ALAKOL HOTEL BOOKING SYSTEM": "СИСТЕМЫ БРОНИРОВАНИЯ ОТЕЛЕЙ ALAKOL",
        "PERSONAL DATA PROCESSING CONSENT": "СОГЛАСИЕ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "PRIVACY POLICY": "ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ",
        "PUBLIC OFFER": "ПУБЛИЧНАЯ ОФЕРТА",
        "FOR HOTEL BOOKING SERVICES": "НА ОКАЗАНИЕ УСЛУГ БРОНИРОВАНИЯ ОТЕЛЕЙ",
        "eKol SYSTEM": "СИСТЕМА eKol",
        "USER AGREEMENT": "ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ",
        "AGREEMENT WITH HOTEL OWNERS": "СОГЛАШЕНИЕ С ВЛАДЕЛЬЦАМИ ОТЕЛЕЙ",
        
        # Даты и версии
        "June 19, 2025": "19 Июня, 2025",
        "Effective Date:": "Дата вступления в силу:",
        "Document Version:": "Версия документа:",
        "from the moment of user acceptance": "с момента принятия пользователем",
        
        # Системная информация
        "System:": "Система:",
        "eKol - Hotel Management System": "eKol - Система управления отелями",
        "Payment System:": "Платежная система:",
        "Robokassa (official integration)": "Robokassa (официальная интеграция)",
        "Region:": "Регион:",
        "Alakol, Republic of Kazakhstan": "Алаколь, Республика Казахстан",
        "Time Zone:": "Временная зона:",
        "Kazakhstan/Astana (UTC+5)": "Kazakhstan/Astana (UTC+5)",
        
        # Документация
        "Document updated:": "Документ обновлен:",
        "June 19, 2025, 4:45 AM UTC+5": "19 Июня, 2025, 4:45 AM UTC+5",
        "for": "для",
        
        # Основные разделы
        "1. GENERAL PROVISIONS": "1. ОБЩИЕ ПОЛОЖЕНИЯ",
        "2. BOOKING CONDITIONS": "2. УСЛОВИЯ БРОНИРОВАНИЯ",
        "3. CANCELLATION CONDITIONS": "3. УСЛОВИЯ ОТМЕНЫ",
        "4. BOOKING CHANGES": "4. ИЗМЕНЕНИЕ БРОНИРОВАНИЯ",
        "5. RESPONSIBILITIES OF PARTIES": "5. ОТВЕТСТВЕННОСТЬ СТОРОН",
        "6. DISPUTE RESOLUTION": "6. РАЗРЕШЕНИЕ СПОРОВ",
        "2. PAYMENT METHODS": "2. СПОСОБЫ ОПЛАТЫ",
        "3. PAYMENT STRUCTURE": "3. СТРУКТУРА ПЛАТЕЖЕЙ",
        "4. PAYMENT PROCEDURE": "4. ПРОЦЕДУРА ОПЛАТЫ",
        "5. REFUNDS": "5. ВОЗВРАТ СРЕДСТВ",
        "6. DISPUTE SITUATIONS": "6. СПОРНЫЕ СИТУАЦИИ",
        "2. OPERATOR DETAILS": "2. РЕКВИЗИТЫ ОПЕРАТОРА",
        "3. PERSONAL DATA PROCESSING PURPOSES": "3. ЦЕЛИ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "4. PERSONAL DATA CATEGORIES": "4. КАТЕГОРИИ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "5. PERSONAL DATA PROCESSING METHODS": "5. СПОСОБЫ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "6. PERSONAL DATA PROCESSING CONDITIONS": "6. УСЛОВИЯ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "7. PERSONAL DATA TRANSFER TO THIRD PARTIES": "7. ПЕРЕДАЧА ПЕРСОНАЛЬНЫХ ДАННЫХ ТРЕТЬИМ ЛИЦАМ",
        "8. PROCESSING AND STORAGE TERMS": "8. СРОКИ ОБРАБОТКИ И ХРАНЕНИЯ",
        "9. PERSONAL DATA PROTECTION MEASURES": "9. МЕРЫ ЗАЩИТЫ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "10. PERSONAL DATA SUBJECT RIGHTS": "10. ПРАВА СУБЪЕКТА ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "11. RIGHTS IMPLEMENTATION PROCEDURE": "11. ПОРЯДОК РЕАЛИЗАЦИИ ПРАВ",
        "12. CONSENT WITHDRAWAL": "12. ОТЗЫВ СОГЛАСИЯ",
        "2. LEGAL GROUNDS FOR PERSONAL DATA PROCESSING": "2. ПРАВОВЫЕ ОСНОВАНИЯ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "3. PERSONAL DATA CATEGORIES": "3. КАТЕГОРИИ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "4. PERSONAL DATA PROCESSING PURPOSES": "4. ЦЕЛИ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "5. PERSONAL DATA PROCESSING METHODS": "5. СПОСОБЫ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "6. PERSONAL DATA PROCESSING TERMS": "6. СРОКИ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "7. PERSONAL DATA TRANSFER TO THIRD PARTIES": "7. ПЕРЕДАЧА ПЕРСОНАЛЬНЫХ ДАННЫХ ТРЕТЬИМ ЛИЦАМ",
        "8. CROSS-BORDER PERSONAL DATA TRANSFER": "8. ТРАНСГРАНИЧНАЯ ПЕРЕДАЧА ПЕРСОНАЛЬНЫХ ДАННЫХ",
        "9. SECURITY MEASURES": "9. МЕРЫ БЕЗОПАСНОСТИ",
        "1. DEFINITIONS AND TERMS": "1. ОПРЕДЕЛЕНИЯ И ТЕРМИНЫ",
        "2. CONTRACT SUBJECT": "2. ПРЕДМЕТ ДОГОВОРА",
        "3. CONTRACT CONCLUSION PROCEDURE": "3. ПОРЯДОК ЗАКЛЮЧЕНИЯ ДОГОВОРА",
        "4. RIGHTS AND OBLIGATIONS OF PARTIES": "4. ПРАВА И ОБЯЗАННОСТИ СТОРОН",
        "5. SERVICE DESCRIPTION": "5. ОПИСАНИЕ УСЛУГ",
        "6. SERVICE COST AND PAYMENT PROCEDURE": "6. СТОИМОСТЬ УСЛУГ И ПОРЯДОК ОПЛАТЫ",
        "7. BOOKING CHANGES AND CANCELLATION": "7. ИЗМЕНЕНИЕ И ОТМЕНА БРОНИРОВАНИЯ",
        "2. SERVICE DESCRIPTION": "2. ОПИСАНИЕ УСЛУГ",
        "3. REGISTRATION AND ACCOUNT": "3. РЕГИСТРАЦИЯ И УЧЕТНАЯ ЗАПИСЬ",
        "4. BOOKING PROCEDURE": "4. ПОРЯДОК БРОНИРОВАНИЯ",
        "5. PAYMENT AND PRICING": "5. ОПЛАТА И ЦЕНООБРАЗОВАНИЕ",
        "6. BOOKING CANCELLATION AND REFUNDS": "6. ОТМЕНА БРОНИРОВАНИЯ И ВОЗВРАТ СРЕДСТВ",
        "7. RIGHTS AND OBLIGATIONS OF PARTIES": "7. ПРАВА И ОБЯЗАННОСТИ СТОРОН",
        "8. RESPONSIBILITY OF PARTIES": "8. ОТВЕТСТВЕННОСТЬ СТОРОН",
        "1. PARTIES TO THE AGREEMENT": "1. СТОРОНЫ СОГЛАШЕНИЯ",
        "2. SUBJECT OF AGREEMENT": "2. ПРЕДМЕТ СОГЛАШЕНИЯ",
        "3. COMMISSION AND PAYMENT SYSTEM": "3. КОМИССИЯ И СИСТЕМА ОПЛАТЫ",
        "4. HOTEL OBLIGATIONS": "4. ОБЯЗАННОСТИ ОТЕЛЯ",
        "5. PLATFORM OBLIGATIONS": "5. ОБЯЗАННОСТИ ПЛАТФОРМЫ",
        "6. CANCELLATION AND REFUND CONDITIONS": "6. УСЛОВИЯ ОТМЕНЫ И ВОЗВРАТА",
        "7. QUALITY CONTROL": "7. КОНТРОЛЬ КАЧЕСТВА",
        "8. FORCE MAJEURE": "8. ФОРС-МАЖОР",
        "9. AGREEMENT TERMINATION": "9. РАСТОРЖЕНИЕ СОГЛАШЕНИЯ",
        
        # Контактная информация
        "CONTACT INFORMATION": "КОНТАКТНАЯ ИНФОРМАЦИЯ",
        "FINAL PROVISIONS": "ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ",
        "Platform:": "Платформа:",
        "BIN/IIN:": "БИН/ИИН:",
        "Legal address:": "Юридический адрес:",
        "Phone:": "Телефон:",
        "Email for partners:": "Email для партнеров:",
        "Email for notifications:": "Email для уведомлений:",
        "Contractor:": "Исполнитель:",
        "Company:": "Компания:",
        "Email:": "Email:",
        "Name:": "Наименование:",
        "\"Alakol Booking Ltd\" LLP": "ТОО \"Alakol Booking Ltd\"",
        "BIN:": "БИН:",
        "123456789012 (tentative)": "123456789012 (предполагаемый)",
        "Almaty, Republic of Kazakhstan": "Алматы, Республика Казахстан",
        "[LEGAL ENTITY/IE NAME]": "[НАИМЕНОВАНИЕ ЮРИДИЧЕСКОГО ЛИЦА/ИП]",
        "[BIN/IIN]": "[БИН/ИИН]",
        "[ADDRESS]": "[АДРЕС]",
        "[PHONE]": "[ТЕЛЕФОН]",
        "[EMAIL]": "[EMAIL]",
        "[PARTNER_EMAIL]": "[EMAIL_ПАРТНЕРОВ]",
        
        # Длинные описания
        "These Rules determine the terms and conditions for booking hotel rooms, as well as the conditions for changing and canceling bookings through the website [WEBSITE ADDRESS].": "Настоящие Правила определяют условия и порядок бронирования номеров в отелях, а также условия изменения и отмены бронирования через веб-сайт [АДРЕС САЙТА].",
        
        "The Rules apply to all users of the booking system and are an integral part of the Public Offer for hotel booking services.": "Правила действуют для всех пользователей системы бронирования и являются неотъемлемой частью Публичной оферты на оказание услуг бронирования отелей.",
        
        "By accepting the booking terms, the User agrees to these Rules in full.": "Принимая условия бронирования, Пользователь соглашается с настоящими Правилами в полном объеме.",
        
        "These Rules regulate the procedure for payment of booking services and refunds in the Alakol hotel booking system.": "Настоящие Правила определяют порядок оплаты услуг бронирования отелей и условия возврата денежных средств при использовании системы eKol для региона Алаколь через веб-сайт [АДРЕС САЙТА].",
        
        "The Rules are an integral part of the User Agreement and are mandatory for all system users.": "Правила разработаны в соответствии с законодательством Республики Казахстан и являются неотъемлемой частью Публичной оферты на оказание услуг бронирования.",
        
        "By making a payment, the user confirms agreement with these Rules.": "Используя сервис и производя оплату, Пользователь соглашается с настоящими Правилами в полном объеме.",
        
        "1.4. The eKol system supports multilingual functionality (Kazakh, Russian, English languages) and operates in the Kazakhstan/Astana (UTC+5) time zone.": "1.4. Система eKol поддерживает мультиязычность (казахский, русский, английский языки) и работает в временной зоне Kazakhstan/Astana (UTC+5).",
        
        # Подразделы
        "2.1. Minimum requirements for booking:": "2.1. Минимальные требования для бронирования:",
        "2.2. Prepayment amount:": "2.2. Размер предоплаты:",
        "2.3. Booking confirmation:": "2.3. Подтверждение бронирования:",
        "3.1. General cancellation principles:": "3.1. Общие принципы отмены:",
        "3.2. Cancellation conditions by prepayment amount:": "3.2. Условия отмены в зависимости от размера предоплаты:",
        "3.3. Force majeure circumstances:": "3.3. Форс-мажорные обстоятельства:",
        "4.1. Submitting cancellation request:": "4.1. Подача заявки на отмену:",
        "4.2. Request processing:": "4.2. Обработка заявки:",
        "4.3. Refund:": "4.3. Возврат средств:",
        
        # Списки условий
        "Registration on the website or providing contact information": "Регистрация на сайте или предоставление контактной информации",
        "Selection of hotel, room type, and accommodation dates": "Выбор отеля, типа номера и дат проживания",
        "Agreement to hotel terms and these Rules": "Согласие с условиями отеля и настоящими Правилами",
        "Payment of prepayment in the amount established by the hotel": "Оплата предоплаты в размере, установленном отелем",
        
        "The prepayment amount is determined by each hotel independently": "Размер предоплаты определяется каждым отелем самостоятельно",
        "Prepayment can be 10%, 30%, 50%, 70%, or 100% of the total cost": "Предоплата может составлять 10%, 30%, 50%, 70% или 100% от общей стоимости",
        "The remaining amount is paid at the hotel upon check-in": "Оставшаяся сумма оплачивается в отеле при заселении",
        "With 100% prepayment, no additional payment at the hotel is required": "При 100% предоплате дополнительная оплата в отеле не требуется",
        
        "Booking is considered confirmed after successful prepayment": "Бронирование считается подтвержденным после успешной предоплаты",
        "Confirmation is sent to the specified email within 15 minutes": "Подтверждение отправляется на указанный email в течение 15 минут",
        "The confirmation includes all booking details and hotel contacts": "Подтверждение включает все детали бронирования и контакты отеля",
        
        # Условия отмены
        "IMPORTANT:": "ВАЖНО:",
        "Cancellation terms depend on the amount of prepayment made and time until check-in.": "Условия отмены зависят от размера произведенной предоплаты и времени до заселения.",
        
        "The first 10% of prepayment is a guarantee deposit and is non-refundable when canceled by the client": "Первые 10% предоплаты являются гарантийным депозитом и не возвращаются при отмене клиентом",
        "The remaining part of the prepayment may be refunded depending on cancellation timing": "Оставшаяся часть предоплаты может быть возвращена в зависимости от времени отмены",
        "In force majeure circumstances, the prepayment is refunded in full": "При форс-мажорных обстоятельствах предоплата возвращается полностью",
        
        # Конкретные условия по процентам
        "With 10% prepayment:": "При предоплате 10%:",
        "With 30% prepayment:": "При предоплате 30%:",
        "With 50% prepayment:": "При предоплате 50%:",
        "With 70% prepayment:": "При предоплате 70%:",
        "With 100% prepayment:": "При предоплате 100%:",
        
        "Cancellation at any time: 0% refund (entire amount remains as guarantee deposit)": "Отмена в любое время: 0% возврат (вся сумма остается в качестве гарантийного депозита)",
        "No-show: 0% refund": "Неявка: 0% возврат",
        
        "Cancellation 15+ days before check-in: 20% refund": "Отмена за 15+ дней до заселения: возврат 20%",
        "Cancellation 10-14 days before check-in: 0% refund": "Отмена за 10-14 дней до заселения: возврат 0%",
        "Cancellation 7-9 days before check-in: 0% refund": "Отмена за 7-9 дней до заселения: возврат 0%",
        "Cancellation 36+ hours before check-in: 0% refund": "Отмена за 36+ часов до заселения: возврат 0%",
        "Cancellation less than 36 hours before check-in: 0% refund": "Отмена менее чем за 36 часов до заселения: возврат 0%",
        
        "Cancellation 15+ days before check-in: 40% refund": "Отмена за 15+ дней до заселения: возврат 40%",
        "Cancellation 10-14 days before check-in: 20% refund": "Отмена за 10-14 дней до заселения: возврат 20%",
        
        "Cancellation 15+ days before check-in: 60% refund": "Отмена за 15+ дней до заселения: возврат 60%",
        "Cancellation 10-14 days before check-in: 40% refund": "Отмена за 10-14 дней до заселения: возврат 40%",
        "Cancellation 7-9 days before check-in: 10% refund": "Отмена за 7-9 дней до заселения: возврат 10%",
        
        "Cancellation 15+ days before check-in: 90% refund": "Отмена за 15+ дней до заселения: возврат 90%",
        "Cancellation 10-14 days before check-in: 70% refund": "Отмена за 10-14 дней до заселения: возврат 70%",
        "Cancellation 7-9 days before check-in: 40% refund": "Отмена за 7-9 дней до заселения: возврат 40%",
        "Cancellation 36+ hours before check-in: 20% refund": "Отмена за 36+ часов до заселения: возврат 20%",
        
        # Обстоятельства форс-мажора
        "Natural disasters": "Стихийные бедствия",
        "Military actions or terrorist acts": "Военные действия или террористические акты",
        "Epidemics and pandemics with movement restrictions": "Эпидемии и пандемии с ограничениями передвижения",
        "Hotel closure by government authorities": "Закрытие отеля государственными органами",
        "Other emergencies recognized as force majeure": "Другие чрезвычайные ситуации, признанные форс-мажором",
        
        "In force majeure circumstances, prepayment is refunded in full regardless of cancellation timing.": "При форс-мажорных обстоятельствах предоплата возвращается полностью независимо от времени отмены.",
        
        # Процедуры
        "Request is submitted through personal account on the website": "Заявка подается через личный кабинет на сайте",
        "Or by email with booking number specified": "Или по электронной почте с указанием номера бронирования",
        "Or by phone to customer support": "Или по телефону в службу поддержки клиентов",
        
        "Requests are processed within 1-2 business days": "Заявки обрабатываются в течение 1-2 рабочих дней",
        "Client receives cancellation confirmation by email": "Клиент получает подтверждение отмены по электронной почте",
        "Confirmation specifies the refund amount": "Подтверждение указывает сумму возврата",
        
        "Refund is made using the same method as the original payment": "Возврат производится тем же способом, что и первоначальный платеж",
        "Refund timeframe: 5-10 business days": "Срок возврата: 5-10 рабочих дней",
        "Payment system fees are non-refundable": "Комиссии платежной системы не возвращаются",
        
        # Способы оплаты
        "2.1. Available payment methods:": "2.1. Доступные способы оплаты:",
        "Bank cards (Visa, MasterCard, MIR)": "Банковские карты (Visa, MasterCard, MIR)",
        "Electronic wallets": "Электронные кошельки",
        "Bank transfers": "Банковские переводы",
        "Mobile payments": "Мобильные платежи",
        "Other methods supported by Robokassa payment system": "Другие методы, поддерживаемые платежной системой Robokassa",
        
        "2.2. Payment currency:": "2.2. Валюта платежа:",
        "Main currency: Kazakhstani tenge (KZT)": "Основная валюта: Казахстанский тенге (KZT)",
        "Supported: Russian ruble (RUB), US dollar (USD), Euro (EUR)": "Поддерживаются: Российский рубль (RUB), Доллар США (USD), Евро (EUR)",
        "Conversion is performed at the payment system rate at the time of transaction": "Конвертация производится по курсу платежной системы на момент транзакции",
        
        "2.3. Payment security:": "2.3. Безопасность платежей:",
        "All payments are processed through certified Robokassa system": "Все платежи обрабатываются через сертифицированную систему Robokassa",
        "Compliance with PCI DSS security standards": "Соответствие стандартам безопасности PCI DSS",
        "Data encryption via SSL protocol": "Шифрование данных по протоколу SSL",
        "The system does not store bank card data": "Система не хранит данные банковских карт",
        
        # Структура платежей
        "3.1. Flexible prepayment system:": "3.1. Гибкая система предоплаты:",
        "The prepayment amount is determined by each hotel's policy and can be:": "Размер предоплаты определяется политикой каждого отеля и может составлять:",
        "of the total accommodation cost": "от общей стоимости проживания",
        "of the total accommodation cost (full prepayment)": "от общей стоимости проживания (полная предоплата)",
        
        "3.2. Hotel balance payment:": "3.2. Доплата в отеле:",
        "Balance payment amount is (100% - N%), where N is the prepayment size": "Размер доплаты составляет (100% - N%), где N - размер предоплаты",
        "When N = 100%, no hotel balance payment is required": "При N = 100%, доплата в отеле не требуется",
        "Balance payment is made directly at the hotel upon check-in": "Доплата производится непосредственно в отеле при заселении",
        "Balance payment methods are determined by hotel policy": "Способы доплаты определяются политикой отеля",
        
        "3.3. Platform commission:": "3.3. Комиссия платформы:",
        "Commission size: 10% of total booking cost": "Размер комиссии: 10% от общей стоимости бронирования",
        "Commission is included in the N% prepayment": "Комиссия включена в N% предоплату",
        "Commission is charged on full booking cost": "Комиссия взимается с полной стоимости бронирования",
        
        "IMPORTANT ROUNDING NOTICE:": "ВАЖНОЕ УВЕДОМЛЕНИЕ О ОКРУГЛЕНИЯХ:",
        "Due to percentage calculations when computing prepayment, balance payment, and commissions, all monetary amounts may be rounded with an accuracy of up to 1 (one) tenge up or down.": "В связи с процентными вычислениями при расчете предоплаты, доплаты и комиссий, все денежные суммы могут округляться с погрешностью до 1 (одного) тенге в большую или меньшую сторону.",
        "Due to percentage calculations when computing prepayment, balance payment, and refunds, all monetary amounts may be rounded with an accuracy of up to 1 (one) tenge up or down.": "В связи с процентными вычислениями при расчете предоплаты, доплаты и возвратов средств, все денежные суммы могут округляться с погрешностью до 1 (одного) тенге в большую или меньшую сторону.",
        
        # Процедуры оплаты
        "4.1. Payment stages:": "4.1. Этапы оплаты:",
        "Hotel selection and booking parameters": "Выбор отеля и параметров бронирования",
        "Review of payment and cancellation terms": "Ознакомление с условиями оплаты и отмены",
        "Filling booking data": "Заполнение данных бронирования",
        "Redirect to Robokassa payment system": "Перенаправление в платежную систему Robokassa",
        "Payment method selection and payment data entry": "Выбор способа оплаты и ввод платежных данных",
        "Payment confirmation": "Подтверждение платежа",
        "Booking confirmation receipt": "Получение подтверждения бронирования",
        
        "4.2. Payment confirmation:": "4.2. Подтверждение оплаты:",
        "Successful payment is confirmed instantly": "Успешная оплата подтверждается мгновенно",
        "Confirmation is sent to the specified email": "Подтверждение отправляется на указанный email",
        "Confirmation includes booking number and payment details": "Подтверждение включает номер бронирования и детали платежа",
        "For unsuccessful payment, funds are not charged": "При неуспешной оплате средства не списываются",
        
        "4.3. Payment receipt:": "4.3. Чек об оплате:",
        "Electronic receipt is sent to email within 24 hours": "Электронный чек отправляется на email в течение 24 часов",
        "Receipt contains all necessary details for reporting": "Чек содержит все необходимые детали для отчетности",
        "Receipt duplicate can be requested from customer support": "Дубликат чека можно запросить в службе поддержки",
        
        # Дополнительные переводы для заполнения остальных файлов
        "This Consent is given in accordance with the requirements of the Law of the Republic of Kazakhstan \"On Personal Data and Their Protection\" dated May 21, 2013 No. 94-V.": "Настоящее Согласие дается в соответствии с требованиями Закона Республики Казахстан \"О персональных данных и их защите\" от 21 мая 2013 года № 94-V.",
        
        "Consent is given to the personal data operator - \"Alakol Booking Ltd\" LLP (hereinafter - \"Operator\").": "Согласие дается оператору персональных данных - ТОО \"Alakol Booking Ltd\" (далее - \"Оператор\").",
        
        "Consent applies to personal data processing when using the Alakol hotel booking system.": "Согласие распространяется на обработку персональных данных при использовании системы бронирования отелей Алаколь.",
        
        # Публичная Оферта
        "Offer": "Оферта",
        "this document containing the proposal of [LEGAL ENTITY/IE NAME] to conclude a contract for hotel booking services through the eKol system.": "настоящий документ, содержащий предложение [НАИМЕНОВАНИЕ ЮРИДИЧЕСКОГО ЛИЦА/ИП] о заключении договора на оказание услуг бронирования отелей через систему eKol.",
        
        "Contractor": "Исполнитель",
        "[LEGAL ENTITY/IE NAME], BIN/IIN: [BIN/IIN], legal address: [ADDRESS], conducting activities for providing hotel booking services through the eKol web platform.": "[НАИМЕНОВАНИЕ ЮРИДИЧЕСКОГО ЛИЦА/ИП], БИН/ИИН: [БИН/ИИН], юридический адрес: [АДРЕС], осуществляющий деятельность по оказанию услуг бронирования отелей через веб-платформу eKol.",
        
        "Customer": "Заказчик",
        "an individual who has reached 18 years of age, accepted this offer and concluded a contract with the Contractor.": "физическое лицо, достигшее 18-летнего возраста, принявшее настоящую оферту и заключившее договор с Исполнителем.",
        
        "Website": "Сайт",
        "website [WEBSITE ADDRESS], owned by the Contractor, operating on the technological platform.": "веб-сайт [АДРЕС САЙТА], принадлежащий Исполнителю, работающий на технологической платформе.",
        
        "Services": "Услуги",
        "a complex of services for searching, selecting and booking hotel rooms in the Alakol region, provided by the Contractor through the eKol system.": "комплекс услуг по поиску, подбору и бронированию номеров в отелях региона Алаколь, предоставляемых Исполнителем через систему eKol.",
        
        "Booking": "Бронирование",
        "room reservation in a hotel for a specific period using the eKol system, including 6 stages: hotel search, room selection, availability check, data entry, N% prepayment (where N is determined by hotel policy) and confirmation.": "резервирование номера в отеле на определенный период времени с использованием системы eKol, включающее 6 этапов: поиск отелей, выбор номера, проверку доступности, заполнение данных, предоплату N% (где N определяется политикой отеля) и подтверждение.",
        
        "1.7. The eKol system includes the following modules:": "1.7. Система eKol включает следующие модули:",
        "hotel": "отель",
        "hotel, room, booking management": "управление отелями, номерами, бронированиями",
        "booking": "бронирование",
        "booking functionality": "функциональность бронирования",
        "userauths": "пользователи",
        "authentication and user management with OTP system": "аутентификация и управление пользователями с системой OTP",
        "user_dashboard": "личный_кабинет",
        "user personal account": "личный кабинет пользователя",
        "robokassa": "робокасса",
        "payment system integration": "интеграция платежной системы",
        "search": "поиск",
        "hotel search": "поиск отелей",
        "addon": "дополнения",
        "additional functions": "дополнительные функции",
        
        # Финальные положения
        "This Agreement is governed by the legislation of the Republic of Kazakhstan. All disputes are resolved through negotiation or in court.": "Настоящее Соглашение регулируется законодательством Республики Казахстан. Все споры разрешаются путем переговоров или в суде.",
        
        "System operates in time zone:": "Система работает в часовом поясе:",
        "Payment system:": "Платежная система:",
        "Robokassa with PCI DSS standards support": "Robokassa с поддержкой стандартов PCI DSS",
        
        "This offer is valid until its withdrawal by the Contractor. All disputes are resolved in accordance with the legislation of the Republic of Kazakhstan.": "Настоящая оферта действует до ее отзыва Исполнителем. Все споры разрешаются в соответствии с законодательством Республики Казахстан.",
        
        "This Agreement is written in Kazakh, Russian and English languages. All issues not regulated by this Agreement are resolved in accordance with the current legislation of the Republic of Kazakhstan.": "Настоящее Соглашение составлено на казахском, русском и английском языках. Все вопросы, не урегулированные настоящим Соглашением, разрешаются в соответствии с действующим законодательством Республики Казахстан.",
    }
    
    return translations

def fill_legal_translations():
    """Заполняет пустые переводы в django.po файле"""
    
    po_file_path = "locale/ru/LC_MESSAGES/django.po"
    
    # Читаем файл
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Получаем переводы
    translations = create_translation_mappings()
    
    # Количество заполненных переводов
    filled_count = 0
    
    # Обрабатываем каждый перевод
    for english_text, russian_text in translations.items():
        # Ищем паттерн msgid "english_text"\nmsgstr ""
        pattern = re.compile(
            r'(msgid\s+"' + re.escape(english_text) + r'"\s*\n)msgstr\s+""',
            re.MULTILINE | re.DOTALL
        )
        
        # Заменяем пустые msgstr на русский перевод
        new_content = pattern.sub(
            r'\1msgstr "' + russian_text.replace('"', '\\"') + '"',
            content
        )
        
        if new_content != content:
            filled_count += 1
            content = new_content
            print(f"Заполнен перевод: {english_text[:50]}...")
    
    # Сохраняем обновленный файл
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nВсего заполнено переводов: {filled_count}")
    print("Переводы успешно заполнены в django.po")

if __name__ == "__main__":
    fill_legal_translations() 