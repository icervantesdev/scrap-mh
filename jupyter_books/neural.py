import pandas as pd
from sqlalchemy import create_engine
import os
import mysql.connector
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
import numpy as np

# Database connection parameters
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='production_db'
)

# Load data from tables
query_user = "SELECT id, score FROM users;"
users = pd.read_sql(query_user, conn)

query_orders = """
    SELECT 
        o.id AS order_id, 
        om.user_id, 
        o.order_state_id, 
        om.payment_id,
        o.comment,
        o.total_orden
    FROM 
        orders o
    INNER JOIN 
        order_main om ON o.main_order_id = om.id;
"""
orders = pd.read_sql(query_orders, conn)

query_cart = "SELECT user_id, created_at FROM carts;"
carts = pd.read_sql(query_cart, conn)

query_order_items = """
SELECT 
    om.user_id, 
    COUNT(oi.product_id) AS product_count,
    AVG(o.total_orden) AS avg_order_value
FROM 
    det_order oi
INNER JOIN 
    orders o ON oi.order_id = o.id
INNER JOIN 
    order_main om ON o.main_order_id = om.id
GROUP BY 
    om.user_id;
"""
order_items = pd.read_sql(query_order_items, conn)
conn.close()

# Data preparation
orders['is_canceled'] = orders['order_state_id'].apply(lambda x: 1 if x == 4 else 0)

customer_related_reasons = [
    'CLIENTE_SOLICITO_ANTES_DE_GENERAR_GUIA',
    'CLIENTE_SOLICITO_DESPUES_DE_GENERAR_GUIA_NO_RECOLECTADO',
    'CLIENTE_SOLICITO_DESPUES_DE_GENERAR_GUIA_RECOLECTADO',
    'CLIENTE_NO_ACEPTO_PRODUCTO',
    'IMPOSIBLE_LOCALIZAR_CLIENTE',
    'FRAUDE_DETECTADO_CLIENTE',
    'CLIENTE_SE_COMUNICA_CANCELAR_ENVIO'
]

# Flagging orders with customer-related cancellation reasons
orders['customer_related_cancellation'] = orders.apply(
    lambda row: 1 if row['is_canceled'] == 1 and row['comment'] in customer_related_reasons else 0, 
    axis=1
)

# Aggregating data
canceled_orders = orders.groupby('user_id')['is_canceled'].sum().reset_index()
customer_related_cancellations = orders.groupby('user_id')['customer_related_cancellation'].sum().reset_index()
order_counts = orders.groupby('user_id')['order_id'].count().reset_index()
order_data = pd.merge(canceled_orders, order_counts, on='user_id')
order_data = pd.merge(order_data, customer_related_cancellations, on='user_id')
order_data = pd.merge(order_data, order_items[['user_id', 'avg_order_value']], on='user_id', how='left')
order_data['cancel_rate'] = order_data['is_canceled'] / order_data['order_id']

# Merge with user data
data = pd.merge(users, order_data, left_on='id', right_on='user_id', how='left')
data = pd.merge(data, carts.groupby('user_id').size().reset_index(name='cart_count'), left_on='id', right_on='user_id', how='left')

# Fill missing values
data['cancel_rate'].fillna(0, inplace=True)
data['cart_count'].fillna(0, inplace=True)
data['customer_related_cancellation'].fillna(0, inplace=True)
data['avg_order_value'].fillna(data['avg_order_value'].mean(), inplace=True)

# Define features and target
features = ['cancel_rate', 'cart_count', 'customer_related_cancellation', 'avg_order_value']
target = 'score'

# Prepare data for training
X = data[features]
y = data[target]

# Normalize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Build neural network model with regularization
model = Sequential([
    Dense(32, input_dim=X_train.shape[1], activation='relu', kernel_regularizer=l2(0.01)),
    Dropout(0.2),
    Dense(16, activation='relu', kernel_regularizer=l2(0.01)),
    Dense(1, activation='linear')
])

model.compile(optimizer=Adam(), loss='mse', metrics=['mae'])

# Early stopping callback
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train the model with cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
for train_index, val_index in kf.split(X_train):
    X_kf_train, X_kf_val = X_train[train_index], X_train[val_index]
    y_kf_train, y_kf_val = y_train.iloc[train_index], y_train.iloc[val_index]
    
    model.fit(X_kf_train, y_kf_train, epochs=50, batch_size=32, validation_data=(X_kf_val, y_kf_val), callbacks=[early_stopping])

# Predict and update user scores
predicted_scores = model.predict(scaler.transform(data[features]))
data['predicted_score'] = np.clip(predicted_scores, 0, 5)  # Ensure the score is between 0 and 5

# Guardar todos los valores calculados junto con el score en un archivo CSV
csv_filename = 'user_scores_with_features.csv'
data[['id', 'predicted_score', 'cancel_rate', 'cart_count', 'customer_related_cancellation', 'avg_order_value']].rename(
    columns={'id': 'user_id', 'predicted_score': 'score'}).to_csv(csv_filename, index=False)
print(f"Data saved to {csv_filename}")
