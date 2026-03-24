import os
import json
from flask import Flask, render_template, request, redirect
from upstash_redis import Redis

app = Flask(__name__, template_folder='../templates')

# Menggunakan variabel yang kamu buat di Vercel tadi
kv = Redis(
    url=os.environ.get('MY_UPSTASH_URL'), 
    token=os.environ.get('MY_UPSTASH_TOKEN')
)

def get_initial_data():
    # Gunakan path absolut agar Vercel tidak bingung mencari file
    import os
    
    # Mencari lokasi file asia_teams.json di folder utama (root)
    # Path ini naik satu level dari folder 'api'
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, '..', 'asia_teams.json')
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data['AFC_Teams']
    except Exception as e:
        # Jika file masih tidak ketemu, kita masukkan data manual sedikit agar tidak kosong
        return [
            {"negara": "Jepang", "poin": 1628.81},
            {"negara": "Iran", "poin": 1611.16},
            {"negara": "Korea Selatan", "poin": 1563.99},
            {"negara": "Indonesia", "poin": 1100.12}
        ]

@app.route('/')
def index():
    try:
        # 1. Ambil data dari Redis
        raw_data = kv.get('afc_teams')
        
        # 2. Cek apakah data benar-benar ada dan tidak kosong
        if raw_data is None or raw_data == "" or raw_data == "null":
            teams_data = get_initial_data()
            # Langsung simpan ke Redis agar kunjungan berikutnya tidak kosong
            kv.set('afc_teams', json.dumps(teams_data))
        else:
            # 3. Jika raw_data berupa string, ubah jadi list. Jika sudah list, pakai langsung.
            if isinstance(raw_data, str):
                teams_data = json.loads(raw_data)
            else:
                teams_data = raw_data
        
        # 4. Sortir berdasarkan poin
        teams_data.sort(key=lambda x: x['poin'], reverse=True)
        return render_template('index.html', teams=teams_data)
        
    except Exception as e:
        # Jika masih error JSON, reset saja datanya di Redis
        backup = get_initial_data()
        kv.set('afc_teams', json.dumps(backup))
        return render_template('index.html', teams=backup)

@app.route('/update', methods=['POST'])
def update():
    # Logika update skor kamu tetap di sini
    return redirect('/')
