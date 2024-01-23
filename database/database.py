import datetime
import sqlite3


class Database:

    def __init__(self, file_db):
        self.connection = sqlite3.connect(file_db)
        self.cursor = self.connection.cursor()

    def add_row(self, bot_id, user_id, role, message, length=0):
        with self.connection:
            self.cursor.execute("INSERT INTO history (bot_id, user_id, role, message, length) VALUES (?, ?, ?, ?, ?)", (bot_id, user_id, role, message, length))

    def get_history_by_user_id(self, bot_id, user_id):
        messages = []
        with self.connection:
            query = self.cursor.execute("SELECT role, message FROM history WHERE user_id = ? AND bot_id = ?", (user_id, bot_id)).fetchall()
            for item in query:
                messages.append({"role": item[0], "content": item[1]})
        return messages

    def add_bot(self, bot_id: int, token_bot: str, username: str, status: str, prompt: str, voice_id: str, yoomoney_token: str, price_per_minute: str):
        with self.connection:
            return self.cursor.execute("INSERT INTO bots (bot_id, token_bot, bot_username, status, prompt, voice_id, "
                                       "yoomoney_token, price_per_minute) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                       (bot_id, token_bot, username, status, prompt, voice_id, yoomoney_token,
                                        price_per_minute)).lastrowid

    def get_bots(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM bots").fetchall()

    def get_active_bots(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM bots WHERE status = 'запущен'").fetchall()

    def update_status_bot(self, bot_token, status):
        with self.connection:
            self.cursor.execute("UPDATE bots SET status = ? WHERE token_bot = ?", (status, bot_token))

    def get_prompt(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT prompt FROM bots WHERE bot_id = ?", (bot_id, )).fetchmany(1)

    def get_voice_id(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT voice_id FROM bots WHERE bot_id = ?", (bot_id, )).fetchmany(1)

    def get_price_per_minute(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT price_per_minute FROM bots WHERE bot_id = ?", (bot_id, )).fetchmany(1)

    def get_total_lenght_by_user(self, user_id, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT SUM(length) FROM history WHERE bot_id = ? AND user_id = ?", (bot_id, user_id)).fetchmany(1)

    def exist_user(self, bot_id, user_id):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM users WHERE bot_id = ? AND user_id = ?", (bot_id, user_id)).fetchmany(1)))
            # return self.cursor.execute("SELECT * FROM users WHERE bot_id = ? AND user_id = ?", (bot_id, user_id)).fetchone()

    def add_user(self, bot_id, user_id, username, full_name, utm_mark_id, promo_id):
        with self.connection:
            self.cursor.execute("INSERT INTO users (user_id, bot_id, username, join_date, last_message_time, full_name, utm_mark_id, promo_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (user_id, bot_id, username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), full_name, utm_mark_id, promo_id))

    def get_bot_token(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT token_bot FROM bots WHERE bot_id = ?", (bot_id, )).fetchmany(1)[0][0]

    def update_prompt(self, bot_id, new_prompt):
        with self.connection:
            self.cursor.execute("UPDATE bots SET prompt = ? WHERE bot_id = ?", (new_prompt, bot_id))

    def update_yoomoney(self, bot_id, new_yoomoney_token):
        with self.connection:
            self.cursor.execute("UPDATE bots SET yoomoney_token = ? WHERE bot_id = ?", (new_yoomoney_token, bot_id))

    def update_price_per_minute(self, bot_id, price_per_minute):
        with self.connection:
            self.cursor.execute("UPDATE bots SET price_per_minute = ? WHERE bot_id = ?", (price_per_minute, bot_id))

    def update_voice_id(self, bot_id, voice_id):
        with self.connection:
            self.cursor.execute("UPDATE bots SET voice_id = ? WHERE bot_id = ?", (voice_id, bot_id))

    def add_rate(self, bot_id, count_minutes, price, price_dollar):
        with self.connection:
            self.cursor.execute("INSERT INTO rates (bot_id, count_minutes, price, price_dollar) VALUES (?, ?, ?, ?)",
                                (bot_id, count_minutes, price, price_dollar))

    def update_rate(self, rate_id, count_minutes, price, dollar_price):
        with self.connection:
            self.cursor.execute("UPDATE rates SET count_minutes = ?, price = ?, price_dollar = ? WHERE rate_id = ?",
                                (count_minutes, price, rate_id, dollar_price))

    def get_all_rates_by_bot_id(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM rates WHERE bot_id = ?", (bot_id, )).fetchall()

    def delete_rate(self, rate_id):
        with self.connection:
            self.cursor.execute("DELETE FROM rates WHERE rate_id = ?", (rate_id, ))

    def get_minutes_by_user(self, bot_id, user_id):
        with self.connection:
            return self.cursor.execute("SELECT count_minutes FROM users WHERE bot_id = ? AND user_id = ?", (bot_id, user_id)).fetchmany(1)[0][0]

    def get_count_minutes_by_rate(self, rate_id):
        with self.connection:
            return self.cursor.execute("SELECT bot_id, count_minutes FROM rates WHERE rate_id = ?", (rate_id, )).fetchmany(1)

    def add_minutes(self, user_id, bot_id, count_minutes):
        with self.connection:
            self.cursor.execute("UPDATE users SET count_minutes = count_minutes + ? WHERE user_id = ? AND bot_id = ?", (count_minutes, user_id, bot_id))

    def add_payment(self, bill_id, user_id, bot_id, amount, mark_id, promo_id, pay_type, rate_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO payments (bill_id, user_id, payment_datetime, amount, bot_id, mark_id, promo_id, pay_type, rate_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (bill_id, user_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), amount, bot_id, mark_id, promo_id, pay_type, rate_id)).lastrowid

    def get_yoomoney_token(self, rate_id):
        with self.connection:
            bot_id = self.cursor.execute("SELECT bot_id FROM rates WHERE rate_id = ?", (rate_id, )).fetchmany(1)[0][0]
            return self.cursor.execute("SELECT yoomoney_token FROM bots WHERE bot_id = ?", (bot_id, )).fetchmany(1)[0][0]

    def update_start_photo(self, bot_id, file_id):
        with self.connection:
            self.cursor.execute("UPDATE bots SET start_photo = ? WHERE bot_id = ?", (file_id, bot_id))

    def update_start_text(self, bot_id, text):
        with self.connection:
            self.cursor.execute("UPDATE bots SET start_text = ? WHERE bot_id = ?", (text, bot_id))

    def get_start_message(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT start_text, start_photo FROM bots WHERE bot_id = ?", (bot_id, )).fetchmany(1)

    def update_last_message_time(self, bot_id, user_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET last_message_time = ?, is_send_1_hour = 0, is_send_1_day = 0,"
                                "is_send_2_day = 0, is_send_3_day = 0, is_send_7_day = 0 "
                                "WHERE bot_id = ? AND user_id = ?",
                                (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), bot_id, user_id))

    def get_users_for_mailing(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT user_id, last_message_time, is_send_1_hour, is_send_1_day, is_send_2_day, is_send_3_day,"
                                       "is_send_7_day FROM users WHERE bot_id = ? AND "
                                       "(is_send_1_hour = 0 OR is_send_1_day = 0 OR is_send_2_day = 0 OR is_send_3_day = 0 OR is_send_7_day = 0)", (bot_id, )).fetchall()

    def get_all_users_by_bot_id(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT user_id FROM users WHERE bot_id = ?", (bot_id, )).fetchall()

    def get_users_without_subscribe_by_bot_id(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT history.user_id FROM users LEFT JOIN history ON users.user_id = history.user_id WHERE history.bot_id = ? GROUP BY history.user_id HAVING users.count_minutes * 60 < SUM(history.length)", (bot_id, )).fetchall()

    def update_mailing(self, bot_id, user_id, type_mailing):
        with self.connection:
            self.cursor.execute("UPDATE users SET %s = 1 WHERE bot_id = ? AND user_id = ?" % type_mailing, (bot_id, user_id))

    def get_payments(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT payment_datetime, amount FROM payments WHERE bot_id = ?", (bot_id, )).fetchall()

    def get_payments_for_statistics(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT amount, pay_type FROM payments WHERE bot_id = ?", (bot_id, )).fetchall()

    def get_count_users(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(*) FROM users WHERE bot_id = ?", (bot_id, )).fetchmany(1)[0][0]

    def get_count_users_last_30_days(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(*) FROM users WHERE bot_id = ? AND date(join_date) >= date('now','-30 day')", (bot_id, )).fetchmany(1)[0][0]

    def add_mark(self, bot_id, name, link):
        with self.connection:
            self.cursor.execute("INSERT INTO utm_marks (bot_id, name, link) VALUES (?, ?, ?)", (bot_id, name, link))

    def get_marks(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM utm_marks WHERE bot_id = ?", (bot_id, )).fetchall()

    def get_mark_by_id(self, mark_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM utm_marks WHERE mark_id = ?", (mark_id, )).fetchmany(1)

    def get_bot_username(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT bot_username FROM bots WHERE bot_id = ?", (bot_id, )).fetchmany(1)[0][0]

    def get_conversion_by_mark(self, mark_id):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(*) FROM users WHERE utm_mark_id = ?", (mark_id, )).fetchmany(1)[0][0]

    def get_bot_id_by_mark(self, mark_id):
        with self.connection:
            return self.cursor.execute("SELECT bot_id FROM utm_marks WHERE mark_id = ?", (mark_id, )).fetchmany(1)

    def delete_mark(self, mark_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM utm_marks WHERE mark_id = ?", (mark_id, )).fetchmany(1)

    def get_mark_id_by_user_id(self, bot_id, user_id):
        with self.connection:
            return self.cursor.execute("SELECT utm_mark_id FROM users WHERE user_id = ? AND bot_id = ?", (user_id, bot_id)).fetchmany(1)[0][0]

    def get_count_buy_by_mark(self, mark_id):
        with self.connection:
            return self.cursor.execute("SELECT SUM(amount) FROM payments WHERE mark_id = ?", (mark_id, )).fetchmany(1)[0][0]

    def get_users_by_mark_id(self, mark_id):
        with self.connection:
            users_with_payments = self.cursor.execute("SELECT users.user_id, username, full_name, join_date, amount FROM users LEFT JOIN payments ON payments.user_id = users.user_id WHERE users.utm_mark_id = ? AND payments.mark_id = ?", (mark_id, mark_id)).fetchall()
            all_users = self.cursor.execute("SELECT user_id, username, full_name, join_date FROM users WHERE users.utm_mark_id = ?", (mark_id,)).fetchall()
            return users_with_payments, all_users

    def get_users_by_promo_id(self, promo_id):
        with self.connection:
            return self.cursor.execute("SELECT users.user_id, username, full_name, join_date, amount, utm_mark_id FROM users LEFT JOIN payments ON payments.user_id = users.user_id WHERE payments.promo_id = ?", (promo_id, )).fetchall()

    def get_mark_by_link(self, bot_id, utm_link):
        with self.connection:
            return self.cursor.execute("SELECT mark_id FROM utm_marks WHERE bot_id = ? AND link = ?", (bot_id, utm_link)).fetchmany(1)

    def update_utm_id(self, bot_id, user_id, utm_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET utm_mark_id = ? WHERE bot_id = ? AND user_id = ?", (utm_id, bot_id, user_id))

    def update_promo_id(self, bot_id, user_id, promo_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET promo_id = ? WHERE bot_id = ? AND user_id = ?", (promo_id, bot_id, user_id))

    def get_promocodes(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM promocodes WHERE bot_id = ?", (bot_id, )).fetchall()

    def add_promocode(self, bot_id, title, discount, count_total, count_by_person, date_end, link):
        with self.connection:
            self.cursor.execute("INSERT INTO promocodes (bot_id, name, discount_percent, count_activation_total, "
                                "count_activation_by_person, date_end, link) VALUES (?, ?, ?, ?, ?, ?, ?)", (bot_id, title, discount,
                                                                                                    count_total, count_by_person,
                                                                                                    date_end, link))

    def get_promo(self, promo_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM promocodes WHERE promo_id = ?", (promo_id, )).fetchmany(1)

    def get_count_activation_promo(self, promo_id):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(*) FROM payments WHERE promo_id = ?", (promo_id, )).fetchmany(1)[0][0]

    def delete_promo(self, promo_id):
        with self.connection:
            self.cursor.execute("DELETE FROM promocodes WHERE promo_id = ?", (promo_id, ))
            self.cursor.execute("DELETE FROM promocodes_users WHERE promo_id = ?", (promo_id, ))

    def update_promocode(self, promo_id, title, value):
        with self.connection:
            self.cursor.execute("UPDATE promocodes SET %s = ? WHERE promo_id = ?" % title, (value, promo_id))

    def check_promo(self, bot_id, promo_title, user_id):
        with self.connection:
            query = self.cursor.execute("SELECT promo_id, discount_percent, count_activation_total, count_activation_by_person, date_end FROM promocodes WHERE bot_id = ? AND name = ?", (bot_id, promo_title)).fetchmany(1)
            if len(query) > 0:
                promo_id = query[0][0]
                total_activation = self.cursor.execute("SELECT COUNT(*) FROM payments WHERE promo_id = ?", (promo_id, )).fetchmany(1)[0][0]
                total_activation_by_person = self.cursor.execute("SELECT COUNT(*) FROM payments WHERE promo_id = ? AND user_id = ?", (promo_id, user_id)).fetchmany(1)[0][0]

                if (total_activation < query[0][2] or query[0][2] == 0) and \
                    (total_activation_by_person < query[0][3] or query[0][3] == 0) and \
                    (query[0][4] == "0" or datetime.datetime.strptime(query[0][4], "%Y-%m-%d") < datetime.datetime.now()):
                    return promo_id, query[0][1]
            return 0, 0

    def get_status_bot(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT status FROM bots WHERE bot_id = ?", (bot_id, )).fetchmany(1)[0][0]

    def add_mailing(self, bot_id, text, photo_path, video_path, document_path, type_, admin_id, msg_id):
        with self.connection:
            self.cursor.execute("INSERT INTO mailings (bot_id, text, photo, video, document, type, admin_id, msg_id_admin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (bot_id, text, photo_path, video_path, document_path, type_, admin_id, msg_id))

    def get_mailing(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM mailings WHERE bot_id = ?", (bot_id, )).fetchmany(1)

    def update_mailing_done(self, mailing_id, count_send):
        with self.connection:
            self.cursor.execute("UPDATE mailings SET is_done = 1, count_send = ? WHERE mailing_id = ?", (count_send, mailing_id))

    def delete_mailing(self, mailing_id):
        with self.connection:
            self.cursor.execute("DELETE FROM mailings WHERE mailing_id = ?", (mailing_id, ))

    def get_pay_types(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM manual_pay_types WHERE bot_id = ?", (bot_id, )).fetchall()

    def add_pay_type(self, bot_id, name, description):
        with self.connection:
            self.cursor.execute("INSERT INTO manual_pay_types (bot_id, name, description) VALUES (?, ?, ?)", (bot_id, name, description))

    def get_pay_type_by_id(self, type_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM manual_pay_types WHERE type_id = ?", (type_id, )).fetchmany(1)[0]

    def update_pay_type(self, pay_type_id, title, value):
        with self.connection:
            self.cursor.execute("UPDATE manual_pay_types SET %s = ? WHERE type_id = ?" % title, (value, pay_type_id))

    def update_status_pay_type(self, pay_type_id):
        with self.connection:
            is_enable = self.cursor.execute("SELECT is_enable FROM manual_pay_types WHERE type_id = ?", (pay_type_id, )).fetchmany(1)[0][0]
            value = 0 if is_enable else 1
            self.cursor.execute("UPDATE manual_pay_types SET is_enable = ? WHERE type_id = ?", (value, pay_type_id))

    def delete_pay_type(self, pay_type_id):
        with self.connection:
            self.cursor.execute("DELETE FROM manual_pay_types WHERE type_id = ?", (pay_type_id, ))

    def get_amount_by_rate_id(self, rate_id):
        with self.connection:
            return self.cursor.execute("SELECT count_minutes, price, price_dollar FROM rates WHERE rate_id = ?", (rate_id, )).fetchmany(1)[0]

    def get_promo_by_link(self, link):
        with self.connection:
            return self.cursor.execute("SELECT * FROM promocodes WHERE link = ?", (link, )).fetchmany(1)

    def get_promo_by_name(self, name, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM promocodes WHERE name = ? and bot_id = ?", (name, bot_id)).fetchmany(1)

    def add_feedback_message(self, user_id, bot_id, message_text, user_message_id, video=None, photo=None, document=None):
        with self.connection:
            self.cursor.execute("INSERT INTO feedback_messages (user_id, bot_id, text, photo, document, video, user_message_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (user_id, bot_id, message_text, photo, document, video, user_message_id))

    def get_feedback_messages_not_send(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM feedback_messages WHERE is_send = 0").fetchall()

    def get_feedback_messages_not_answer(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM feedback_messages WHERE is_answer = 0 AND answer_text "
                                       "IS NOT NULL AND bot_id = ?",
                                       (bot_id, )).fetchall()

    def update_status_feedback_message(self, name, value):
        with self.connection:
            self.cursor.execute("UPDATE feedback_messages SET %s = ?" % name, (value, ))

    def get_user_by_user_id(self, user_id, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE user_id = ? AND bot_id = ?", (user_id, bot_id)).fetchmany(1)

    def update_answer_feedback(self, message_id, text, photo=None, document=None, video=None):
        with self.connection:
            self.cursor.execute("UPDATE feedback_messages SET answer_text = ?, photo_answer = ?, document_answer = ?, video_answer = ? WHERE id = ?",
                                (text, photo, document, video, message_id))

    def check_answer_message(self, message_id):
        with self.connection:
            return bool(self.cursor.execute("SELECT is_answer FROM feedback_messages WHERE id = ?", (message_id, )).fetchmany(1)[0][0])

    def ban_user(self, user_id, bot_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET is_ban = 1 WHERE user_id = ? AND bot_id = ?", (user_id, bot_id))

    def get_payment_by_row_id(self, row_id):
        with self.connection:
            return bool(self.cursor.execute("SELECT * FROM payments WHERE payment_id = ?", (row_id, )).fetchmany(1)[0][8])

    def update_payment_row(self, row_id, is_successfull):
        with self.connection:
            self.cursor.execute("UPDATE payments SET is_check_admin = 1, is_successfull = ? WHERE payment_id = ?", (row_id, is_successfull))

    def update_mailing_count(self, mailing_id, counter, total_counter):
        with self.connection:
            self.cursor.execute("UPDATE mailings SET count_send = ?, total_count_send = ? WHERE mailing_id = ?", (counter, total_counter, mailing_id))

    def update_payment_done(self, bill_id, bot_id):
        with self.connection:
            self.cursor.execute("UPDATE payments SET is_successfull = 1 WHERE bill_id = ? AND bot_id = ?", (bill_id, bot_id))
            # self.cursor.execute("UPDATE payments SET is_successfull = 1 WHERE bill_id = ?", (bill_id, ))

    def get_subscribe_not_updated_after_payment(self, bot_id, pay_type="yoomoney"):
        with self.connection:
            return self.cursor.execute("SELECT * FROM payments WHERE bot_id = ? AND is_successfull = 1 AND is_update_subscribe = 0 AND pay_type = ?", (bot_id, pay_type, )).fetchall()

    def update_subscribe(self, payment_id):
        with self.connection:
            self.cursor.execute("UPDATE payments SET is_update_subscribe = 1 WHERE payment_id = ?", (payment_id, ))

    def get_successfull_subscribe(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM payments WHERE is_successfull = 1 AND is_send_to_admin = 0").fetchall()

    def update_is_send_admin_about_new_subscribe(self, payment_id):
        with self.connection:
            self.cursor.execute("UPDATE payments SET is_send_to_admin = 1 WHERE payment_id = ?", (payment_id, ))