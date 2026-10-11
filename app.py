import base64
from io import BytesIO
from datetime import datetime
from flask import Flask, render_template_string
import matplotlib
import matplotlib.pyplot as plt
import requests

# Menggunakan backend Agg agar Matplotlib dapat berjalan tanpa tampilan GUI
matplotlib.use('Agg')

app = Flask(__name__)

def fetch_bmkg_data():
    """Mengambil data prakiraan cuaca wilayah Jember dari API Resmi BMKG"""
    try:
        # Endpoint BMKG Wilayah Jember (Kode Administrasi Adm4: 35.09)
        url = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=35.09"
        res = requests.get(url, timeout=5).json()
        cuaca_terkini = res['data'][0]['cuaca'][0][0]
        
        return {
            'status': 'Online (API BMKG)',
            'cuaca': cuaca_terkini.get('weather_desc', 'Cerah Berawan'),
            'suhu_c': cuaca_terkini.get('t', '--'),
            'kelembapan_persen': cuaca_terkini.get('hu', '--'),
            'kecepatan_angin_kmh': cuaca_terkini.get('ws', '--'),
            'waktu_prediksi': cuaca_terkini.get('local_datetime', '-')
        }
    except Exception as e:
        return {
            'status': f'Offline/Error: {str(e)}',
            'cuaca': 'Cerah Berawan (Fallback)',
            'suhu_c': 29.0,
            'kelembapan_persen': 75,
            'kecepatan_angin_kmh': 12,
            'waktu_prediksi': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
joisoioisweweww  e
def generate_charts(bmkg_suhu):
    """Me-render grafik simulasi AWS dan Validasi BMKG"""
    # Dummy data waktu 6 jam terakhir
    waktu_list = ['07:00', '08:00', '09:00', '10:00', '11:00', '12:00']
    
    # Dummy data sensor AWS
    suhu_aws = [26.5, 27.8, 29.1, 30.4, 31.2, 30.8]
    kat_aws = [55.0, 53.5, 50.2, 48.0, 45.5, 44.0]
    
    # Nilai BMKG untuk perbandingan di grafik
    try:
        val_bmkg = float(bmkg_suhu)
    except (ValueError, TypeError):
        val_bmkg = 29.0
    suhu_bmkg = [val_bmkg - 1.5, val_bmkg - 1.0, val_bmkg - 0.5, val_bmkg, val_bmkg + 0.5, val_bmkg]

    # 1. Grafik AWS Dummy
    fig1, ax1 = plt.subplots(figsize=(6.5, 3.5), dpi=100)
    ax1.plot(waktu_list, suhu_aws, color='#dc3545', linewidth=2, label='Suhu AWS')
    ax1.set_ylabel('Suhu Udara (°C)', color='#dc3545')
    
    ax2 = ax1.twinx()
    ax2.plot(waktu_list, kat_aws, color='#198754', linewidth=2, linestyle='--', label='Kadar Air')
    ax2.set_ylabel('Kadar Air Tanah (%)', color='#198754')
    fig1.tight_layout()

    buf1 = BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    img_aws = base64.b64encode(buf1.getvalue()).decode('utf-8')
    plt.close(fig1)

    # 2. Grafik Validasi AWS vs BMKG
    fig2, ax = plt.subplots(figsize=(5, 3.5), dpi=100)
    ax.plot(waktu_list, suhu_aws, color='#0d6efd', linewidth=2, label='AWS Simulasi')
    ax.plot(waktu_list, suhu_bmkg, color='#ffc107', linewidth=2, linestyle='--', label='BMKG')
    ax.set_ylabel('Suhu (°C)')
    ax.set_title('Uji Validasi: AWS vs BMKG', fontsize=10)
    ax.legend(loc='upper right')
    fig2.tight_layout()

    buf2 = BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    img_validasi = base64.b64encode(buf2.getvalue()).decode('utf-8')
    plt.close(fig2)

    return img_aws, img_validasi

# HTML Template
HTML_PAGE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Testing BMKG - AWS FTP UNEJ</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .card-stat { border-radius: 12px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
</head>
<body>

    <nav class="navbar navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="#">🧪 Testing Integration BMKG | UNEJ</a>
            <span class="badge bg-warning text-dark">Mode Progres Mingguan (Testing)</span>
        </div>
    </nav>

    <div class="container mb-5">
        
        <!-- Status Banner -->
        <div class="alert alert-info d-flex justify-content-between align-items-center" role="alert">
            <div>
                <strong>Status Koneksi BMKG:</strong> {{ bmkg.status }}
            </div>
            <a href="/" class="btn btn-sm btn-outline-primary">🔄 Refresh Data BMKG</a>
        </div>

        <!-- Panel Prakiraan BMKG (DATA UTAMA YANG DITES) -->
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card card-stat p-4 bg-white border-primary">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold mb-0 text-primary">🌤️ Data Real-time Prakiraan Cuaca BMKG (Wilayah Jember)</h5>
                        <span class="badge bg-secondary">Jam Prediksi BMKG: {{ bmkg.waktu_prediksi }}</span>
                    </div>
                    <div class="row text-center align-items-center g-3">
                        <div class="col-md-3 col-6">
                            <small class="text-muted d-block">Kondisi Cuaca</small>
                            <span class="fw-bold fs-4 text-dark">{{ bmkg.cuaca }}</span>
                        </div>
                        <div class="col-md-3 col-6">
                            <small class="text-muted d-block">Suhu Udara BMKG</small>
                            <span class="fw-bold fs-4 text-danger">{{ bmkg.suhu_c }} °C</span>
                        </div>
                        <div class="col-md-3 col-6">
                            <small class="text-muted d-block">Kelembapan Udara BMKG</small>
                            <span class="fw-bold fs-4 text-info">{{ bmkg.kelembapan_persen }} %</span>
                        </div>
                        <div class="col-md-3 col-6">
                            <small class="text-muted d-block">Kecepatan Angin BMKG</small>
                            <span class="fw-bold fs-4 text-secondary">{{ bmkg.kecepatan_angin_kmh }} km/h</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Dummy Hardware Sensor Placeholder -->
        <div class="card card-stat p-3 mb-4 bg-light">
            <h6 class="fw-bold text-muted mb-2">📟 Status Hardware Sensor AWS Rakitan</h6>
            <p class="small text-muted mb-0">Rangkaian sensor belum terhubung. Menampilkan data dummy untuk visualisasi antarmuka web.</p>
        </div>

        <!-- Grafik Result -->
        <div class="row g-3">
            <div class="col-md-7">
                <div class="card card-stat p-3 text-center">
                    <h6 class="fw-bold mb-3 text-start">📊 Grafik AWS (Simulasi Dummy)</h6>
                    <img src="data:image/png;base64,{{ chart_aws }}" class="img-fluid rounded">
                </div>
            </div>
            <div class="col-md-5">
                <div class="card card-stat p-3 text-center">
                    <h6 class="fw-bold mb-3 text-start">⚔️ Grafik Uji Validasi (AWS vs BMKG)</h6>
                    <img src="data:image/png;base64,{{ chart_val }}" class="img-fluid rounded">
                </div>
            </div>
        </div>

        <footer class="mt-5 text-center text-muted small">
            Sumber Data: <a href="https://data.bmkg.go.id" target="_blank">API Publik BMKG</a>
        </footer>
    </div>
</body>
</html>
"""

@app.route('/')
def test_dashboard():
    data_bmkg = fetch_bmkg_data()
    chart_aws, chart_val = generate_charts(data_bmkg['suhu_c'])
    return render_template_string(HTML_PAGE, bmkg=data_bmkg, chart_aws=chart_aws, chart_val=chart_val)

if __name__ == '__main__':
    print("Mulai pengujian integrasi BMKG...")
    app.run(host='127.0.0.1', port=5000, debug=True)
