import threading

def delete_message_after_delay(bot, chat_id, message_id, delay):
    """
    Belgilangan vaqtdan keyin xabarni o'chirish.
    Bot obyektini ham argument sifatida qabul qiladi.
    """
    timer = threading.Timer(delay, lambda: bot.delete_message(chat_id, message_id))
    timer.start()