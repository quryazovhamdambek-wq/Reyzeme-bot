import logging
import os
from io import BytesIO
from flask import Flask
from threading import Thread

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# ---------------------------------------------------------
# 1. FLASK WEB-SERVER (Render uchun)
# ---------------------------------------------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot muvaffaqiyatli ishlamoqda!"

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------------------------------------------------
# 2. SOZLAMALAR VA BOSQICHLAR
# ---------------------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8941048533:AAFJUlaY7aBxd3J7nZOMBAsk9Myl7eYBIW0"
CHANNEL_USERNAME = "@Rezyumelar_Uz"

# Conversation bosqichlari
(
    CHECK_SUB,
    NAME,
    AGE,
    JOB,
    TG_USER,
    PHONE,
    REGION,
    PRICE,
    TIME,
    GOAL,
    FORMAT_CHOICE
) = range(11)

# ---------------------------------------------------------
# 3. KANALGA OBUNA TEKSHIRISH
# ---------------------------------------------------------
async def is_subscribed(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

# ---------------------------------------------------------
# 4. HANDLERLAR (SAVOL-JAVOB RO'YXATI)
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    
    # Obunani tekshiramiz
    if not await is_subscribed(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Botdan foydalanish uchun avval {CHANNEL_USERNAME} kanaliga obuna bo'ling!",
            reply_markup=reply_markup
        )
        return CHECK_SUB

    await update.message.reply_text("Assalomu alaykum! Rezyume yaratishni boshlaymiz.\n\n👨‍💼 **Xodim** (Ism va Familiyangizni kiriting):")
    return NAME

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if await is_subscribed(context.bot, user_id):
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="Rahmat! Obuna tasdiqlandi. 🎉\n\n👨‍💼 **Xodim** (Ism va Familiyangizni kiriting):"
        )
        return NAME
    else:
        await query.message.reply_text(f"Hali obuna bo'lmadingiz. Iltimos, {CHANNEL_USERNAME} kanaliga a'zo bo'ling.")
        return CHECK_SUB

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("🕑 **Yosh:** (Yoshingizni kiriting, masalan: 22):")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['age'] = update.message.text
    await update.message.reply_text("📚 **Soha:** (Sohangiz yoki kasbingizni kiriting, masalan: Python Dasturchi):")
    return JOB

async def get_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['job'] = update.message.text
    username = update.effective_user.username
    default_tg = f"@{username}" if username else "Kiritilmagan"
    context.user_data['tg'] = default_tg
    
    await update.message.reply_text(f"🇺🇿 **Telegram:** (Telegram usernamesingiz, masalan: {default_tg}):")
    return TG_USER

async def get_tg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tg'] = update.message.text
    reply_keyboard = [[{"text": "📱 Telefon raqamni yuborish", "request_contact": True}]]
    await update.message.reply_text(
        "📞 **Aloqa:** (Telefon raqamingizni kiriting yoki tugmani bosing):",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        context.user_data['phone'] = update.message.contact.phone_number
    else:
        context.user_data['phone'] = update.message.text
    
    await update.message.reply_text("🌐 **Hudud:** (Yashaydigan joyingiz, masalan: Toshkent sh.):", reply_markup=ReplyKeyboardRemove())
    return REGION

async def get_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['region'] = update.message.text
    await update.message.reply_text("💰 **Narxi:** (Kutilayotgan maosh, masalan: 500$ yoki Kelishiladi):")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['price'] = update.message.text
    await update.message.reply_text("🕰 **Murojaat qilish vaqti:** (Masalan: 09:00 - 18:00):")
    return TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['time'] = update.message.text
    await update.message.reply_text("🔎 **Maqsad:** (Qisqacha maqsadingiz yoki tajribangiz haqida yozing):")
    return GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['goal'] = update.message.text
    
    # Format tanlash uchun tugmalar
    keyboard = [
        [InlineKeyboardButton("💬 Telegram Post ko'rinishida", callback_data="fmt_post")],
        [InlineKeyboardButton("📄 PDF Hujjat ko'rinishida", callback_data="fmt_pdf")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Rezyume qanday formatda tayyorlansin?", reply_markup=reply_markup)
    return FORMAT_CHOICE

# ---------------------------------------------------------
# 5. POST VA PDF YARATISH
# ---------------------------------------------------------
async def generate_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    choice = query.data
    data = context.user_data

    post_text = (
        "Ish joyi kerak:\n\n"
        f"👨‍💼 Xodim: {data.get('name')}\n"
        f"🕑 Yosh: {data.get('age')}\n"
        f"📚 Soha: {data.get('job')}\n"
        f"🇺🇿 Telegram: {data.get('tg')}\n"
        f"📞 Aloqa: {data.get('phone')}\n"
        f"🌐 Hudud: {data.get('region')}\n"
        f"💰 Narxi: {data.get('price')}\n"
        f"🕰 Murojaat qilish vaqti: {data.get('time')}\n"
        f"🔎 Maqsad: {data.get('goal')}"
    )

    if choice == "fmt_post":
        await query.message.reply_text(f"```\n{post_text}\n```", parse_mode="Markdown")
        await query.message.reply_text("Tayyor! Yuqoridagi matnni nusxalab kanalingizga joylashingiz mumkin. ✨")
    
    elif choice == "fmt_pdf":
        # Soda PDF yaratish
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        y = 750
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, y, "Ish joyi kerak (Rezyume)")
        y -= 30
        p.setFont("Helvetica", 12)
        
        lines = post_text.split('\n')
        for line in lines:
            p.drawString(100, y, line)
            y -= 20
            
        p.showPage()
        p.save()
        buffer.seek(0)
        
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=buffer,
            filename=f"Rezyume_{data.get('name')}.pdf",
            caption="Mana sizning PDF rezyumezingiz! 📄"
        )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Jarayon bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ---------------------------------------------------------
# 6. ASOSIY ISHGA TUSHIRISH
# ---------------------------------------------------------
def main():
    keep_alive()

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHECK_SUB: [CallbackQueryHandler(check_sub_callback, pattern="^check_subscription$")],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            JOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_job)],
            TG_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tg)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)
            ],
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_region)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal)],
            FORMAT_CHOICE: [CallbackQueryHandler(generate_result, pattern="^fmt_")],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    print("Rezyume boti ishga tushdi...")
    application.run_polling()

if __name__ == '__main__':
    main()
    
