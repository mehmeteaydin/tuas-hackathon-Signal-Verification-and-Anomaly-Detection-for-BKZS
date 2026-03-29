import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA


df = pd.read_csv("data/data_single_100k.csv")

print("Orijinal Veri Boyutu:", df.shape)


df = df.dropna()

yasakli_kolonlar = ['Vehicle_ID', 'Timestamp_ms', 'Target']

X = df.drop(columns=yasakli_kolonlar, errors='ignore').select_dtypes(include=['float64', 'int64'])

print(f"\nKullanılan Temiz Feature Sayısı: {len(X.columns)}")
print("Feature Listesi:", X.columns.tolist())

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    n_estimators=200,
    contamination= 0.21,      # Belirlenen anomali oranı
    max_samples='auto',
    random_state=42
)

model.fit(X_scaled)

df['anomaly'] = model.predict(X_scaled)   # -1: Anomali, 1: Normal
df['anomaly_score'] = model.decision_function(X_scaled)

df_sorted = df.sort_values(by='anomaly_score')

print("\nEn Şüpheli İlk 10 Veri (Top Anomalies):")
print(df_sorted[['anomaly', 'anomaly_score']].head(10))

plt.figure()
plt.hist(df['anomaly_score'], bins=50)
plt.title("Anomaly Score Distribution")
plt.xlabel("Score (Düşük = Daha Anormal)")
plt.ylabel("Frekans")
plt.savefig("graphs/anomaly_score_distribution.png")
# plt.show()

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure()
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df['anomaly'], cmap='coolwarm', alpha=0.6)
plt.title("Anomaly Visualization (PCA)")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.savefig("graphs/pca_visualization.png")
# plt.show()

feature_importance = np.abs(X_scaled).mean(axis=0)

importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': feature_importance
}).sort_values(by='Importance', ascending=False)

print("\nFeature Importance (Modelin En Çok Baktıkları - İlk 10):")
print(importance_df.head(10))


print("\n--- Sistem İstatistikleri ---")
if 'Vehicle_ID' in df.columns:
    print("Toplam farklı araç sayısı:", df['Vehicle_ID'].nunique())
print("Bulunan Anomali Sayısı (-1):", (df['anomaly'] == -1).sum())

export_filename = "result data/data_200K_with_anomalies.csv"
df.to_csv(export_filename, index=False)
