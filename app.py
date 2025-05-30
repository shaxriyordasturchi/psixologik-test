import streamlit as st
import subprocess
import platform
import threading
import time
import socket
import plotly.express as px
import pandas as pd
import requests

st.set_page_config(page_title="Network Monitor", layout="wide")
st.title("📡 Tarmoq Monitoring Dashbordi")

# Telegram bot token va chat_id ni shu yerga kiriting
BOT_TOKEN = "7899690264:AAH14dhEGOlvRoc4CageMH6WYROMEE5NmkY"
CHAT_ID = "7750409176"

# IP manzillar ro'yxatini olish
ip_input = st.text_area("IP manzillarni kiriting (har biri yangi qatorda):", "192.168.216.197\n192.168.1.2")
hosts = [ip.strip() for ip in ip_input.split("\n") if ip.strip()]

# PING funksiyasi
def ping_host_with_time(host, results):
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]
        start = time.time()
        output = subprocess.run(command, capture_output=True, text=True, timeout=3)
        duration = round((time.time() - start) * 1000)

        if "TTL=" in output.stdout or "ttl=" in output.stdout:
            results[host] = ("Online", duration)
        else:
            results[host] = ("No Response", None)
    except subprocess.TimeoutExpired:
        results[host] = ("Timeout", None)
    except:
        results[host] = ("Error", None)

def ping_multiple_hosts_with_time(hosts):
    threads = []
    results = {}
    for host in hosts:
        thread = threading.Thread(target=ping_host_with_time, args=(host, results))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    return results

# PING + GRAFIK tugmasi
if st.button("📊 Ping + Grafik"):
    with st.spinner("Ping vaqtlari o'lchanmoqda..."):
        ping_results = ping_multiple_hosts_with_time(hosts)
        data = [{"Host": host, "Status": status, "Ping (ms)": ping_time} for host, (status, ping_time) in ping_results.items()]
        df = pd.DataFrame(data)

        st.dataframe(df)

        df_chart = df[df["Ping (ms)"].notnull()]
        fig = px.bar(df_chart, x="Host", y="Ping (ms)", color="Ping (ms)", height=400)
        st.plotly_chart(fig)

# TEZ PORT SCANNER THREADING BILAN
def scan_port_thread(host, port, open_ports):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append(port)

def scan_ports_fast(host, port_range=(20, 1024)):
    open_ports = []
    threads = []
    for port in range(port_range[0], port_range[1] + 1):
        t = threading.Thread(target=scan_port_thread, args=(host, port, open_ports))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    open_ports.sort()
    return open_ports

st.subheader("📍 Port Scanner")
target_host = st.text_input("Port tekshiriladigan IP manzil:", "192.168.1.1")
start_port = st.number_input("Boshlang'ich port:", 1, 65534, 20)
end_port = st.number_input("Tugash port:", start_port+1, 65535, 1024)

if st.button("🔍 Tez Portlarni skanerlash"):
    with st.spinner("Tez skanerlash boshlandi..."):
        ports = scan_ports_fast(target_host, (start_port, end_port))
        if ports:
            st.success(f"Ochiq portlar: {ports}")
        else:
            st.warning("Hech qanday port ochiq emas.")

# TELEGRAM NOTIFIKATSIYA
def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, data=payload)

st.subheader("📤 Telegramga natijani yuborish")

if st.button("📨 Telegramga yuborish"):
    if 'df' in locals():
        message = "\n".join([f"{row['Host']}: {row['Status']} ({row['Ping (ms)']} ms)" for _, row in df.iterrows()])
        send_telegram_message(BOT_TOKEN, CHAT_ID, f"📡 Tarmoq natijalari:\n{message}")
        st.success("Telegramga yuborildi ✅")
    else:
        st.error("Iltimos, avval ping natijalarini oling.")
