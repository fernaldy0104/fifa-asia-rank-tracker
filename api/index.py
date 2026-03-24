import os
import json
from flask import Flask, render_template, request, redirect
from upstash_redis import Redis

app = Flask(__name__)

# Mengambil URL koneksi dari Environment Variables Vercel
# Pastikan di Settings Vercel sudah ada variabel bernama REDIS_URL
redis_url = os.environ.get('REDIS_URL')
kv = Redis.from_url(redis_url)

def get_initial_data():
    # Mengambil data awal dari file JSON jika database Redis masih kosong
    with open('asia_teams.json', 'r') as f:
        data = json.load(f)
    return data['AFC_Teams']

@app.route('/')
def index():
    # 1. Ambil data dari Redis
    teams_data_raw = kv.get('afc_teams')
    
    # 2. Jika database kosong, isi dengan data awal dari JSON
    if not teams_data_raw:
        teams_data = get_initial_data()
        kv.set('afc_teams', json.dumps(teams_data))
    else:
        # Jika data ada, Redis biasanya mengembalikan string, jadi kita ubah ke list/dict
        if isinstance(teams_data_raw, str):
            teams_data = json.loads(teams_data_raw)
        else:
            teams_data = teams_data_raw
    
    # 3. Urutkan berdasarkan poin tertinggi
    teams_data.sort(key=lambda x: x['poin'], reverse=True)
    return render_template('index.html', teams=teams_data)

@app.route('/update', methods=['POST'])
def update():
    negara_kita = request.form.get('negara_kita')
    lawan = request.form.get('lawan')
    hasil = float(request.form.get('hasil'))
    
    # Ambil data terbaru dari Redis
    current_data = kv.get('afc_teams')
    teams_data = json.loads(current_data) if isinstance(current_data, str) else current_data
    
    try:
        # Cari index tim yang mau diupdate
        idx_tim = next(i for i, t in enumerate(teams_data) if t['negara'] == negara_kita)
        idx_lawan = next(i for i, t in enumerate(teams_data) if t['negara'] == lawan)
        
        p_tim = teams_data[idx_tim]['poin']
        p_lawan = teams_data[idx_lawan]['poin']
        
        # Logika FIFA: Hitung probabilitas menang (We)
        we = 1 / (10**(-(p_tim - p_lawan) / 600) + 1)
        
        # Update poin (Konstanta 25 untuk pertandingan persahabatan/kualifikasi biasa)
        teams_data[idx_tim]['poin'] = round(p_tim + 25 * (hasil - we), 2)

        # 4. SIMPAN KEMBALI KE REDIS (Bukan ke file JSON)
        kv.set('afc_teams', json.dumps(teams_data))
        
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        
    return redirect('/')
