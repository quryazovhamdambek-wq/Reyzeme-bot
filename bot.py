import asyncio
import io
import logging
import os
import sqlite3
from aiohttp import web

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Admin ID, Bot Token va Kanal username
ADMIN_ID = 6416459996
BOT_TOKEN = os.environ.get(
    "BOT_TOKEN", "8941048533:AAFkpwA0YEjriEfj6SCwLcDUox2sfUNVQEc"
)
CHANNEL_USERNAME = "@TALIM_ADMINII"

logging.basicConfig(level=logging.INFO)

# Conversation handler bosqichlari
(
    LANG,
    TEMPLATE,
    NAME,
    PHONE,
    PHOTO,
    SKILLS,
    EXPERIENCE,
    LANGUAGES_EXP,
    PORTFOLIO,
    CERTIFICATES,
    EXPORT_FORMAT,
) = range(11)

# Matnlar lug'ati (O'zbek / Русский / English)
TEXTS = {
    "uz": {
        "welcome": "Xush kelibsiz! Rezyume yaratish uchun /create tugmasini bosing.",
        "sub_req": "Botdan foydalanish uchun rasmiy kanalimizga a'zo bo'ling:",
        "btn_sub": "📢 Kanalga a'zo bo'lish",
        "btn_check": "✅ Tekshirish",
        "not_sub": "Siz hali kanalga a'zo bo'lmadingiz. Iltimos, a'zo bo'lib qayta tekshiring!",
        "choose_template": "Rezyume shablonini tanlang:",
        "ask_name": "1/8. Ismingiz va familiyangizni kiriting:",
        "ask_phone": "2/8. Telefon raqamingizni kiriting:",
        "ask_photo": "3/8. Rezyume uchun rasmingizni yuboring (yoki 'O'tkazib yuborish' tugmasini bosing):",
        "skip": "⏭ O'tkazib yuborish",
        "ask_skills": "4/8. Ko'nikmalaringizni kiriting:",
        "ask_exp": "5/8. Ish tajribangiz haqida yozing:",
        "ask_lang": "6/8. Biladigan tillaringiz (masalan: O'zbek, Ingliz B2):",
        "ask_port": "7/8. Portfolio yoki loyihalaringiz havolasini yuboring:",
        "ask_cert": "8/8. Erishgan sertifikatlaringiz bo'lsa yozing (yoki 'Yo'q' deb yuboring):",
        "ask_format": "Rezyumeni qaysi formatda olishni xohlaysiz?",
        "done": "Sizning rezyumeringiz tayyor bo'ldi! 🎉",
        "cancel": "Jarayon bekor qilindi. /start ni bosing.",
    },
    "ru": {
        "welcome": "Добро пожаловать! Нажмите /create, чтобы создать резюме.",
        "sub_req": "Чтобы использовать бота, подпишитесь на наш официальный канал:",
        "btn_sub": "📢 Подписаться на канал",
        "btn_check": "✅ Проверить",
        "not_sub": "Вы еще не подписались на канал. Пожалуйста, подпишитесь и проверьте снова!",
        "choose_template": "Выберите шаблон резюме:",
        "ask_name": "1/8. Введите ваше имя и фамилию:",
        "ask_phone": "2/8. Введите ваш номер телефона:",
        "ask_photo": "3/8. Отправьте ваше фото для резюме (или нажмите 'Пропустить'):",
        "skip": "⏭ Пропустить",
        "ask_skills": "4/8. Введите ваши навыки:",
        "ask_exp": "5/8. Напишите о вашем опыте работы:",
        "ask_lang": "6/8. Владение языками (например: Узбекский, Английский B2):",
        "ask_port": "7/8. Отправьте ссылку на портфолио или проекты:",
        "ask_cert": "8/8. Укажите ваши сертификаты (или напишите 'Нет'):",
        "ask_format": "В каком формате вы хотите получить резюме?",
        "done": "Ваше резюме готово! 🎉",
        "cancel": "Процесс отменен. Нажмите /start.",
    },
    "en": {
        "welcome": "Welcome! Press /create to build a resume.",
        "sub_req": "To use the bot, please subscribe to our official channel:",
        "btn_sub": "📢 Subscribe to Channel",
        "btn_check": "✅ Check",
        "not_sub": "You have not subscribed yet. Please subscribe and try again!",
        "choose_template": "Choose a resume template:",
        "ask_name": "1/8. Enter your full name:",
        "ask_phone": "2/8. Enter your phone number:",
        "ask_photo": "3/8. Send your photo (or press 'Skip'):",
        "skip": "⏭ Skip",
        "ask_skills": "4/8. Enter your skills:",
        "ask_exp": "5/8. Write about your work experience:",
        "ask_lang": "6/8. Languages spoken (e.g., English B2, Uzbek Native):",
        "ask_port": "7/8. Send portfolio or project links:",
        "ask_cert": "8/8. List your certificates (or write 'None'):",
        "ask_format": "In which format would you like to receive your resume?",
        "done": "Your resume is ready! 🎉",
        "cancel": "Process cancelled. Press /start.",
    },
}


