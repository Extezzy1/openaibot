from db_ import db

def create_message_promo(promo_id):
    promo = db.get_promo(promo_id)[0]
    count_activation = db.get_count_activation_promo(promo_id)
    count_activation_max = "безлим. " if promo[4] == 0 else promo[4]
    count_activation_by_person_max = "безлим. " if promo[5] == 0 else promo[5]
    date_end = "не ограничен." if promo[6] == "0" else promo[6]
    link = promo[7]
    return f"""Название: <b>{promo[2]}</b>
Процент скидки: <b>{promo[3]}%</b>
Активаций промокода: <b>{count_activation}</b>
Максимум активаций: <b>{count_activation_max}</b>
Максимум активация одним человеком: <b>{count_activation_by_person_max}</b>
Срок действия: <b>{date_end}</b>
Прямая ссылка: {link}"""