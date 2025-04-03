from scapy.all import sniff
from threading import Thread, Event
from collections import deque
from app.utils.alerts import send_alert

class TrafficReceiver:
    def __init__(self, config):
        self.config = config.get('traffic', {})
        self.interface = self.config.get('interface', 'eth0')
        self.is_running = False
        self.stop_event = Event()
        self.packet_history = deque(maxlen=1000)
        self.unique_ips = set()

    def _packet_handler(self, packet):
        if not self.is_running:
            return

        if hasattr(packet, 'src'):
            self.unique_ips.add(packet.src)
            
        self.packet_history.append(packet)

    def start(self):
        if self.is_running:
            return

        self.is_running = True
        self.stop_event.clear()
        
        self.sniffer = Thread(
            target=lambda: sniff(
                iface=self.interface,
                prn=self._packet_handler,
                stop_filter=lambda _: self.stop_event.is_set()
            ),
            daemon=True
        )
        self.sniffer.start()
        send_alert(f"Traffic receiver started on {self.interface}")

    def stop(self):
        self.is_running = False
        self.stop_event.set()
        if hasattr(self, 'sniffer'):
            self.sniffer.join(timeout=2)
        send_alert("Traffic receiver stopped")

    def get_stats(self):
        return {
            'total_packets': len(self.packet_history),
            'unique_ips': len(self.unique_ips),
            'is_running': self.is_running
        }