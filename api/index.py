import os
import json
from flask import Flask, render_template, request, redirect
from upstash_redis import Redis

# Vercel mencari variabel 'app' ini
app = Flask(__name__, template_folder='../templates')

kv = Redis(
    url=os.environ.get('MY_UPSTASH_URL'), 
    token=os.environ.get('MY_UPSTASH_TOKEN')
)

def get_initial_data():
    # Pastikan file asia_teams.json ada di root folder (luar folder api)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, '..', 'asia_teams.json')
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data['AFC_Teams']
    except:
        # Data cadangan jika file tidak ditemukan
        return [{"negara": "Jepang", "poin": 1628.81}, {"negara": "Indonesia", "poin": 1100.12}]

@app.route('/')
def index():
    try:
        # Coba paksa reset sekali saja jika data masih 'Indonesia' saja
        # kv.delete('afc_teams') 
        
        raw_data = kv.get('afc_teams')
        if not raw_data:
            teams_data = get_initial_data()
            kv.set('afc_teams', json.dumps(teams_data))
        else:
            teams_data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            
        teams_data.sort(key=lambda x: x['poin'], reverse=True)
        return render_template('index.html', teams=teams_data)
    except Exception as e:
        return f"Build Success, but Data Error: {str(e)}"

# Jangan hapus baris ini agar Vercel bisa mengenali Flask
if __name__ == "__main__":
    app.run()
