import subprocess
import platform
import time
import socket
import threading
from queue import Queue

# Ping uchun bitta hostga ping yuborish
def ping_single_host(host, results):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]
    start_time = time.time()
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        elapsed = (time.time() - start_time) * 1000  # ms da
        results[host] = round(elapsed, 2)
    except subprocess.CalledProcessError:
        results[host] = None

# Ko'p hostlarga parallel ping yuborish
def ping_multiple_hosts(hosts):
    threads = []
    results = {}
    for host in hosts:
        t = threading.Thread(target=ping_single_host, args=(host, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return results

# Portni tekshirish uchun bitta thread funksiyasi
def scan_port_thread(host, port, open_ports):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((host, port))
    if result == 0:
        open_ports.append(port)
    sock.close()

# Threading bilan port skanerlash
def scan_ports_threaded(host, start_port=1, end_port=1024, max_threads=100):
    open_ports = []
    ports_queue = Queue()

    for port in range(start_port, end_port + 1):
        ports_queue.put(port)

    def worker():
        while not ports_queue.empty():
            port = ports_queue.get()
            scan_port_thread(host, port, open_ports)
            ports_queue.task_done()

    threads = []
    for _ in range(min(max_threads, end_port - start_port + 1)):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    ports_queue.join()
    for t in threads:
        t.join()

    return sorted(open_ports)
