# request 处理访问者请求
from flask import Flask,render_template,request
from datetime import datetime,timedelta
import threading
from utils import get_ip_info, cleanup_online_users

app = Flask(__name__)

# 存储访问统计信息
visit_stats={
    'total_visits':0,
    # {ip:访问时间}
    'online_users':{}
}

# 预设的朋友列表及其信息
friends_list = {
    'friend1': {
        'name': '少女乐队厨',
        'avatar': 'static/friends/foofoo.jpg',
        'last_seen': datetime.now() - timedelta(hours=2)
    },
    'friend2': {
        'name': '五条菌',
        'avatar': 'static/friends/wutiao.jpg',
        'last_seen': datetime.now() - timedelta(days=1)
    },
    'friend3': {
        'name': '先知·mohan穆德',
        'avatar': 'static/friends/mohan.jpg',
        'last_seen': datetime.now() - timedelta(hours=5)
    }
}

# 线程锁保证数据安全
stats_lock = threading.Lock()

# 在应用启动时开始清理任务
cleanup_online_users(visit_stats, stats_lock)

@app.route('/')
def index():
    visitor_ip = request.remote_addr
    visit_time = datetime.now()
    
    with stats_lock:
        # 获取地理位置信息
        location_info = get_ip_info(visitor_ip)

        # 检查同一IP是否在短时间内访问过（例如30分钟内）
        recent_visit = False
        for ip,last_seen in visit_stats['online_users'].items():
            if (ip == visitor_ip and visit_time - last_seen < timedelta(minutes=30)):
                recent_visit = True
                break
        
        # 只有不是近期访问过的用户才增加总访问次数
        if not recent_visit:
            visit_stats['total_visits'] += 1
            
        # 更新在线用户最后访问时间
        visit_stats['online_users'][visitor_ip] = visit_time
        visit_number = visit_stats['total_visits']
        online_count = len(visit_stats['online_users'])

    return render_template('index.html', 
                          visit_time=visit_time.strftime('%Y-%m-%d %H:%M:%S'),
                          visit_number=visit_number,
                          online_count=online_count,
                          visitor_ip=visitor_ip,
                          location=location_info,
                          friends=friends_list)

if __name__ == '__main__':
    app.run(DEBUG=True)