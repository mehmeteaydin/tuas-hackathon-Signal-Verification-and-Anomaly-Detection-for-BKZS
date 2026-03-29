import joblib
import numpy as np
import pandas as pd
from pathlib import Path

classes = ["Normal", "Spoofing", "DoS", "Sybil", "Data_Tampering"]

class MLEngine:
    def __init__(self):
        models_dir = Path(__file__).resolve().parent.parent / "models_bin"
        
        self.model = joblib.load(models_dir / "xgb_model.pkl")
        self.scaler = joblib.load(models_dir / "robust_scaler.pkl")
        self.encoder = joblib.load(models_dir / "label_encoder.pkl")
            

        # Model feature list
        if self.model and hasattr(self.model, "feature_names_in_"):
            self.expected_features = list(self.model.feature_names_in_)

        # Sınıf isimlerini al
        if self.encoder and hasattr(self.encoder, "classes_"):
            self.classes = list(self.encoder.classes_)
        else:
            self.classes = classes


    def predict(self, features_dict: dict) -> tuple:
        if not self.model:
            return "HATA", 0.0, 0.0

        df = pd.DataFrame([features_dict])
        df = df.apply(pd.to_numeric, errors="coerce")

        if df.isnull().any().any():
            df.fillna(0, inplace=True)

        for col in self.expected_features:
            if col not in df.columns:
                df[col] = 0.0
        df = df[self.expected_features]

        # Scaler
        if self.scaler is not None:
            try:
                scale_cols = getattr(self.scaler, 'feature_names_in_', self.expected_features)
                scale_cols = [c for c in self.expected_features if c in scale_cols]
                if scale_cols:
                    df[scale_cols] = self.scaler.transform(df[scale_cols])
            except Exception as e:
                pass

        # Predict
        try:
            raw_pred = self.model.predict(df)[0]
            if isinstance(raw_pred, (int, np.integer)):
                predicted_class = self.classes[raw_pred] if 0 <= raw_pred < len(self.classes) else str(raw_pred)
            else:
                predicted_class = str(raw_pred)
                
            proba = self.model.predict_proba(df)[0]
            confidence = float(np.max(proba))
        except Exception as e:
            return "HATA", 0.0, 0.0

        if_score = round(-confidence * 0.8, 4) if predicted_class != "Normal" else round(confidence * 0.3, 4)
        
        return predicted_class, confidence, if_score
