from pydantic import BaseModel, Field
from typing import Optional

class GNSSSignal(BaseModel):
    Speed_kmh: float
    Acceleration_mps2: float
    GPS_Lat: float
    GPS_Long: float
    Signal_Strength_dBm: float
    Packet_Size_bytes: int
    Transmission_Rate_Mbps: float
    Latency_ms: float
    Jitter_ms: float
    Packet_Loss_percent: float
    Flow_Duration_ms: float
    Total_Fwd_Packets: int
    Total_Bwd_Packets: int
    Avg_Packet_Length: float
    SYN_Flag_Count: int
    ACK_Flag_Count: int
    Flow_Bytes_per_s: float
    Trust_Score: float
    Encryption_Overhead_ms: float
    Authentication_Success: int

class PredictResponse(BaseModel):
    attack_type: str
    confidence: float
    anomaly_score: float
    shap_explanations: dict