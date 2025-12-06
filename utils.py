import requests
from datetime import datetime,timedelta
import threading
def get_ip_info(ip):
    """获取ip详细信息"""
    try:
        # 使用免费的IP查询API
        response = requests.get(f'https://ipwhois.app/json/{ip}')
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country':data.get('country','未知'),
                    'region':data.get('regionName','未知'),
                    'city':data.get('city','未知'),
                    'isp':data.get('isp','未知')
                }
    except Exception as e:
        print(f'获取ip信息时出错:{e}')
        return {'country':'未知','region':'未知','city':'未知','isp':'未知'}

def cleanup_online_users(visit_stats, stats_lock):
    """定期清理超过30分钟未活动的用户"""
    with stats_lock:
        current_time = datetime.now()

        for ip, last_visit in visit_stats['online_users'].items():
            if current_time - last_visit > timedelta(minutes=30):
                del visit_stats['online_users'][ip]
    
    # 每5分钟执行一次清理
    timer = threading.Timer(300, cleanup_online_users)
    # 设置守护线程
    timer.daemon = True
    timer.start()
