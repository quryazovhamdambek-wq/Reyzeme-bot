import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Botni token orqali ulaymiz
bot = telebot.TeleBot('SIZNING_TOKENINGIZ_SHU_YERGA_YOZILADI')

# Foydalanuvchilarning ma'lumotlarini vaqtincha saqlash uchun idish (lug'at)
foydalanuvchilar = {}

# 1-qadam: /start bosilganda ishga tushadi
@bot.message_handler(commands=['start'])
def boshlash(xabar):
    chat_id = xabar.chat.id
    # Foydalanuvchi uchun bo'sh joy ochamiz
    foydalanuvchilar[chat_id] = {}
    
    msg = bot.send_message(chat_id, "Salom! Professional rezyume tayyorlash botiga xush kelibsiz.\n\nIltimos, **Ism va familiyangizni** kiriting:")
    bot.register_next_step_handler(msg, ismni_olish)

# 2-qadam: Ismni saqlab, yoshni so'raydi
def ismni_olish(xabar):
    chat_id = xabar.chat.id
    foydalanuvchilar[chat_id]['ism'] = xabar.text
    
    msg = bot.send_message(chat_id, "Ajoyib! Endi yoshingizni kiriting (masalan: 20):")
    bot.register_next_step_handler(msg, yoshni_olish)

# 3-qadam: Yoshni saqlab, kasbni so'raydi (Tugmalar bilan)
def yoshni_olish(xabar):
    chat_id = xabar.chat.id
    foydalanuvchilar[chat_id]['yosh'] = xabar.text
    
    # Foydalanuvchi qiynalmasligi uchun tayyor kasb tugmalarini chiqaramiz
    tugmalar = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    tugmalar.add(KeyboardButton("Dasturchi 💻"), KeyboardButton("Dizayner 🎨"))
    tugmalar.add(KeyboardButton("Buxgalter 📊"), KeyboardButton("Menejer 📈"))
    
    msg = bot.send_message(chat_id, "Mutaxassisligingizni tanlang yoki o'zingiz yozib yuboring:", reply_markup=tugmalar)
    bot.register_next_step_handler(msg, kasbni_olish)

# 4-qadam: Kasbni saqlab, ish tajribasini so'raydi
def kasbni_olish(xabar):
    chat_id = xabar.chat.id
    foydalanuvchilar[chat_id]['kasb'] = xabar.text
    
    # Tugmalarni o'chirib yuboramiz
    msg = bot.send_message(chat_id, "Qancha ish tajribangiz bor? (Masalan: 1 yil yoki 'Tajribam yo'q')", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, tajribani_olish)

# 5-qadam: Tajribani saqlab, telefon raqamni so'raydi
def tajribani_olish(xabar):
    chat_id = xabar.chat.id
    foydalanuvchilar[chat_id]['tajriba'] = xabar.text
    
    # Telefon raqamni ulashish uchun maxsus tugma
    tugma = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kontakt_tugmasi = KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)
    tugma.add(kontakt_tugmasi)
    
    msg = bot.send_message(chat_id, "Aloqa uchun telefon raqamingizni yuboring (tugmani bosing yoki yozib yuboring):", reply_markup=tugma)
    bot.register_next_step_handler(msg, telefonni_olish)

# 6-qadam: Oxirgi qadam - hamma ma'lumotni jamlab rezyume chiqarish
def telefonni_olish(xabar):
    chat_id = xabar.chat.id
    
    # Agar foydalanuvchi tugmani bosib kontakt yuborsa, raqamni olamiz, aks holda matnni
    if xabar.contact is not None:
        telefon = xabar.contact.phone_number
    else:
        telefon = xabar.text
        
    foydalanuvchilar[chat_id]['telefon'] = telefon
    
    # Xotiradan barcha ma'lumotlarni yig'ib olamiz
    user = foydalanuvchilar[chat_id]
    
    # Tayyor rezyume matni
    rezyume = f"""
📄 **SIZNING TAYYOR REZYUMENGIZ:**

👤 **F.I.O:** {user['ism']}
🎂 **Yosh:** {user['yosh']} yosh
💼 **Kasb:** {user['kasb']}
⏳ **Ish tajribasi:** {user['tajriba']}
📞 **Telefon:** {user['telefon']}

_Tabriklayman! Rezyumengiz muvaffaqiyatli tuzildi._
"""
    
    # Rezyumeni foydalanuvchiga yuboramiz va eski tugmalarni tozalaymiz
    bot.send_message(chat_id, rezyume, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

# Bot uxlab qolmasligi uchun
bot.polling(none_stop=True)
    
