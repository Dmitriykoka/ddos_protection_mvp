import time
import random
from threading import Thread
from scapy.all import IP, TCP, send
from app.utils.alerts import send_alert

class TrafficGenerator:
    def __init__(self, config):
        self.config = config.get('traffic', {})
        self.target_ip = self.config.get('target_ip', '192.168.1.100')
        self.normal_rate = self.config.get('normal_rate', 10)
        self.attack_rate = self.config.get('attack_rate', 500)
        self.is_running = False
        self.thread = None
        self.normal_count = 0
        self.attack_count = 0

    def generate_normal(self):
        while self.is_running:
            packet = IP(dst=self.target_ip)/TCP(dport=80)
            send(packet, verbose=0)
            self.normal_count += 1
            time.sleep(1.0 / self.normal_rate)

    def generate_attack(self):
        while self.is_running:
            src_ip = f"10.0.0.{random.randint(1, 254)}"
            packet = IP(src=src_ip, dst=self.target_ip)/TCP(dport=80)
            send(packet, verbose=0)
            self.attack_count += 1
            time.sleep(1.0 / self.attack_rate)

    def start(self, mode='normal'):
        if self.is_running:
            self.stop()

        self.is_running = True
        self.thread = Thread(
            target=self.generate_normal if mode == 'normal' else self.generate_attack,
            daemon=True
        )
        self.thread.start()
        send_alert(f"Traffic generator started in {mode} mode")

    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.thread:
                self.thread.join(timeout=2)
            send_alert("Traffic generator stopped")

    def get_stats(self):
        return {
            'normal': self.normal_count,
            'attack': self.attack_count
        }