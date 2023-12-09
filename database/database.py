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

    def add_bot(self, bot_id: int, token_bot: str, username: str, status: str, prompt: str, voice_id: str, yoomoney_token: str):
        with self.connection:
            return self.cursor.execute("INSERT INTO bots (bot_id, token_bot, bot_username, status, prompt, voice_id, yoomoney_token) VALUES (?, ?, ?, ?, ?, ?, ?)", (bot_id, token_bot, username, status, prompt, voice_id, yoomoney_token)).lastrowid

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

    def get_total_lenght_by_user(self, user_id, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT SUM(length) FROM history WHERE bot_id = ? AND user_id = ?", (bot_id, user_id)).fetchmany(1)

    def exist_user(self, bot_id, user_id):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM users WHERE bot_id = ? AND user_id = ?", (bot_id, user_id)).fetchmany(1)))
            # return self.cursor.execute("SELECT * FROM users WHERE bot_id = ? AND user_id = ?", (bot_id, user_id)).fetchone()

    def add_user(self, bot_id, user_id, username, join_date):
        with self.connection:
            self.cursor.execute("INSERT INTO users (user_id, bot_id, username, join_date) VALUES (?, ?, ?, ?)",
                                (user_id, bot_id, username, join_date))

    def get_bot_token(self, bot_id):
        with self.connection:
            return self.cursor.execute("SELECT token_bot FROM bots WHERE bot_id = ?", (bot_id, )).fetchmany(1)[0][0]

    def update_prompt(self, bot_id, new_prompt):
        with self.connection:
            self.cursor.execute("UPDATE bots SET prompt = ? WHERE bot_id = ?", (new_prompt, bot_id))

    def update_yoomoney(self, bot_id, new_yoomoney_token):
        with self.connection:
            self.cursor.execute("UPDATE bots SET yoomoney_token = ? WHERE bot_id = ?", (new_yoomoney_token, bot_id))

    def update_voice_id(self, bot_id, voice_id):
        with self.connection:
            self.cursor.execute("UPDATE bots SET voice_id = ? WHERE bot_id = ?", (voice_id, bot_id))