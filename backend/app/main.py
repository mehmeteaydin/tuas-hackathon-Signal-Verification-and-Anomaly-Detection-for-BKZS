from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
import asyncio
import json
import time
import csv
from pathlib import Path

# Kendi dosyalarından importlar (Bunların var olduğundan emin ol)
from schemas import GNSSSignal
from ml_engine import MLEngine

app = FastAPI(title="BKZS için Anti-Spoofing & Signal Doğrulama")

# Static dosyaları dışarı açıyoruz (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML şablonları
templates = Jinja2Templates(directory="templates")

ml_engine = MLEngine()

# ─── CSV Normal Verilerini Yükle ──────────────────────────────────────────────
# Dosya yolunu kendi klasör yapına göre ayarlayabilirsin
CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "data_single_100k.csv"

_normal_rows: list[dict] = []
_csv_index: int = 0

# GNSSSignal şemasının alanları (schemas.py ile senkron tutulmalı)
SIGNAL_FIELDS = [
    "Speed_kmh", "Acceleration_mps2", "GPS_Lat", "GPS_Long",
    "Signal_Strength_dBm", "Packet_Size_bytes", "Transmission_Rate_Mbps",
    "Latency_ms", "Jitter_ms", "Packet_Loss_percent", "Flow_Duration_ms",
    "Total_Fwd_Packets", "Total_Bwd_Packets", "Avg_Packet_Length",
    "SYN_Flag_Count", "ACK_Flag_Count", "Flow_Bytes_per_s",
    "Trust_Score", "Encryption_Overhead_ms", "Authentication_Success"
]

def _load_normal_rows():
    global _normal_rows
    if not CSV_PATH.exists():
        print(f"[UYARI] CSV bulunamadı: {CSV_PATH}")
        return
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            target = row.get("Target", row.get("target", ""))
            if target.strip().lower() == "normal":
                _normal_rows.append(row)
    print(f"[CSV] {len(_normal_rows)} adet Normal satır yüklendi.")

_load_normal_rows()

# ─── Simülasyon State ─────────────────────────────────────────────────────────
sim_state = {
    "attack_mode": "Normal",
    "attack_until": 0.0,
    "is_streaming": False  # Yeni: Akışı kontrol eden bayrak
}

# ─── HTML Routes ──────────────────────────────────────────────────────────────
@app.get("/home")
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/test")
async def test_page(request: Request):
    return templates.TemplateResponse(request=request, name="test.html")

@app.get("/", include_in_schema=False)
async def open_swagger():
    return RedirectResponse(url="/docs")


# ─── API Routes (Simülasyon & Akış Kontrolü) ──────────────────────────────────
@app.get("/control_stream/{action}", tags=["Simülasyon"])
async def control_stream(action: str):
    """Akışı global olarak başlatır veya durdurur."""
    if action == "start":
        sim_state["is_streaming"] = True
        return {"status": "Akış başlatıldı"}
    elif action == "stop":
        sim_state["is_streaming"] = False
        return {"status": "Akış durduruldu"}
    return {"error": "Geçersiz işlem. 'start' veya 'stop' gönderin."}


@app.get("/inject/{attack_type}", tags=["Simülasyon"])
async def inject_attack(attack_type: str):
    valid = ["Normal", "Spoofing", "DoS", "Sybil", "Data_Tampering"]
    if attack_type not in valid:
        return {"error": "Geçerli tipler: " + ", ".join(valid)}
    
    if attack_type == "Normal":
        sim_state["attack_mode"] = "Normal"
        sim_state["attack_until"] = 0.0
    else:
        sim_state["attack_mode"] = attack_type
        sim_state["attack_until"] = time.time() + 5.0 # 5 saniye boyunca etkili
        
    return {"injected": attack_type, "duration_s": 5 if attack_type != "Normal" else 0}


# ─── Sinyal Üretici Fonksiyonlar ──────────────────────────────────────────────
def _next_csv_row() -> dict:
    """CSV'den sıradaki Normal satırı alır, sona ulaşınca başa döner."""
    global _csv_index
    if not _normal_rows:
        return {}
    row = _normal_rows[_csv_index % len(_normal_rows)]
    _csv_index += 1
    return row

