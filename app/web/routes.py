from flask import jsonify, request
from datetime import datetime

def init_routes(app, detector, traffic_gen, traffic_rec):
    @app.route('/api/stats')
    def get_stats():
        return jsonify({
            'detection': {
                'is_attack': detector.is_attack_detected(),
                'blocked_ips_count': len(detector.blocked_ips)
            },
            'generator': {
                'normal': traffic_gen.normal_count,
                'attack': traffic_gen.attack_count
            },
            'receiver': traffic_rec.get_stats()
        })

    @app.route('/api/traffic/start', methods=['POST'])
    def start_traffic():
        mode = request.args.get('mode')
        if mode not in ['normal', 'attack']:
            return jsonify({'error': 'Invalid mode'}), 400
        
        traffic_gen.start(mode)
        return jsonify({'status': 'started', 'mode': mode})

    @app.route('/api/traffic/stop', methods=['POST'])
    def stop_traffic():
        traffic_gen.stop()
        return jsonify({'status': 'stopped'})

    @app.route('/api/block', methods=['POST'])
    def block_ip():
        ip = request.json.get('ip')
        if not ip:
            return jsonify({'error': 'IP is required'}), 400
        
        detector.block_ip(ip)
        return jsonify({'status': 'success', 'ip': ip})