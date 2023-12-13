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

    def add_user(self, bot_id, user_id, username, full_name):
        with self.connection:
            self.cursor.execute("INSERT INTO users (user_id, bot_id, username, join_date, last_message_time, full_name) VALUES (?, ?, ?, ?, ?, ?)",
                                (user_id, bot_id, username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), full_name))

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

    def add_rate(self, bot_id, count_minutes, price):
        with self.connection:
            self.cursor.execute("INSERT INTO rates (bot_id, count_minutes, price) VALUES (?, ?, ?)", (bot_id, count_minutes, price))

    def update_rate(self, rate_id, count_minutes, price):
        with self.connection:
            self.cursor.execute("UPDATE rates SET count_minutes = ?, price = ? WHERE rate_id = ?",
                                (count_minutes, price, rate_id))

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

    def add_payment(self, payment_id, user_id, bot_id, amount, mark_id):
        with self.connection:
            self.cursor.execute("INSERT INTO payments (payment_id, user_id, payment_datetime, amount, bot_id, mark_id) VALUES (?, ?, ?, ?, ?, ?)",
                                (payment_id, user_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), amount, bot_id, mark_id))

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

    def update_mailing(self, bot_id, user_id, type_mailing):
        with self.connection:
            self.cursor.execute("UPDATE users SET %s = 1 WHERE bot_id = ? AND user_id = ?" % type_mailing, (bot_id, user_id))

    def get_payments(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT payment_datetime, amount FROM payments WHERE bot_id = ?", (bot_id, )).fetchall()

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
            users_with_payments = self.cursor.execute("SELECT users.user_id, username, join_date, full_name, amount FROM users LEFT JOIN payments ON payments.user_id = users.user_id WHERE users.utm_mark_id = ? AND payments.mark_id = ?", (mark_id, mark_id)).fetchall()
            all_users = self.cursor.execute("SELECT user_id, username, join_date, full_name FROM users WHERE users.utm_mark_id = ?", (mark_id,)).fetchall()
            return users_with_payments, all_users