import os
import json
from flask import Flask, render_template, request, redirect
from upstash_redis import Redis

app = Flask(__name__, template_folder='../templates')

# Koneksi ke Redis
redis_url = os.environ.get('REDIS_URL')
kv = Redis.from_url(redis_url)

def get_initial_data():
    # Mengacu ke file json di folder utama
    json_path = os.path.join(os.path.dirname(__file__), '..', 'asia_teams.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data['AFC_Teams']

@app.route('/')
def index():
    try:
        raw_data = kv.get('afc_teams')
        if not raw_data:
            teams_data = get_initial_data()
            kv.set('afc_teams', json.dumps(teams_data))
        else:
            teams_data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
        
        teams_data.sort(key=lambda x: x['poin'], reverse=True)
        return render_template('index.html', teams=teams_data)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/update', methods=['POST'])
def update():
    try:
        negara_kita = request.form.get('negara_kita')
        lawan = request.form.get('lawan')
        hasil = float(request.form.get('hasil'))
        
        raw_data = kv.get('afc_teams')
        teams_data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
        
        idx_tim = next(i for i, t in enumerate(teams_data) if t['negara'] == negara_kita)
        idx_lawan = next(i for i, t in enumerate(teams_data) if t['negara'] == lawan)
        
        p_tim = teams_data[idx_tim]['poin']
        p_lawan = teams_data[idx_lawan]['poin']
        
        we = 1 / (10**(-(p_tim - p_lawan) / 600) + 1)
        teams_data[idx_tim]['poin'] = round(p_tim + 25 * (hasil - we), 2)

        kv.set('afc_teams', json.dumps(teams_data))
    except Exception as e:
        print(f"Update error: {e}")
        
    return redirect('/')
