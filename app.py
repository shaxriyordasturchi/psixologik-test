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

# PORT SCANNER
def scan_ports(host, port_range=(20, 1024)):
    open_ports = []
    for port in range(port_range[0], port_range[1] + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
    return open_ports

st.subheader("📍 Port Scanner")
target_host = st.text_input("Port tekshiriladigan IP manzil:", "192.168.1.1")
start_port = st.number_input("Boshlang'ich port:", 1, 65534, 20)
end_port = st.number_input("Tugash port:", start_port+1, 65535, 1024)

if st.button("🔍 Portlarni skanerlash"):
    with st.spinner("Skanerlanmoqda..."):
        ports = scan_ports(target_host, (start_port, end_port))
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
bot_token = st.text_input("7899690264:AAH14dhEGOlvRoc4CageMH6WYROMEE5NmkY", type="password")
chat_id = st.text_input("7750409176")

if st.button("📨 Telegramga yuborish"):
    if bot_token and chat_id and 'df' in locals():
        message = "\n".join([f"{row['Host']}: {row['Status']} ({row['Ping (ms)']} ms)" for _, row in df.iterrows()])
        send_telegram_message(bot_token, chat_id, f"📡 Tarmoq natijalari:\n{message}")
        st.success("Telegramga yuborildi ✅")
    else:
        st.error("Iltimos, avval ping natijalarini oling va to‘liq ma’lumot kiriting.")

