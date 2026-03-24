from flask import Flask, render_template, request, redirect
import os
import json
from vercel_kv import kv

app = Flask(__name__)

# Fungsi untuk inisialisasi data jika database masih kosong
def get_initial_data():
    with open('asia_teams.json', 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    # Ambil data dari Database KV, jika kosong ambil dari JSON awal
    teams_data = kv.get('afc_teams')
    if not teams_data:
        teams_data = get_initial_data()['AFC_Teams']
        kv.set('afc_teams', teams_data)
    
    # Urutkan berdasarkan poin
    teams_data.sort(key=lambda x: x['poin'], reverse=True)
    return render_template('index.html', teams=teams_data)

@app.route('/update', methods=['POST'])
def update():
    negara_kita = request.form.get('negara_kita')
    lawan = request.form.get('lawan')
    hasil = float(request.form.get('hasil'))
    
    teams_data = kv.get('afc_teams')
    
    # Logika hitung poin FIFA (tetap sama)
    try:
        idx_tim = next(i for i, t in enumerate(teams_data) if t['negara'] == negara_kita)
        idx_lawan = next(i for i, t in enumerate(teams_data) if t['negara'] == lawan)
        
        p_tim = teams_data[idx_tim]['poin']
        p_lawan = teams_data[idx_lawan]['poin']
        
        we = 1 / (10**(-(p_tim - p_lawan) / 600) + 1)
        teams_data[idx_tim]['poin'] = round(p_tim + 25 * (hasil - we), 2)

        # SIMPAN KE DATABASE (Bukan ke file JSON)
        kv.set('afc_teams', teams_data)
    except:
        pass
        
    return redirect('/')
