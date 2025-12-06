from datetime import datetime

visit_stats = {
    'total_visits': 0,
    # {ip:访问时间}
    'online_users': {}
}
ips = ['0.0.0.1', '0.0.0.2', '0.0.0.3']

for ip in ips:
    visit_time = datetime.now()
    visit_stats['online_users'][ip] = visit_time

for ip,last_seen in visit_stats['online_users'].items():
    print(ip,last_seen)
