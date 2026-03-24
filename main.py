from flask import Flask, render_template, request, redirect
import json

app = Flask(__name__)

# Fungsi untuk memuat dan mengurutkan data dari JSON
def load_data():
    try:
        with open('asia_teams.json', 'r') as f:
            data = json.load(f)
            # WAJIB: Urutkan dari poin terbesar ke terkecil agar Rank 1, 2, 3 benar
            data['AFC_Teams'].sort(key=lambda x: x['poin'], reverse=True)
            return data
    except FileNotFoundError:
        return {"AFC_Teams": []}

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', teams=data['AFC_Teams'])

@app.route('/update', methods=['POST'])
def update():
    negara_kita = request.form.get('negara_kita')
    lawan = request.form.get('lawan')
    hasil = float(request.form.get('hasil')) # 1=Menang, 0.5=Seri, 0=Kalah
    
    data = load_data()
    
    # Ambil poin lama
    p_tim = next(t['poin'] for t in data['AFC_Teams'] if t['negara'] == negara_kita)
    p_lawan = next(t['poin'] for t in data['AFC_Teams'] if t['negara'] == lawan)
    
    # RUMUS FIFA
    we = 1 / (10**(-(p_tim - p_lawan) / 600) + 1)
    p_baru = round(p_tim + 25 * (hasil - we), 2) # Bobot I = 25

    # Update poin di data asli
    for t in data['AFC_Teams']:
        if t['negara'] == negara_kita:
            t['poin'] = p_baru

    # Simpan kembali ke JSON
    with open('asia_teams.json', 'w') as f:
        json.dump(data, f, indent=4)
        
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)