# --- SQLite Baza Funksiyalari 🗄️ ---
def init_db():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)"
    )
    conn.commit()
    conn.close()


def add_user(user_id):
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
    )
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users


def get_users_count():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# --- Kanal obunasini tekshirish 📢 ---
async def check_subscription(
    user_id: int, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME, user_id=user_id
        )
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return True


# --- PDF Yaratish Funksiyasi 📄 ---
def generate_pdf(data, photo_bytes=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    story = []

    theme_color = (
        colors.HexColor("#1A365D")
        if data.get("template") == "modern"
        else colors.HexColor("#2B6CB0")
    )

    normal_style = styles["Normal"]
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=theme_color,
        spaceBefore=10,
        spaceAfter=4,
    )

    header_text = f"<b><font size=18>{data.get('name', '')}</font></b><br/><br/>📞 {data.get('phone', '')}"
    header_p = Paragraph(header_text, normal_style)

    if photo_bytes:
        photo_io = io.BytesIO(photo_bytes)
        img = Image(photo_io, width=80, height=80)
        header_table = Table([[header_p, img]], colWidths=[400, 100])
    else:
        header_table = Table([[header_p]], colWidths=[500])

    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    lang = data.get("lang", "uz")
    labels = {
        "uz": [
            "💡 Ko'nikmalar",
            "💼 Ish tajribasi",
            "🌐 Tillar",
            "🔗 Portfolio",
            "📜 Sertifikatlar",
        ],
        "ru": [
            "💡 Навыки",
            "💼 Опыт работы",
            "🌐 Языки",
            "🔗 Портфолио",
            "📜 Сертификаты",
        ],
        "en": [
            "💡 Skills",
            "💼 Experience",
            "🌐 Languages",
            "🔗 Portfolio",
            "📜 Certificates",
        ],
    }

    curr_labels = labels.get(lang, labels["uz"])
    sections = [
        (curr_labels[0], data.get("skills")),
        (curr_labels[1], data.get("experience")),
        (curr_labels[2], data.get("languages")),
        (curr_labels[3], data.get("portfolio")),
        (curr_labels[4], data.get("certificates")),
    ]

    for title, content in sections:
        if content:
            story.append(Paragraph(title, heading_style))
            story.append(Paragraph(content, normal_style))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer


# --- Telegram Post Matni Yaratish 📝 ---
def generate_text_post(data):
    return f"""
📄 **REZYUME / RESUME**

👤 **Ism / Full Name:** {data.get('name', '-')}
📞 **Telefon / Phone:** {data.get('phone', '-')}

💡 **Ko'nikmalar / Skills:**
{data.get('skills', '-')}

💼 **Ish tajribasi / Experience:**
{data.get('experience', '-')}

🌐 **Tillar / Languages:**
{data.get('languages', '-')}

🔗 **Portfolio:** {data.get('portfolio', '-')}
📜 **Sertifikatlar / Certificates:** {data.get('certificates', '-')}

📢 {CHANNEL_USERNAME}
"""