def _csv_row_to_signal(row: dict) -> dict:
    """Ham CSV satırını SIGNAL_FIELDS sözlüğüne dönüştürür."""
    result = {}
    for field in SIGNAL_FIELDS:
        val = row.get(field, "0")
        try:
            f_val = float(val)
            result[field] = int(f_val) if f_val == int(f_val) and "." not in str(val) else f_val
        except (ValueError, TypeError):
            result[field] = 0
    return result
    
def _inject_signal(mode: str) -> dict:
    """Her atak türüne özgü, CSV'den bağımsız manipüle edilmiş sinyal üretir."""
    if mode == "Spoofing":
        return {
            "Speed_kmh":            random.uniform(30.0, 100.0), 
            "Acceleration_mps2":    random.uniform(-5.0, 5.0),
            "GPS_Lat":              13.0 + random.uniform(-0.02, 0.08),
            "GPS_Long":             77.5 + random.uniform(-0.02, 0.09),
            "Signal_Strength_dBm":  random.uniform(-98.0, -51.0),
            "Packet_Size_bytes":    random.randint(250, 600),
            "Transmission_Rate_Mbps": random.uniform(400.0, 850.0),
            "Latency_ms":           random.uniform(3.0, 8.0),
            "Jitter_ms":            random.uniform(0.01, 4.0),
            "Packet_Loss_percent":  random.uniform(0.5, 4.5),
            "Flow_Duration_ms":     random.uniform(500.0, 1150.0),
            
            "Total_Fwd_Packets":    random.randint(460, 498), 
            "Total_Bwd_Packets":    random.randint(2, 70),   
            
            "Avg_Packet_Length":    random.uniform(260.0, 800.0),
            "SYN_Flag_Count":       random.randint(20, 49),
            "ACK_Flag_Count":       random.randint(8, 35),

            "Flow_Bytes_per_s":     random.uniform(910000.0, 990000.0), 
            "Trust_Score":          random.uniform(0.0, 0.43),          
            "Encryption_Overhead_ms": random.uniform(0.01, 0.15),       
            "Authentication_Success": random.choices([0, 1], weights=[70, 30])[0], 
        }
    elif mode == "DoS":
        return {
            "Speed_kmh":            random.uniform(0.0, 50.0),
            "Acceleration_mps2":    random.uniform(-3.0, 3.0),
            "GPS_Lat":              13.0 + random.uniform(-0.05, 0.05),
            "GPS_Long":             77.5 + random.uniform(-0.05, 0.05),
            "Signal_Strength_dBm":  random.uniform(-115.0, -90.0),
            "Packet_Size_bytes":    random.randint(40, 200),
            "Transmission_Rate_Mbps": random.uniform(0.1, 5.0),
            "Latency_ms":           random.uniform(500.0, 2500.0),
            "Jitter_ms":            random.uniform(120.0, 500.0),
            "Packet_Loss_percent":  random.uniform(55.0, 98.0),
            "Flow_Duration_ms":     random.uniform(5000.0, 20000.0),
            "Total_Fwd_Packets":    random.randint(2000, 8000),
            "Total_Bwd_Packets":    random.randint(50, 300),
            "Avg_Packet_Length":    random.uniform(40.0, 150.0),
            "SYN_Flag_Count":       random.randint(800, 4000),
            "ACK_Flag_Count":       random.randint(5, 50),
            "Flow_Bytes_per_s":     random.uniform(60000.0, 300000.0),
            "Trust_Score":          random.uniform(0.1, 0.4),
            "Encryption_Overhead_ms": random.uniform(1.0, 8.0),
            "Authentication_Success": random.choices([0, 1], weights=[70, 30])[0],
        }
    elif mode == "Sybil":
        
        is_extreme = random.random() > 0.4
        
        if is_extreme:
            tx_rate = 999.99 
            ack_count = random.randint(0, 10)
        else:
            tx_rate = random.uniform(430.0, 850.0) 
            ack_count = 0 # Hız 999.99 değilse ACK KESİNLİKLE 0 olmalı

        return {
            "Speed_kmh":            random.uniform(20.0, 85.0),
            "Acceleration_mps2":    random.uniform(-5.0, 5.0),
            "GPS_Lat":              13.0 + random.uniform(-0.05, 0.05),
            "GPS_Long":             77.6 + random.uniform(-0.05, 0.05),
            "Signal_Strength_dBm":  random.uniform(-103.0, -80.0),
            "Packet_Size_bytes":    random.randint(800, 1100),
            
            "Transmission_Rate_Mbps": tx_rate,
            "ACK_Flag_Count":       ack_count,
            "SYN_Flag_Count":       random.randint(15, 45), # 48'in altında olmalı
            
            "Latency_ms":           random.uniform(2.0, 8.0),
            "Jitter_ms":            random.uniform(1.2, 3.8),
            "Packet_Loss_percent":  random.uniform(1.3, 3.8),
            "Flow_Duration_ms":     random.uniform(2500.0, 4500.0),
            "Total_Fwd_Packets":    random.randint(200, 400),
            "Total_Bwd_Packets":    random.randint(200, 400),
            "Avg_Packet_Length":    random.uniform(600.0, 900.0),
            "Flow_Bytes_per_s":     random.uniform(270000.0, 500000.0),
            "Trust_Score":          random.uniform(0.06, 0.40),
            "Encryption_Overhead_ms": random.uniform(0.25, 1.1),
            "Authentication_Success": random.choices([0, 1], weights=[80, 20])[0],
        }
    elif mode == "Data_Tampering":
        return {
            "Speed_kmh":            random.uniform(20.0, 100.0),
            "Acceleration_mps2":    random.uniform(-2.0, 2.0),
            "GPS_Lat":              13.0 + random.uniform(-0.03, 0.03),
            "GPS_Long":             77.5 + random.uniform(-0.03, 0.03),
            "Signal_Strength_dBm":  random.uniform(-85.0, -60.0),
            "Packet_Size_bytes":    random.randint(1, 60),
            "Transmission_Rate_Mbps": random.uniform(5.0, 40.0),
            "Latency_ms":           random.uniform(20.0, 120.0),
            "Jitter_ms":            random.uniform(10.0, 50.0),
            "Packet_Loss_percent":  random.uniform(5.0, 25.0),
            "Flow_Duration_ms":     random.uniform(200.0, 3000.0),
            "Total_Fwd_Packets":    random.randint(100, 800),
            "Total_Bwd_Packets":    random.randint(100, 800),
            "Avg_Packet_Length":    random.uniform(50.0, 300.0),
            "SYN_Flag_Count":       random.randint(5, 40),
            "ACK_Flag_Count":       random.randint(5, 40),
            "Flow_Bytes_per_s":     random.uniform(2000.0, 30000.0),
            "Trust_Score":          random.uniform(0.02, 0.25),
            "Encryption_Overhead_ms": random.uniform(60.0, 250.0),
            "Authentication_Success": 0,
        }

    return {field: 0 for field in SIGNAL_FIELDS}

