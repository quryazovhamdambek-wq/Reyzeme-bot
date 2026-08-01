import os
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Sizning Telegram bot tokeningiz
BOT_TOKEN = "8941048533:AAFJUlaY7aBxd3J7nZOMBAck9MyI7eYBlW0"

# Bosqichlar (States)
NAME, PHONE, PROFESSION, SKILLS = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 **Rezyume Yaratuvchi Botga Xush Kelibsiz!**\n\n"
        "Rezyume tayyorlash uchun Ism va Familiyangizni kiriting:",
        parse_mode="Markdown"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni kiriting (Masalan: +998 90 123 45 67):")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("💼 Qaysi kasb yoki mutaxassislik bo'yicha ish izlayapsiz?")
    return PROFESSION

async def get_profession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['profession'] = update.message.text
    await update.message.reply_text("🛠 Asosiy ko'nikmalaringiz va bilimingizni kiriting (Masalan: Python, Excel, Ingliz tili):")
    return SKILLS

async def generate_pdf_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['skills'] = update.message.text
    user_id = update.effective_user.id
    pdf_filename = f"resume_{user_id}.pdf"

    await update.message.reply_text("⏳ Rezyumeingiz shakllantirilmoqda, iltimos kuting...")

    # ReportLab orqali PDF yaratish
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    # Yuqori qism (Header) - To'q ko'k dizayn
    c.setFillColor(colors.HexColor("#1A365D"))
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)

    # Ism va Familiya (Oq rangda)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, height - 45, context.user_data['name'].upper())

    # Mutaxassislik
    c.setFont("Helvetica", 14)
    c.drawString(40, height - 70, context.user_data['profession'])

    # Aloqa ma'lumotlari
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 130, "ALOQA MA'LUMOTLARI")
    c.setStrokeColor(colors.HexColor("#CBD5E0"))
    c.line(40, height - 135, width - 40, height - 135)

    c.setFont("Helvetica", 11)
    c.drawString(40, height - 155, f"Tel: {context.user_data['phone']}")

    # Ko'nikmalar
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 200, "KO'NIKMALAR VA BILIMLAR")
    c.line(40, height - 205, width - 40, height - 205)

    c.setFont("Helvetica", 11)
    c.drawString(40, height - 225, context.user_data['skills'])

    # Pastki qism (Footer)
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.gray)
    c.drawString(40, 30, "Ushbu rezyume Telegram Bot orqali bepul yaratildi.")

    c.save()

    # PDF faylini Telegram'ga yuborish
    with open(pdf_filename, 'rb') as pdf_file:
        await update.message.reply_document(
            document=pdf_file,
            filename=f"{context.user_data['name']}_Rezyume.pdf",
            caption="✨ Rezyumeingiz tayyor bo'ldi!"
        )

    # Vaqtincha yaratilgan faylni o'chirish
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Rezyume yaratish bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            PROFESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_profession)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_pdf_and_send)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    print("Rezyume boti ishga tushdi...")
    app.run_polling()
  
