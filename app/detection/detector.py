from sklearn.ensemble import IsolationForest
import numpy as np
from app.utils.alerts import send_alert

class DDOSDetector:
    def __init__(self, config):
        self.config = config.get('detector', {})
        self.model = IsolationForest(n_estimators=100)
        self.blocked_ips = set()
        self.traffic_history = []
        self.attack_threshold = self.config.get('threshold', 1000)
        
    def analyze(self, traffic_features):
        """Анализирует трафик на наличие аномалий"""
        X = np.array([traffic_features]).reshape(1, -1)
        is_attack = self.model.predict(X)[0] == -1
        
        if is_attack:
            send_alert(f"DDoS attack detected! Features: {traffic_features}")
            
        return {
            'is_attack': bool(is_attack),
            'features': traffic_features
        }
    
    def is_attack_detected(self):
        """Определяет, обнаружена ли атака в текущий момент"""
        if not self.traffic_history:
            return False
            
        # Проверяем последнюю запись в истории трафика
        last_entry = self.traffic_history[-1]
        return last_entry.get('is_attack', False)
    
    def block_ip(self, ip):
        """Блокирует указанный IP-адрес"""
        self.blocked_ips.add(ip)
        send_alert(f"IP blocked: {ip}")
        
    def get_stats(self):
        """Возвращает текущую статистику детектора"""
        return {
            'is_attack': self.is_attack_detected(),
            'blocked_ips_count': len(self.blocked_ips),
            'last_features': self.traffic_history[-1] if self.traffic_history else None
        }