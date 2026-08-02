import io
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, ContextTypes


# Bu yerda sizning mavjud funksiyalaringiz va so'zlar lug'ati bo'lishi kerak
# (Masalan: generate_pdf, generate_text_post, TEXTS, get_users_count, ADMIN_ID va hokazo)

async def send_final_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    lang = context.user_data.get("lang", "uz")
    start_keyboard = ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True)
    
    pdf_file = await asyncio.to_thread(
        generate_pdf, context.user_data, context.user_data.get("photo_bytes")
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

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    await update.message.reply_text(
        TEXTS[lang]["cancel"], reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    count = get_users_count()
    await update.message.reply_text(
        f"📊 **Bot statistikasi:**\n\nJami foydalanuvchilar soni: **{count}** ta",
        parse_mode="Markdown"
    )
    
