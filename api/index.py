import os
import json  # INI YANG TADI KURANG
from flask import Flask, render_template, request, redirect
from upstash_redis import Redis

app = Flask(__name__, template_folder='../templates')

# Menggunakan variabel baru yang kamu buat tadi
kv = Redis(
    url=os.environ.get('MY_UPSTASH_URL'), 
    token=os.environ.get('MY_UPSTASH_TOKEN')
)

def get_initial_data():
    # Mengambil data awal dari file asia_teams.json
    json_path = os.path.join(os.path.dirname(__file__), '..', 'asia_teams.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data['AFC_Teams']

@app.route('/')
def index():
    try:
        # Coba ambil data dari database
        raw_data = kv.get('afc_teams')
        
        if not raw_data:
            # Jika database masih kosong, isi dengan data awal
            teams_data = get_initial_data()
            kv.set('afc_teams', json.dumps(teams_data))
        else:
            # Pastikan data diubah dari teks menjadi list Python
            teams_data = json.loads(raw_data) if isinstance(raw_data, (str, bytes)) else raw_data
        
        # Urutkan berdasarkan poin tertinggi
        teams_data.sort(key=lambda x: x['poin'], reverse=True)
        return render_template('index.html', teams=teams_data)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/update', methods=['POST'])
def update():
    try:
        # Logika update skor tetap sama
        # ... (kode update kamu) ...
        return redirect('/')
    except:
        return redirect('/')
