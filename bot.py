import subprocess
import telebot
from telebot import types

TOKEN = "9099870218:AAGvAjlOdY-DU_3S9aAxfegPsT6Y0o7lCNA"
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("📡 بث فردي")
    item2 = types.KeyboardButton("📡 بث جماعي")
    item3 = types.KeyboardButton("📺 القنوات الشغالة")
    item4 = types.KeyboardButton("⏹️ إيقاف البث")
    markup.add(item1, item2, item3, item4)
    
    bot.send_message(
        message.chat.id, 
        "👋 مرحباً بيك\nاختر من الجدول 👇", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "📡 بث فردي")
def single_stream(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "📡 بث فردي\nصيفط رابط القناة (M3U / TS)")
    bot.register_next_step_handler(message, get_m3u)

def get_m3u(message):
    user_data[message.chat.id]['m3u'] = message.text
    bot.send_message(message.chat.id, "🔑 صيفط Stream Key الخاص بفيسبوك")
    bot.register_next_step_handler(message, get_stream_key)

def get_stream_key(message):
    user_data[message.chat.id]['stream_key'] = message.text
    chat_id = message.chat.id
    
    m3u_link = user_data[chat_id]['m3u']
    stream_key = user_data[chat_id]['stream_key']
    
    bot.send_message(chat_id, "⏳ Starting live... wait 15 sec check Facebook")
    
    rtmp_url = f"rtmps://live-api-s.facebook.com:443/rtmp/{stream_key}"
    
    ffmpeg_cmd = [
        'ffmpeg', '-re',
        '-i', m3u_link,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-f', 'flv',
        rtmp_url
    ]
    
    try:
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        user_data[chat_id]['process'] = process
        bot.send_message(chat_id, "✅ بدأ البث بنجاح!")
    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ: {str(e)}")

@bot.message_handler(func=lambda message: message.text == "⏹️ إيقاف البث")
def stop_stream(message):
    chat_id = message.chat.id
    if chat_id in user_data and 'process' in user_data[chat_id]:
        user_data[chat_id]['process'].terminate()
        bot.send_message(chat_id, "⏹️ تم إيقاف البث بنجاح.")
    else:
        bot.send_message(chat_id, "⚠️ لا يوجد بث يعمل حالياً.")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
