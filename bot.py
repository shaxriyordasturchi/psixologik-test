import subprocess
import platform
import socket
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

BOT_TOKEN = "7899690264:AAH14dhEGOlvRoc4CageMH6WYROMEE5NmkY"  # Bu yerga bot tokeningizni yozing

# Ping funksiyasi
def ping_host(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    try:
        output = subprocess.run(command, capture_output=True, text=True, timeout=3)
        if "ttl=" in output.stdout.lower():
            # Ping vaqtini qidiring (Windows va Linux uchun farq bo'lishi mumkin)
            import re
            times = re.findall(r'time[=<]([\d\.]+) ?ms', output.stdout.lower())
            if times:
                return f"Online, ping: {times[0]} ms"
            else:
                return "Online, ping vaqti aniqlanmadi"
        else:
            return "No Response"
    except subprocess.TimeoutExpired:
        return "Timeout"
    except Exception as e:
        return f"Error: {str(e)}"

# Port scanning (tezkor versiya)
def scan_ports(host, start_port=20, end_port=1024):
    open_ports = []
    def scan_port(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass

    threads = []
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan_port, args=(port,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return sorted(open_ports)

# Start komandasi uchun menyu
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Ping IP", callback_data='ping')],
        [InlineKeyboardButton("Port Scanner", callback_data='portscan')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Salom! Tarmoq monitoring botiga xush kelibsiz.\n\nQuyidagilardan birini tanlang:', reply_markup=reply_markup)

# Callback query uchun handler
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "ping":
        query.edit_message_text("Ping qilish uchun IP manzil kiriting (masalan, 8.8.8.8):")
        context.user_data['action'] = 'ping'

    elif query.data == "portscan":
        query.edit_message_text("Portlarni skanerlash uchun IP manzil kiriting:")
        context.user_data['action'] = 'portscan'

# Matnli xabarlarni qabul qilish
def handle_message(update: Update, context: CallbackContext):
    user_action = context.user_data.get('action')
    text = update.message.text.strip()

    if user_action == 'ping':
        update.message.reply_text(f"{text} ga ping qilinmoqda...")
        result = ping_host(text)
        update.message.reply_text(f"Natija: {result}")
        context.user_data['action'] = None

    elif user_action == 'portscan':
        update.message.reply_text(f"{text} manzili bo‘yicha portlarni 20-1024 oralig‘ida skanerlash boshlanmoqda...")
        ports = scan_ports(text, 20, 1024)
        if ports:
            ports_str = ', '.join(str(p) for p in ports)
            update.message.reply_text(f"Ochiq portlar: {ports_str}")
        else:
            update.message.reply_text("Hech qanday ochiq port topilmadi.")
        context.user_data['action'] = None

    else:
        update.message.reply_text("Iltimos, boshida /start ni bosing va menyudan birini tanlang.")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("ping", start))
    dp.add_handler(CommandHandler("portscan", start))
    dp.add_handler(CommandHandler("menu", start))

    dp.add_handler(MessageHandler(lambda u, c: True, handle_message))

    print("Bot ishga tushdi...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    from telegram.ext import MessageHandler, Filters
    main()
