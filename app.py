from flask import Flask, jsonify, render_template
import requests
import time
import math

app = Flask(__name__)
request_count = 0
start_time = time.time()

def get_metadata():
    try:
        token = requests.put(
            'http://169.254.169.254/latest/api/token',
            headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
            timeout=2
        ).text
        h = {'X-aws-ec2-metadata-token': token}
        base = 'http://169.254.169.254/latest/meta-data/'
        return {
            'instance_id':   requests.get(base + 'instance-id', headers=h, timeout=2).text,
            'az':            requests.get(base + 'placement/availability-zone', headers=h, timeout=2).text,
            'instance_type': requests.get(base + 'instance-type', headers=h, timeout=2).text,
            'private_ip':    requests.get(base + 'local-ipv4', headers=h, timeout=2).text,
        }
    except:
        return {'instance_id': 'local-dev-001', 'az': 'local-zone-a',
                'instance_type': 't2.micro', 'private_ip': '127.0.0.1'}


@app.route('/')
def index():
    global request_count
    request_count += 1
    m = get_metadata()
    uptime_s = int(time.time() - start_time)
    az_colors = {
        'ap-south-1a': '#00d4ff',
        'ap-south-1b': '#ff6b6b',
        'ap-south-1c': '#a8ff78',
        'local-zone-a': '#ffd700'
    }
    return render_template('index.html',
        instance_id   = m['instance_id'],
        az            = m['az'],
        instance_type = m['instance_type'],
        private_ip    = m['private_ip'],
        region        = m['az'][:-1] if m['az'] != 'local-zone-a' else 'local',
        request_count = request_count,
        uptime        = f"{uptime_s//3600}h {(uptime_s%3600)//60}m {uptime_s%60}s",
        az_color      = az_colors.get(m['az'], '#ffffff')
    )


@app.route('/health')
def health():
    m = get_metadata()
    return jsonify({'status': 'healthy', 'instance_id': m['instance_id'],
                    'az': m['az'], 'timestamp': time.time()})


@app.route('/stress')
def stress():
    m = get_metadata()
    start = time.time()
    while time.time() - start < 25:           # burn CPU for 25 seconds
        sum(math.sqrt(i) for i in range(100000))
    return jsonify({'status': 'stress_complete', 'instance_id': m['instance_id']})


@app.route('/info')
def info():
    m = get_metadata()
    return jsonify({'instance': m, 'requests': request_count,
                    'uptime': int(time.time() - start_time)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)