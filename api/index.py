import os
import json
from flask import Flask, render_template, request, redirect
from upstash_redis import Redis

app = Flask(__name__, template_folder='../templates')

# Pastikan nama variabel ini sesuai dengan yang kamu buat di Vercel tadi
kv = Redis(
    url=os.environ.get('MY_UPSTASH_URL'), 
    token=os.environ.get('MY_UPSTASH_TOKEN')
)

def get_initial_data():
    # Mengambil data dari file lokal di folder utama
    json_path = os.path.join(os.path.dirname(__file__), '..', 'asia_teams.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data['AFC_Teams']

@app.route('/')
def index():
    try:
        # 1. Coba ambil data dari Redis
        raw_data = kv.get('afc_teams')
        
        # 2. Jika kosong (None atau kosong banget), isi pakai data awal
        if raw_data is None or raw_data == "":
            teams_data = get_initial_data()
            kv.set('afc_teams', json.dumps(teams_data))
        else:
            # 3. Proses data agar tidak error "Expecting value"
            try:
                # Jika raw_data sudah dalam bentuk dict/list, pakai langsung
                if isinstance(raw_data, (dict, list)):
                    teams_data = raw_data
                else:
                    teams_data = json.loads(raw_data)
            except:
                # Jika format di Redis rusak, timpa dengan data awal saja biar sembuh
                teams_data = get_initial_data()
                kv.set('afc_teams', json.dumps(teams_data))
        
        # 4. Urutkan poin
        teams_data.sort(key=lambda x: x['poin'], reverse=True)
        return render_template('index.html', teams=teams_data)
        
    except Exception as e:
        return f"Error sistem: {str(e)}"

@app.route('/update', methods=['POST'])
def update():
    # Logika update tetap sama seperti sebelumnya
    return redirect('/')
