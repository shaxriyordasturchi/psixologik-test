import streamlit as st
import pandas as pd
import plotly.express as px
from network_utils import ping_multiple_hosts, scan_ports_threaded

st.set_page_config(page_title="Network Monitor Dashboard", layout="wide")
st.title("Network Monitor Dashboard - Threaded Version")

hosts_input = st.text_input("IP manzillar yoki domenlarni vergul bilan kiriting", "8.8.8.8, 1.1.1.1")
hosts = [h.strip() for h in hosts_input.split(",") if h.strip()]

start_port, end_port = st.slider("Port diapazonini tanlang", 1, 65535, (20, 1024))

if st.button("Ping va portlarni skanerlash"):
    with st.spinner("Ping amalga oshirilmoqda..."):
        ping_results = ping_multiple_hosts(hosts)
    ping_df = pd.DataFrame([
        {"Host": host, "Ping (ms)": ping_results[host]} for host in hosts
    ])
    st.subheader("Ping natijalari:")
    st.dataframe(ping_df)

    for host in hosts:
        if ping_results[host] is not None:
            st.subheader(f"{host} uchun portlar skanerlanyapti...")
            open_ports = scan_ports_threaded(host, start_port, end_port)
            if open_ports:
                st.write(f"{host} ochiq portlar: {open_ports}")
                df_ports = pd.DataFrame(open_ports, columns=["Port"])
                fig = px.bar(df_ports, x="Port", y=[1]*len(open_ports), labels={'y':''}, title=f"{host} ochiq portlar")
                st.plotly_chart(fig)
            else:
                st.info(f"{host} uchun ochiq port topilmadi.")
        else:
            st.error(f"{host} ga ping amalga oshmadi, portlarni skanerlash o'tkazilmadi.")
