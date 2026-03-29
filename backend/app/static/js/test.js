(function () {
    const MAX_POINTS = 50; // Grafikte görünecek maksimum nokta sayısı
    const HISTORY = [];
    let eventSource = null;
    let running = false;

    // Element Seçicileri
    const el = (id) => document.getElementById(id);
    const btnToggle = el("btnToggle");
    const decisionBox = el("decisionBox");
    const attackLabel = el("attackLabel");
    const attackReason = el("attackReason");
    const attackFlag = el("attackFlag");

    // Güvenli DOM Güncelleme Fonksiyonu (Eğer element sayfada varsa günceller)
    const safeSet = (id, val) => {
        const element = el(id);
        if (element) element.innerText = val;
    };

    // --------------------------------------------------
    // 📊 CHART.JS YAPILANDIRMASI
    // --------------------------------------------------
    const ctx = el("chartSignals").getContext("2d");
    const chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Hız Farkı",
                    data: [],
                    borderColor: "#ffb020",
                    tension: 0.3,
                    yAxisID: "ySpeed",
                },
                {
                    label: "Latency (ms)",
                    data: [],
                    borderColor: "#00d4aa",
                    backgroundColor: "rgba(0,212,170,0.1)",
                    fill: true,
                    tension: 0.3,
                    yAxisID: "yLat",
                },
                {
                    label: "Anomali Skoru",
                    data: [],
                    borderColor: "#5b8cff",
                    tension: 0.3,
                    yAxisID: "yScore",
                }
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // Performans için
            scales: {
                ySpeed: { type: 'linear', position: 'left', min: 0, suggestedMax: 100 },
                yLat: { type: 'linear', position: 'right', min: 0, suggestedMax: 500 },
                yScore: { type: 'linear', position: 'right', min: 0, max: 1, display: false }
            }
        }
    });

    // --------------------------------------------------
    // 🔄 UI GÜNCELLEME FONKSİYONU
    // --------------------------------------------------
    function updateDashboard(payload) {
        const s = payload.signal;
        const p = payload.prediction;

        // 1. Karar Paneli
        const cssClass = {
            "Normal": "normal", "DoS": "dos", "Spoofing": "spoofing",
            "Sybil": "sybil", "Data_Tampering": "tampering"
        }[p.attack_type] || "mixed";

        attackLabel.innerText = p.attack_type.toUpperCase().replace("_", " ");
        attackLabel.className = "attack-type " + cssClass;

        if (p.attack_type !== "Normal") {
            decisionBox.className = "decision attack-true below-chart";
            attackFlag.innerText = "attack = true";
            attackFlag.className = "flag on";
            attackReason.innerText = `Anomali: ${p.attack_type} (%${(p.confidence * 100).toFixed(1)})`;
        } else {
            decisionBox.className = "decision attack-false below-chart";
            attackFlag.innerText = "attack = false";
            attackFlag.className = "flag off";
            attackReason.innerText = "Veri akışı güvenli ve stabil.";
        }

        // 2. TÜM 20 METRİĞİN EŞLEŞTİRİLMESİ (Alt Bölüm İçin)
        // Araç Dinamiği
        safeSet('mSpeed', s.Speed_kmh.toFixed(1));
        safeSet('mAccel', s.Acceleration_mps2.toFixed(2));
        safeSet('mLat', s.GPS_Lat.toFixed(4));
        safeSet('mLong', s.GPS_Long.toFixed(4));

        // Ağ Trafiği
        safeSet('mLatency', s.Latency_ms.toFixed(1));
        safeSet('mJitter', s.Jitter_ms.toFixed(2));
        safeSet('mPacketLoss', s.Packet_Loss_percent.toFixed(2));
        safeSet('mTxRate', s.Transmission_Rate_Mbps.toFixed(2));
        safeSet('mFlowDur', s.Flow_Duration_ms.toFixed(0));
        safeSet('mFlowBps', s.Flow_Bytes_per_s.toFixed(0));
        safeSet('mAvgPktLen', s.Avg_Packet_Length.toFixed(1));
        safeSet('mFwdPkts', s.Total_Fwd_Packets);
        safeSet('mBwdPkts', s.Total_Bwd_Packets);

        // Sinyal & Bayraklar
        safeSet('mSignal', s.Signal_Strength_dBm.toFixed(1));
        safeSet('mSyn', s.SYN_Flag_Count);
        safeSet('mAck', s.ACK_Flag_Count);
        safeSet('mPktSize', s.Packet_Size_bytes);

        // Güvenlik
        safeSet('mTrustScore', s.Trust_Score.toFixed(3));
        safeSet('mEncOverhead', s.Encryption_Overhead_ms.toFixed(2) + " ms");
        safeSet('mAuth', s.Authentication_Success === 1 ? "BAŞARILI" : "HATA");

        // 2.5 AKTİF SALDIRI ÇERÇEVESİNDEKİ (Üst Bölüm) DİNAMİK METRİKLERİ GÜNCELLE
        safeSet('mLatency_active', s.Latency_ms.toFixed(1));
        safeSet('mPacketLoss_active', s.Packet_Loss_percent.toFixed(2));
        safeSet('mSyn_active', s.SYN_Flag_Count);
        safeSet('mFwdPkts_active', s.Total_Fwd_Packets);
        safeSet('mTrustScore_active', s.Trust_Score.toFixed(3));
        safeSet('mSignal_active', s.Signal_Strength_dBm.toFixed(1));
        safeSet('mAuth_active', s.Authentication_Success === 1 ? "BAŞARILI" : "HATA");
        safeSet('mPktSize_active', s.Packet_Size_bytes);
        safeSet('mTxRate_active', s.Transmission_Rate_Mbps.toFixed(2));
        safeSet('mAck_active', s.ACK_Flag_Count);
        safeSet('mEncOverhead_active', s.Encryption_Overhead_ms.toFixed(2) + " ms");
        safeSet('mFlowDur_active', s.Flow_Duration_ms.toFixed(0));
        safeSet('mSpeed_active', s.Speed_kmh.toFixed(1));

        // 3. Grafik (Hız ve Gecikme üzerinden devam)
        const timeLabel = new Date().toLocaleTimeString().split(' ')[0];
        chart.data.labels.push(timeLabel);
        chart.data.datasets[0].data.push(s.Speed_kmh);
        chart.data.datasets[1].data.push(s.Latency_ms);
        chart.data.datasets[2].data.push(p.anomaly_score);

        if (chart.data.labels.length > MAX_POINTS) {
            chart.data.labels.shift();
            chart.data.datasets.forEach(ds => ds.data.shift());
        }
        chart.update('none');
    }

    // --------------------------------------------------
    // 📡 SSE BAĞLANTISI VE AKIŞ KONTROLÜ
    // --------------------------------------------------
    async function startStream() {
        try {
            await fetch("/control_stream/start");
            console.log("Sunucu veri akışı başlatıldı.");
        } catch (err) {
            console.error("Akış başlatılırken hata oluştu:", err);
        }

        if (eventSource) eventSource.close();
        eventSource = new EventSource("/stream");

        eventSource.onmessage = (event) => {
            if (event.data === "ping") return;
            try {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            } catch (e) {
                console.error("Gelen veri parse edilemedi:", e);
            }
        };

        eventSource.onerror = () => {
            console.error("Akış kesildi veya bağlanılamıyor.");
            stopStream();
        };
    }

    async function stopStream() {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
        try {
            await fetch("/control_stream/stop");
            console.log("Sunucu veri akışı durduruldu.");
        } catch (err) {
            console.error("Akış durdurulurken hata oluştu:", err);
        }

        running = false;
        btnToggle.innerText = "Akışı başlat";
        btnToggle.className = "primary";
    }

    btnToggle.addEventListener("click", () => {
        if (!running) {
            running = true;
            btnToggle.innerText = "Akışı durdur";
            btnToggle.className = "secondary";
            startStream();
        } else {
            stopStream();
        }
    });

    // --------------------------------------------------
    // 🌊 SALDIRI ENJEKSİYONU & DİNAMİK BİLGİ EKRANI
    // --------------------------------------------------

    // Her saldırının hedef aldığı parametrelerin HTML yapıları
    const activeMetricsMap = {
        "Normal": `
            <div class="metric"><label>Hız (km/h)</label><span class="value" id="mSpeed_active">—</span></div>
            <div class="metric"><label>Güven Skoru</label><span class="value" id="mTrustScore_active">—</span></div>
            <div class="metric"><label>Gecikme (ms)</label><span class="value" id="mLatency_active">—</span></div>
        `,
        "dos": `
            <div class="metric"><label>Gecikme (ms)</label><span class="value" id="mLatency_active">—</span></div>
            <div class="metric"><label>Paket Kaybı (%)</label><span class="value" id="mPacketLoss_active">—</span></div>
            <div class="metric"><label>SYN Bayrağı</label><span class="value" id="mSyn_active">—</span></div>
            <div class="metric"><label>Fwd Paketler</label><span class="value" id="mFwdPkts_active">—</span></div>
        `,
        "spoofing": `
            <div class="metric"><label>Güven Skoru</label><span class="value" id="mTrustScore_active">—</span></div>
            <div class="metric"><label>Sinyal (dBm)</label><span class="value" id="mSignal_active">—</span></div>
            <div class="metric"><label>Kimlik Doğrulama</label><span class="value" id="mAuth_active">—</span></div>
        `,
        "sybil": `
            <div class="metric"><label>Paket Boyutu (B)</label><span class="value" id="mPktSize_active">—</span></div>
            <div class="metric"><label>İletim Hızı (Mbps)</label><span class="value" id="mTxRate_active">—</span></div>
            <div class="metric"><label>ACK Bayrağı</label><span class="value" id="mAck_active">—</span></div>
        `,
        "tampering": `
            <div class="metric"><label>Şifreleme Ek Yükü</label><span class="value" id="mEncOverhead_active">—</span></div>
            <div class="metric"><label>Kimlik Doğrulama</label><span class="value" id="mAuth_active">—</span></div>
            <div class="metric"><label>Akış Süresi (ms)</label><span class="value" id="mFlowDur_active">—</span></div>
        `
    };

    const attackDescriptions = {
        "Normal": { title: "✅ Normal Ağ Trafiği", desc: "Sistem olağan seyrinde. Anormal bir yığılma tespit edilmiyor.", color: "#4ade80" },
        "dos": { title: "🌊 Denial of Service (DoS)", desc: "Ağ trafiği boğuluyor. <strong>Gecikme, Paket Kaybı ve SYN</strong> fırlıyor.", color: "#3b82f6" },
        "spoofing": { title: "🎭 Spoofing", desc: "Sahte konum/kimlik üretiliyor. <strong>Güven skoru düşüyor, Sinyal tutarsızlaşıyor.</strong>", color: "#a855f7" },
        "sybil": { title: "👯 Sybil Attack", desc: "Çoklu sahte node'lar oluşturuluyor. <strong>Paket Boyutu artıyor, ACK sıfırlanıyor.</strong>", color: "#f97316" },
        "tampering": { title: "🛠️ Data Tampering", desc: "Veri paketleri yolda değiştiriliyor. <strong>Şifreleme yükü artıyor, Doğrulama düşüyor.</strong>", color: "#ef4444" }
    };

    document.querySelectorAll("[data-inject]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const type = btn.getAttribute("data-inject"); // "dos", "spoofing", vb.

            const map = {
                "dos": "DoS", "spoofing": "Spoofing", "sybil": "Sybil",
                "tampering": "Data_Tampering", "Normal": "Normal"
            };

            const attackType = map[type] || "Normal";

            try {
                const response = await fetch(`/inject/${attackType}`);
                const result = await response.json();
                console.log("Enjeksiyon Yanıtı:", result);

                // Bilgi ekranını dinamik güncelle
                const infoFrame = el("attackInfoFrame");
                const infoTitle = el("infoTitle");
                const infoDesc = el("infoDesc");
                const activeMetricsContainer = el("activeMetricsContainer");

                const data = attackDescriptions[type] || attackDescriptions["Normal"];
                infoTitle.textContent = data.title;
                infoTitle.style.color = data.color;
                infoFrame.style.borderLeftColor = data.color;
                infoDesc.innerHTML = data.desc;

                // Seçilen saldırıya özel metric HTML'lerini içeri bas
                activeMetricsContainer.innerHTML = activeMetricsMap[type] || activeMetricsMap["Normal"];

                infoFrame.style.display = "block";

                btn.style.opacity = "0.5";
                setTimeout(() => btn.style.opacity = "1", 500);
            } catch (err) {
                console.error("Enjeksiyon hatası:", err);
            }
        });
    });

})();