def build_signal() -> dict:
    """Normal modda CSV satırı, inject modunda bozulmuş sinyal döndürür."""
    mode = sim_state["attack_mode"]
    
    # Süre dolduysa normale dön
    if mode != "Normal" and time.time() > sim_state["attack_until"]:
        sim_state["attack_mode"] = "Normal"
        mode = "Normal"

    if mode == "Normal":
        return _csv_row_to_signal(_next_csv_row())
    else:
        return _inject_signal(mode)


# ─── SSE Stream Endpoint ──────────────────────────────────────────────────────
@app.get("/stream")
async def signal_stream(request: Request):
    """Saniyede bir veri akıtan SSE Endpoint. Kullanıcı koptuğunda veya akış durduğunda yönetir."""
    async def event_generator():
        while True:
            # İstemci (tarayıcı) sekmeyi veya sayfayı kapattıysa döngüyü kır
            if await request.is_disconnected():
                print("[SSE] İstemci bağlantıyı kopardı.")
                break
            
            # Yalnızca is_streaming True ise (butona basılmışsa) veri üret ve modele gönder
            if sim_state["is_streaming"]:
                signal = build_signal()
                
                # ML modelini çağır
                attackType, confidence, if_score = ml_engine.predict(signal)

                payload = {
                    "signal": signal,
                    "prediction": {
                        "attack_type": attackType,
                        "confidence": confidence,
                        "anomaly_score": if_score
                    },
                    "active_attack": sim_state["attack_mode"] if sim_state["attack_mode"] != "Normal" else None,
                    "ground_truth": sim_state["attack_mode"]
                }

                yield f"data: {json.dumps(payload)}\n\n"
            else:
                # Akış durdurulmuş (is_streaming=False) ama tarayıcı bağlantısı henüz açık:
                # Bağlantı zaman aşımına uğramasın diye sadece yorum (ping) satırı gönder
                yield ": ping\n\n"
                
            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")