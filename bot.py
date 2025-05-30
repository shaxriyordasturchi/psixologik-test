from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# TCP/IP kategoriyalari va mavzular
CATEGORIES = {
    "TCP/IP asoslari": ["IP manzillar", "Subnetting", "Routing"],
    "Protokollar": ["TCP", "UDP", "ICMP"],
    "Tarmoq diagnostikasi": ["Ping", "Traceroute", "Netstat"],
}

# Har bir mavzu haqida qisqacha ma'lumot
TOPIC_INFO = {
    "IP manzillar": "IP manzillar qurilmalarni tarmoqda identifikatsiya qiladi. IPv4 va IPv6 turlari mavjud.",
    "Subnetting": "Subnetting tarmoqni kichik segmentlarga bo‘lish uchun ishlatiladi.",
    "Routing": "Routing paketlarni tarmoq bo‘ylab kerakli manzilga yo‘naltirish jarayonidir.",
    "TCP": "TCP ishonchli, ketma-ket ma'lumot uzatishni ta'minlaydigan protokol.",
    "UDP": "UDP bog‘lanishsiz va tezkor ma'lumot uzatish protokoli.",
    "ICMP": "ICMP tarmoq holatini tekshirish va xatoliklarni bildirish uchun ishlatiladi.",
    "Ping": "Ping qurilmaning tarmoqda mavjudligini tekshiradi.",
    "Traceroute": "Traceroute paketlar tarmoqda qaysi yo‘lni bosib o‘tishini ko‘rsatadi.",
    "Netstat": "Netstat faol tarmoq ulanishlari va portlarni ko‘rsatadi.",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in CATEGORIES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("TCP/IP kategoriyalarini tanlang:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("cat_"):
        category = data[4:]
        topics = CATEGORIES.get(category, [])
        keyboard = [
            [InlineKeyboardButton(topic, callback_data=f"topic_{topic}")] for topic in topics
        ]
        keyboard.append([InlineKeyboardButton("Ortga", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"{category} mavzulari:", reply_markup=reply_markup)

    elif data.startswith("topic_"):
        topic = data[6:]
        info = TOPIC_INFO.get(topic, "Bu mavzu haqida ma'lumot topilmadi.")
        keyboard = [[InlineKeyboardButton("Ortga", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"{topic} haqida:\n\n{info}", reply_markup=reply_markup)

    elif data == "back":
        keyboard = [
            [InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in CATEGORIES
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("TCP/IP kategoriyalarini tanlang:", reply_markup=reply_markup)

def main():
    TOKEN = "7899690264:AAH14dhEGOlvRoc4CageMH6WYROMEE5NmkY"  # Bot tokeningizni shu yerga yozing
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
