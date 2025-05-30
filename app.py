import streamlit as st
import subprocess
import platform
import threading
import pandas as pd

st.set_page_config(page_title="Tarmoq Ping Monitor", layout="centered")

st.title("📡 Tarmoq Qurilmalarini Ping Monitoring")

# IP manzillarni kiriting
default_hosts = "192.168.216.108, 8.8.8.8, 1.1.1.1"
hosts_input = st.text_input("IP manzillarni vergul bilan kiriting:", default_hosts)

# IP larni tayyorlash
hosts = [h.strip() for h in hosts_input.split(",") if h.strip()]

# Ping funksiyasi
def ping_host(host, results):
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]
        output = subprocess.run(command, capture_output=True, text=True, timeout=3)
        if "TTL=" in output.stdout or "ttl=" in output.stdout:
            results[host] = "🟢 Online"
        else:
            results[host] = "🔴 No Response"
    except subprocess.TimeoutExpired:
        results[host] = "⏱️ Timeout"
    except Exception as e:
        results[host] = f"⚠️ Error"

# Ko‘p IP larni parallel ping qilish
def ping_multiple_hosts(hosts):
    threads = []
    results = {}
    for host in hosts:
        thread = threading.Thread(target=ping_host, args=(host, results))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    return results

# Natijalarni ko‘rsatish
if st.button("🔍 Pingni boshlash"):
    if not hosts:
        st.warning("Iltimos, kamida bitta IP manzil kiriting.")
    else:
        with st.spinner("Ping yuborilmoqda..."):
            ping_results = ping_multiple_hosts(hosts)
            df = pd.DataFrame([
                {"Host": host, "Status": ping_results.get(host, "Nomaʼlum")}
                for host in hosts
            ])
            st.success("Tayyor!")
            st.dataframe(df, use_container_width=True)
