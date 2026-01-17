import os
import telebot
from dotenv import load_dotenv
import core.database as database
from telebot import types
import utils

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

database.init_db()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom, sizni eshityapman?")

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    for new_user in message.new_chat_members:
        user_id = new_user.id
        chat_id = message.chat.id
        first_name = new_user.first_name

        bot.delete_message(message.chat.id, message.message_id)

        if database.is_user_exists(user_id):
            sent_msg = bot.send_message(chat_id, f"Eski do'stimiz {first_name} guruhga qaytdi!")
            utils.delete_message_after_delay(bot, chat_id, sent_msg.message_id, 15)
        else:
            try:
                bot.restrict_chat_member(
                    chat_id, 
                    user_id, 
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                )
            except Exception as e:
                print(f"Ruxsatlarni cheklashda xatolik: {e}")

            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton(
                text="🤖 Men bot emasman", 
                callback_data=f"verify_{user_id}"
            )
            markup.add(btn)
            
            sent_msg = bot.send_message(
                chat_id, 
                f"Salom {first_name}! Guruhda yozish uchun tugmani bosing (15 sek):",
                reply_markup=markup
            )
            utils.delete_message_after_delay(bot, chat_id, sent_msg.message_id, 15)
@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def verify_callback(call):
    target_user_id = int(call.data.split('_')[1])
    chat_id = call.message.chat.id
    
    if call.from_user.id == target_user_id:
        # 3. Ruxsatlarni qaytarish (Unmute)
        try:
            bot.restrict_chat_member(
                chat_id, 
                target_user_id,
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            
            # Bazaga saqlash
            user = call.from_user
            u_name = f"@{user.username}" if user.username else "Mavjud emas"
            l_name = user.last_name if user.last_name else "Mavjud emas"
            database.add_member(user.id, user.first_name, l_name, u_name)
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"✅ Tasdiqlandi! Endi yozishingiz mumkin, {user.first_name}."
            )
            utils.delete_message_after_delay(bot, chat_id, call.message.message_id, 5)
            
        except Exception as e:
            bot.answer_callback_query(call.id, "Xatolik yuz berdi!")
    else:
        bot.answer_callback_query(call.id, "Bu tugma siz uchun emas! ❌", show_alert=True)
@bot.message_handler(content_types=['new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo'])
def handle_docs_audio(message):
    bot.delete_message(message.chat.id, message.message_id)



bot.infinity_polling()