# --- Bot Handlerlari 🤖 ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)

    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        keyboard = [
            [
                InlineKeyboardButton(
                    "📢 Kanalga a'zo bo'lish",
                    url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}",
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Tekshirish", callback_data="check_sub"
                )
            ],
        ]
        await update.message.reply_text(
            "Botdan foydalanish uchun rasmiy kanalimizga a'zo bo'ling:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END

    keyboard = [["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English"]]
    await update.message.reply_text(
        "Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return LANG


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Русский" in text:
        lang = "ru"
    elif "English" in text:
        lang = "en"
    else:
        lang = "uz"

    context.user_data["lang"] = lang

    reply_markup = ReplyKeyboardMarkup(
        [[KeyboardButton("/create")]], resize_keyboard=True
    )
    await update.message.reply_text(
        TEXTS[lang]["welcome"], reply_markup=reply_markup
    )
    return ConversationHandler.END


async def check_sub_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    is_subscribed = await check_subscription(user_id, context)
    if is_subscribed:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Obuna tasdiqlandi! Iltimos, botni boshlash uchun /start buyrug'ini ustiga bosing.",
        )
    else:
        await query.message.reply_text("Siz hali kanalga a'zo bo'lmadingiz!")


async def create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    keyboard = [["Classic 📄", "Modern 🎨"]]
    await update.message.reply_text(
        TEXTS[lang]["choose_template"],
        reply_markup=ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return TEMPLATE


async def get_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["template"] = "modern" if "Modern" in text else "classic"
    lang = context.user_data.get("lang", "uz")
    await update.message.reply_text(
        TEXTS[lang]["ask_name"], reply_markup=ReplyKeyboardRemove()
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    lang = context.user_data.get("lang", "uz")
    await update.message.reply_text(TEXTS[lang]["ask_phone"])
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    lang = context.user_data.get("lang", "uz")
    keyboard = [[KeyboardButton(TEXTS[lang]["skip"])]]
    await update.message.reply_text(
        TEXTS[lang]["ask_photo"],
        reply_markup=ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        context.user_data["photo_bytes"] = (
            await photo_file.download_as_bytearray()
        )

    await update.message.reply_text(
        TEXTS[lang]["ask_skills"], reply_markup=ReplyKeyboardRemove()
    )
    return SKILLS


async def get_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["skills"] = update.message.text
    lang = context.user_data.get("lang", "uz")
    await update.message.reply_text(TEXTS[lang]["ask_exp"])
    return EXPERIENCE


async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text
    lang = context.user_data.get("lang", "uz")
    await update.message.reply_text(TEXTS[lang]["ask_lang"])
    return LANGUAGES_EXP


async def get_languages_exp(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["languages"] = update.message.text
    lang = context.user_data.get("lang", "uz")
    await update.message.reply_text(TEXTS[lang]["ask_port"])
    return PORTFOLIO


async def get_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["portfolio"] = update.message.text
    lang = context.user_data.get("lang", "uz")
    await update.message.reply_text(TEXTS[lang]["ask_cert"])
    return CERTIFICATES


async def get_certificates(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["certificates"] = update.message.text
    lang = context.user_data.get("lang", "uz")

    keyboard = [
        ["📄 PDF Format", "📝 Text Format"],
        ["🖼️ Image + Text", "🌟 Barchasi (All)"],
    ]
    await update.message.reply_text(
        TEXTS[lang]["ask_format"],
        reply_markup=ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return EXPORT_FORMAT


async def send_final_resume(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    choice = update.message.text
    lang = context.user_data.get("lang", "uz")
    start_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("/start")]], resize_keyboard=True
    )

    pdf_file = await asyncio.to_thread(
        generate_pdf,
        context.user_data,
        context.user_data.get("photo_bytes"),
    )
    text_post = generate_text_post(context.user_data)

    if "PDF" in choice:
        await update.message.reply_document(
            document=pdf_file,
            filename=f"Resume_{context.user_data.get('name', 'User')}.pdf",
            caption=TEXTS[lang]["done"],
            reply_markup=start_keyboard,
        )
    elif "Text" in choice:
        await update.message.reply_text(
            text_post, parse_mode="Markdown", reply_markup=start_keyboard
        )
    elif "Image" in choice:
        if context.user_data.get("photo_bytes"):
            photo_io = io.BytesIO(context.user_data["photo_bytes"])
            await update.message.reply_photo(
                photo=photo_io,
                caption=text_post,
                parse_mode="Markdown",
                reply_markup=start_keyboard,
            )
        else:
            await update.message.reply_text(
                text_post, parse_mode="Markdown", reply_markup=start_keyboard
            )
    else:  # Barchasi / All
        await update.message.reply_document(
            document=pdf_file,
            filename=f"Resume_{context.user_data.get('name', 'User')}.pdf",
        )
        if context.user_data.get("photo_bytes"):
            photo_io = io.BytesIO(context.user_data["photo_bytes"])
            await update.message.reply_photo(
                photo=photo_io,
                caption=text_post,
                parse_mode="Markdown",
                reply_markup=start_keyboard,
            )
        else:
            await update.message.reply_text(
                text_post, parse_mode="Markdown", reply_markup=start_keyboard
            )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    await update.message.reply_text(TEXTS[lang]["cancel"])
    return ConversationHandler.END


async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        count = get_users_count()
        await update.message.reply_text(
            f"📊 **Bot statistikasi:**\n\nJami foydalanuvchilar soni: **{count}** ta"
        )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text(
            "Xabar matnini kiriting! Masalan: `/send Salom`"
        )
        return
    users = get_all_users()
    sent = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await update.message.reply_text(
        f"📣 Xabar **{sent}** ta foydalanuvchiga muvaffaqiyatli yuborildi!"
    )


# --- Render Veb-Server 🌐 ---
async def handle_ping(request):
    return web.Response(text="Bot ishlamoqda! ✅")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)

    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Veb-server {port}-portda ishga tushdi 🚀")


async def main():
    init_db()
    await start_web_server()

    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("create", create_start),
            CommandHandler("start", start),
        ],
        states={
            LANG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)
            ],
            TEMPLATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_template)
            ],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)
            ],
            PHOTO: [
                MessageHandler(filters.PHOTO, get_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_photo),
            ],
            SKILLS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_skills)
            ],
            EXPERIENCE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, get_experience
                )
            ],
            LANGUAGES_EXP: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, get_languages_exp
                )
            ],
            PORTFOLIO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_portfolio)
            ],
            CERTIFICATES: [
                MessageHandler(
      
      
