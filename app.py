# request 处理访问者请求
from flask import Flask,render_template,request
from datetime import datetime,timedelta
import threading
# requests 调用第三方服务
import requests
import json


app = Flask(__name__)

# 存储访问统计信息
visit_stats={
    'total_visits':0,
    'online_users':{},
    'visit_history':[]
}


# 线程锁保证数据安全
stats_lock = threading.Lock()


def get_location_info(ip):
    """使用IP地址获取地理位置信息"""
    try:
        # 使用免费的IP地理位置API
        response = requests.get(f'https://ip-api.com/json/{ip}')
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
        print(f'获取地理位置信息时出错:{e}')
        return {'country':'未知','region':'未知','city':'未知','isp':'未知'}



def cleanup_online_users():
    """定期清理超过10分钟未活动的用户"""
    with stats_lock:
        current_time = datetime.now()
        expired_ips = []
        for ip, last_seen in visit_stats['online_users'].items():
            if current_time - last_seen > timedelta(minutes=10):
                expired_ips.append(ip)
        
        for ip in expired_ips:
            del visit_stats['online_users'][ip]
    
    # 每5分钟执行一次清理
    timer = threading.Timer(300, cleanup_online_users)
    timer.daemon = True
    timer.start()

# 在应用启动时开始清理任务
cleanup_online_users()

@app.route('/')
def index():
    visitor_ip = request.remote_addr

    # 处理代理情况下的真实IP
    if request.headers.get('X-Forwarded-For'):
        visitor_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        visitor_ip = request.headers.get('X-Real-IP')

    visit_time = datetime.now()
    
    with stats_lock:
        # 获取地理位置信息
        location_info = get_location_info(visitor_ip)

        # 检查同一IP是否在短时间内访问过（例如30分钟内）
        recent_visit = False
        for record in reversed(visit_stats['visit_history'][-50:]):  # 只检查最近50条记录
            if (record['ip'] == visitor_ip and 
                visit_time - record['time'] < timedelta(minutes=30)):
                recent_visit = True
                break
        
        # 记录本次访问
        visit_record = {
            'ip': visitor_ip,
            'time': visit_time,
            'location': location_info

        }
        # 添加访问记录
        visit_stats['visit_history'].append(visit_record)
        
        # 只有不是近期访问过的用户才增加总访问次数
        if not recent_visit:
            visit_stats['total_visits'] += 1
            
        # 更新在线用户最后访问时间
        visit_stats['online_users'][visitor_ip] = visit_time
        current_visit_number = visit_stats['total_visits']
        online_count = len(visit_stats['online_users'])

    return render_template('index.html', 
                          visit_time=visit_time.strftime('%Y-%m-%d %H:%M:%S'),
                          visit_number=current_visit_number,
                          online_count=online_count,
                          visitor_ip=visitor_ip,
                          location=location_info)



if __name__ == '__main__':
    app.run(DEBUG=True)
