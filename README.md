# 🛡️ BKZS için Sinyal Doğrulama ve Anomali Tespiti 

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0.3-orange.svg)](https://xgboost.readthedocs.io/)
[![Isolation Forest](https://img.shields.io/badge/IsolationForest-ScikitLearn-green.svg)](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)


> **Bölgesel Konumlama ve Zamanlama Sistemi (BKZS) için Sinyal Doğrulama ve Anomali Tespit Yazılımı**

Türkiye'nin kritik navigasyon altyapısını GPS spoofing ve jamming saldırılarına karşı koruyan makine öğrenmesi tabanlı açık kaynaklı anomali tespit sistemi.

## 📊 Performans Metrikleri

| Metrik | Değer |
|--------|-------|
| 🎯 Training Accuracy | **91%** |
| ✅ Test Accuracy | **91%** |
| 🎯 Precision | **%93** |
| 🔍 Recall | **85%** |
| ⚖️ F1-Score | **91%** |

---

## 🎯 Özellikler

- ✅ **Gerçek Zamanlı Anomali Tespiti:** <100ms gecikme ile GPS spoofing/DoS saldırılarını tespit eder
- ✅ **Yüksek Doğruluk:** %91 test accuracy ile operasyonel kullanıma hazır
- ✅ **RESTful API:** FastAPI ile entegre edilebilir endpoint'ler
- ✅ **Modern Web UI:** Gerçek zamanlı dashboard ve görselleştirme
- ✅ **Açık Kaynak:** Şeffaf metodoloji ve topluluk katkısına açık
- ✅ **Feature Engineering:** 48 özellikten akıllıca seçilmiş 25 kritik özellik
- ✅ **Ensemble Learning:** XGBoost + Isolation Forest hibrit yaklaşım

---

## 🏗️ Mimari

```
┌─────────────────┐
│   Veri Kaynağı  │  (5G-VANET-IoT Dataset)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessing  │  (Normalization, Temporal Features, Semantic )
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Feature Eng.    │  (48 → 25 Features)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  XGBoost Model  │  (Anomaly Classification)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │  (REST Endpoints)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Web UI        │  (Dashboard & Visualization)
└─────────────────┘
```

---

## 📁 Proje Yapısı

```
bkzs/
│
├── backend/app/
│   ├── __init__.py             
│   ├── main.py                 # FastAPI application
│   ├── ml_engine.py            # Trained Model Engine
│   ├── schemas.py              # Signal model
│   ├── models_bin/
│   │   ├── xgboost_model.pkl   # Trained model
│   │   ├── scaler.pkl          # Feature scaler
│   │   └── feature_selector.pkl
│   ├── templates/
|   |   ├── index.html      
|   |   ├── test.html
|   |
│   ├── static/
|   |   ├── test.js
|   |   ├── utils.css
|   |   ├── styles.css
├── frontend/
│   ├── index.html              # Main dashboard
│   ├── styles.css
│   └── script.js
│
├── data/
│   ├── raw/
│
├── README.md
└── requirements.txt
```

---

## 🔧 Teknoloji Yığını

### Backend
- **Framework:** FastAPI 0.109.0
- **ML Model:** XGBoost 2.0.3
- **Anomaly Detection:** Isolation Forest (scikit-learn 1.4.0)
- **Data Processing:** Pandas 2.2.0, NumPy 1.26.3
- **Server:** Uvicorn 0.27.0

### Frontend
- **UI:** HTML5, CSS3, Vanilla JavaScript
- **Visualization:** Chart.js
- **HTTP Client:** Fetch API

### Data Science
- **Feature Engineering:** Custom pipeline

---

## 📡 API Endpoint'leri

### POST `/predict`
Tek sinyal örneği için tahmin yapar.

**Request:**
```json
{
  "latency": 45.2,
  "throughput": 78.5,
  "signal_strength": -85.0,
  "packet_loss": 2.3,
  "jitter": 12.1,
  "snr": 15.2,
  "error_rate": 0.05,
  "authentication_time": 120.0,
  "encryption_overhead": 8.5
}
```

**Response:**
```json
{
  "prediction": "anomaly",
  "confidence": 0.87,
  "anomaly_score": -0.65,
  "risk_level": "high",
  "timestamp": "2025-03-29T10:30:45Z"
}
```

### POST `/inject/{attack_type}`
Çoklu sinyal örneği için toplu tahmin.

**Request:**
```json
{
  "samples": [
    { "latency": 45.2, "throughput": 78.5, ... },
    { "latency": 32.1, "throughput": 92.3, ... }
  ]
}
```

### GET `/stream`
Sistemin sinyal veri akışı durumu.

**Response:**
```json
{
  "status": "healthy",
  "uptime": "5 days, 3:24:15",
  "model_version": "1.0.0",
  "memory_usage_mb": 198.5,
  "request_count": 15234
}
```

## 🧪 Veri Seti

**Kaynak:** [Kaggle - 5G-VANET-IoT Ultra-Low Latency Security Data](https://www.kaggle.com/datasets/colabsss/5g-vanet-iot-ultra-low-latency-security-data)

**İçerik:**
- 5G ağlarında Vehicular Ad-hoc Networks (VANET) güvenlik verileri
- IoT cihaz iletişim metrikleri
- Spoofing ve jamming saldırı örnekleri

**Özellikler:**
- `latency`, `throughput`, `signal_strength`, `packet_loss`, `jitter`
- `snr`, `error_rate`, `authentication_time`, `encryption_overhead`
- Zaman damgaları ve araç kimlikleri

---

## 🎓 Metodoloji

### 1. Veri Zenginleştirme
- Semantik snapshot'lar ile temporal özellikler
- Isolation Forest ile anomaly scoring
- Domain bilgisi ile feature engineering

### 2. Data Leakage Önleme
- Vehicle ID bazlı grup split
- GroupKFold cross-validation
- Temporal validation stratejisi

### 3. Model Eğitimi
- XGBoost sınıflandırma
- Feature importance ile 48→25 özellik seçimi
- Early stopping ve regularization

### 4. Değerlendirme
- %70-15-15 train-validation-test split
- Confusion matrix ve ROC-AUC analizi

---

## 🚧 Geliştirme Süreci

### Karşılaşılan Zorluklar

#### ❌ Zorluk 1: Düşük İlk Accuracy (%10)
**Sebep:** Ham veri yetersiz  
**Çözüm:** Veri zenginleştirme ve feature engineering

#### ❌ Zorluk 2: Data Leakage (Kritik!)
**Sebep:** Aynı araç ID'leri train ve test setinde  
**Çözüm:** ID bazlı grup split → Gerçekçi %75 accuracy

#### ❌ Zorluk 3: Simülasyon Gap
**Sebep:** Farklı veri dağılımı  
**Çözüm:** Domain adaptation ve fine-tuning stratejileri

#### ❌ Zorluk 4: Overfitting
**Sebep:** 48 özellik çok fazla  
**Çözüm:** Feature selection (48→25)

## 🤖 Yapay Zeka Beyanı

Bu proje geliştirilirken yapay zeka araçları yardımcı araç olarak kullanılmıştır:

- **Kod Yazımı (%30):** GitHub Copilot, boilerplate kod üretimi
- **Veri Analizi (%40):** EDA stratejileri, feature engineering önerileri
- **Model Optimizasyonu (%35):** Hiperparametre tuning, cross-validation metodları
- **Dokümantasyon (%25):** README taslakları, kod yorumları

⚠️ **Önemli:** Proje fikri, problem çözme yaklaşımı ve kritik kararlar tamamen takım üyeleri tarafından alınmıştır.

---

## 👥 Takım

- 5 kişilik geliştirici takımı
- Roller: ML Engineer, Backend Dev, Frontend Dev, Data Scientist, Project Manager

---

---

## 🔗 Referanslar

1. [Kaggle Dataset](https://www.kaggle.com/datasets/colabsss/5g-vanet-iot-ultra-low-latency-security-data)
2. [TUA - Türkiye Uzay Ajansı](https://tua.gov.tr)
3. [ESA Navigation](https://www.esa.int/Applications/Navigation)
4. [NASA GPS Technology](https://www.nasa.gov/)
5. [XGBoost Documentation](https://xgboost.readthedocs.io/)
6. [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🌟 Yıldız Vermeyi Unutmayın!

Projeyi beğendiyseniz ⭐ vermeyi unutmayın!

---

**© 2026 BKZS Anti-Spoofing Project | Türkiye Uzay Ajansı**
