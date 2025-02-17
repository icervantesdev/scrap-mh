import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

class DataPreprocessor:
    def __init__(self, normalization_method='standard', categorical_encoding='onehot'):
        self.normalization_method = normalization_method
        self.categorical_encoding = categorical_encoding
        self.scaler = None
        self.encoder = None
        
    def load_data(self, file_path, delimiter=','):
        """Carga datos desde un archivo CSV."""
        return pd.read_csv(file_path, delimiter=delimiter)
    
    def clean_data(self, df):
        """Limpia los datos eliminando valores duplicados y tratando valores nulos."""
        df = df.drop_duplicates()
        df = df.dropna(how='all')  # Elimina filas completamente vacías
        return df
    
    def impute_missing_values(self, df, strategy='mean'):
        """Rellena valores nulos usando la estrategia especificada."""
        imputer = SimpleImputer(strategy=strategy)
        df[df.select_dtypes(include=['number']).columns] = imputer.fit_transform(df.select_dtypes(include=['number']))
        return df
    
    def normalize_data(self, df):
        """Normaliza los datos numéricos con el método especificado."""
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if self.normalization_method == 'standard':
            self.scaler = StandardScaler()
        elif self.normalization_method == 'minmax':
            self.scaler = MinMaxScaler()
        else:
            raise ValueError("Método de normalización no válido. Usa 'standard' o 'minmax'.")
        
        df[numeric_cols] = self.scaler.fit_transform(df[numeric_cols])
        return df
    
    def encode_categorical(self, df):
        """Codifica variables categóricas con el método especificado."""
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        if self.categorical_encoding == 'onehot':
            df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        elif self.categorical_encoding == 'label':
            from sklearn.preprocessing import LabelEncoder
            for col in categorical_cols:
                encoder = LabelEncoder()
                df[col] = encoder.fit_transform(df[col])
        else:
            raise ValueError("Método de codificación no válido. Usa 'onehot' o 'label'.")
        
        return df
    
    def preprocess(self, file_path):
        """Ejecuta el proceso completo de limpieza, normalización y transformación de datos."""
        df = self.load_data(file_path)
        df = self.clean_data(df)
        df = self.impute_missing_values(df)
        df = self.normalize_data(df)
        df = self.encode_categorical(df)
        return df
    
    def save_data(self, df, output_path):
        """Guarda los datos procesados en un archivo CSV."""
        df.to_csv(output_path, index=False)
        print(f"Datos guardados en {output_path}")

# Uso del script
def main():
    file_path = input("Ingresa la ruta del archivo CSV: ")  # Ruta del archivo de entrada
    output_path = 'processed_data.csv'  # Ruta del archivo de salida
    
    processor = DataPreprocessor(normalization_method='minmax', categorical_encoding='onehot')
    df_processed = processor.preprocess(file_path)
    processor.save_data(df_processed, output_path)

if __name__ == "__main__":
    main()