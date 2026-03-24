import os
import json
from flask import Flask, render_template, request, redirect
from upstash_redis import Redis

app = Flask(__name__)

# Koneksi ke Database menggunakan variabel yang ada di Vercel Settings kamu
redis_url = os.environ.get('REDIS_URL')
kv = Redis.from_url(redis_url)

def get_initial_data():
    with open('asia_teams.json', 'r') as f:
        data = json.load(f)
    return data['AFC_Teams']

@app.route('/')
def index():
    # Ambil data dari Redis
    teams_data = kv.get('afc_teams')
    
    # Jika database masih kosong, isi dengan data dari file JSON
    if not teams_data:
        teams_data = get_initial_data()
        kv.set('afc_teams', json.dumps(teams_data))
    else:
        # Jika data dari Redis berupa string, ubah kembali ke list
        if isinstance(teams_data, str):
            teams_data = json.loads(teams_data)
    
    teams_data.sort(key=lambda x: x['poin'], reverse=True)
    return render_template('index.html', teams=teams_data)

@app.route('/update', methods=['POST'])
def update():
    negara_kita = request.form.get('negara_kita')
    lawan = request.form.get('lawan')
    hasil = float(request.form.get('hasil'))
    
    # Ambil data terbaru dari database
    teams_data = json.loads(kv.get('afc_teams'))
    
    try:
        idx_tim = next(i for i, t in enumerate(teams_data) if t['negara'] == negara_kita)
        idx_lawan = next(i for i, t in enumerate(teams_data) if t['negara'] == lawan)
        
        p_tim = teams_data[idx_tim]['poin']
        p_lawan = teams_data[idx_lawan]['poin']
        
        we = 1 / (10**(-(p_tim - p_lawan) / 600) + 1)
        teams_data[idx_tim]['poin'] = round(p_tim + 25 * (hasil - we), 2)

        # Simpan kembali ke Redis dalam format JSON string
        kv.set('afc_teams', json.dumps(teams_data))
    except Exception as e:
        print(f"Error: {e}")
        
    return redirect('/')
