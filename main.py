from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from helper import WEEK_DAYS, LESSON_TIMES, LECTORS, SEMINAR_TEACHERS  # 🔹 yangi import

TOKEN = "8473703167:AAGGkseujn4qcYeVCBNq-czlq6CtPG-OpYA"
ADMIN_USERNAME = "@Akmalovna_1128"

BTN_JADVAL = "📘 Dars jadvali"
BTN_KAZUS = "📚 Kazus namunalar"
BTN_INFO = "ℹ️ Ma'lumot"
BTN_ADMIN = "📞 Admin bilan bog‘lanish"

main_buttons = ReplyKeyboardMarkup([
    [BTN_JADVAL, BTN_KAZUS],
    [BTN_INFO, BTN_ADMIN]
], resize_keyboard=True)

# Boshlanish
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Assalomu alaykum, {update.effective_user.first_name}! 👋\n\n"
        "Men DHF_Support botman.\nQuyidagi menyulardan birini tanlang:",
        reply_markup=main_buttons
    )

# === Dars jadvali interaktiv keyboard ===
async def send_jadval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [[day] for day in WEEK_DAYS], resize_keyboard=True
    )
    await update.message.reply_text("📅 Haftaning kunini tanlang:", reply_markup=keyboard)
    context.user_data["state"] = "day"  # holatni eslab qolamiz


async def handle_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text in WEEK_DAYS:
        context.user_data["day"] = update.message.text
        keyboard = ReplyKeyboardMarkup(
            [[t] for t in LESSON_TIMES], resize_keyboard=True
        )
        await update.message.reply_text("⏰ Soatni tanlang:", reply_markup=keyboard)
        context.user_data["state"] = "time"


async def handle_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") == "time" and update.message.text in LESSON_TIMES:
        context.user_data["time"] = update.message.text
        keyboard = ReplyKeyboardMarkup(
            [["Konstitutsiyaviy huquq"], ["Davlat huquqi nazariyasi"]],
            resize_keyboard=True
        )
        await update.message.reply_text("📖 Fanni tanlang:", reply_markup=keyboard)
        context.user_data["state"] = "subject"


async def handle_subject_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subject = update.message.text
    if context.user_data.get("state") == "subject" and subject in LECTORS:
        keyboard = ReplyKeyboardMarkup([["📘 Ma’ruza"], ["📗 Seminar"]], resize_keyboard=True)
        context.user_data["subject"] = subject
        await update.message.reply_text("Dars turini tanlang:", reply_markup=keyboard)
        context.user_data["state"] = "type"


async def handle_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text
    subject = context.user_data.get("subject")

    if t == "📘 Ma’ruza":
        await update.message.reply_text(
            f"📘 {subject} fanidan ma’ruza: {LECTORS[subject]}",
            reply_markup=main_buttons
        )
    elif t == "📗 Seminar":
        keyboard = ReplyKeyboardMarkup(
            [["1-guruh"], ["2-guruh"], ["3-guruh"]], resize_keyboard=True
        )
        await update.message.reply_text("Qaysi guruh uchun?", reply_markup=keyboard)
        context.user_data["state"] = "group"
        context.user_data["subject"] = subject


async def handle_group_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") == "group":
        group = int(update.message.text.split("-")[0])
        subject = context.user_data["subject"]
        teacher = SEMINAR_TEACHERS[subject][group]
        await update.message.reply_text(
            f"📗 {subject} fani, {group}-guruh seminar o‘qituvchisi: {teacher}",
            reply_markup=main_buttons
        )
        context.user_data.clear()


# === Kazus va boshqa tugmalar avvalgidek ===
async def send_kazus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kazus fayllar tez orada yuklanadi.", reply_markup=main_buttons)

async def send_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "DHF_Support bot orqali siz dars jadvali, kazus namunalarini va foydali hujjatlarni olishingiz mumkin.",
        reply_markup=main_buttons
    )

async def send_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Agar yordam kerak bo‘lsa, admin bilan bog‘laning: {ADMIN_USERNAME}",
        reply_markup=main_buttons
    )


# === Asosiy ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_JADVAL}$"), send_jadval))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(WEEK_DAYS)})$"), handle_day_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(LESSON_TIMES)})$"), handle_time_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(Konstitutsiyaviy huquq|Davlat huquqi nazariyasi)$"), handle_subject_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(📘 Ma’ruza|📗 Seminar)$"), handle_type_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^[123]-guruh$"), handle_group_selection))

    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_KAZUS}$"), send_kazus))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_INFO}$"), send_info))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ADMIN}$"), send_admin))

    print("✅ DHF_Support bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
