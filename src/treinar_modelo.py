import os
import pandas as pd
import joblib
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def carregar_e_preparar_dados():
    """Lê o CSV validado e prepara as features e o target."""
    caminho_csv = Path("data/processed/dados_validos.csv")
    
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}. Rode a Fase 2 primeiro!")
    
    print("Lendo dados...")
    df = pd.read_csv(caminho_csv)
    
    features = ['produto', 'turno', 'operador', 'quantidade_inspecionada']
    X = df[features]
    y = df['defeito'].apply(lambda x: 1 if x == 'sim' else 0)
    
    return X, y

def criar_pipeline_modelo(modelo):
    """Cria um pipeline com One-Hot Encoding."""
    cat_cols = ['produto', 'turno', 'operador']
    num_cols = ['quantidade_inspecionada']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
            ('num', 'passthrough', num_cols)
        ])
    
    return Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', modelo)
    ])

def treinar_e_avaliar():
    print("=== FASE 4: TREINAMENTO DE MODELO DE ML ===")
    
    X, y = carregar_e_preparar_dados()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Dados de treino: {len(X_train)} | Dados de teste: {len(X_test)}")
    
    # 1. Modelo Baseline: Regressão Logística
    print("\n--- Treinando Baseline (Regressão Logística) ---")
    pipeline_lr = criar_pipeline_modelo(LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'))
    pipeline_lr.fit(X_train, y_train)
    y_pred_lr = pipeline_lr.predict(X_test)
    
    print(f"Acurácia Baseline: {accuracy_score(y_test, y_pred_lr):.4f}")
    print("Relatório de Classificação (Baseline):")
    print(classification_report(y_test, y_pred_lr, target_names=['Sem Defeito (0)', 'Com Defeito (1)'], zero_division=0))
    
    # 2. Modelo Principal: Random Forest (Ajustado para equilíbrio)
    print("\n--- Treinando Modelo Principal (Random Forest) ---")
    rf_model = RandomForestClassifier(
        n_estimators=200, 
        max_depth=8, 
        min_samples_leaf=2, 
        random_state=42, 
        class_weight='balanced'
    )
    pipeline_rf = criar_pipeline_modelo(rf_model)
    pipeline_rf.fit(X_train, y_train)
    
    # O threshold operacional fica fixo em 0,5; não otimizamos no conjunto de teste.
    y_proba_rf = pipeline_rf.predict_proba(X_test)[:, 1]
    melhor_threshold = 0.5
    y_pred_rf = (y_proba_rf >= melhor_threshold).astype(int)
    print(f"\nThreshold operacional: {melhor_threshold}")
    print(f"Acurácia Random Forest: {accuracy_score(y_test, y_pred_rf):.4f}")
    print("Relatório de Classificação (Random Forest):")
    print(classification_report(y_test, y_pred_rf, target_names=['Sem Defeito (0)', 'Com Defeito (1)'], zero_division=0))
    
    print("\nMatriz de Confusão (Random Forest):")
    print(confusion_matrix(y_test, y_pred_rf))
    
    # 3. Importância das Features
    print("\n--- Importância das Features ---")
    cat_encoder = pipeline_rf.named_steps['preprocessor'].named_transformers_['cat']
    cat_features = cat_encoder.get_feature_names_out(['produto', 'turno', 'operador'])
    all_features = np.concatenate([cat_features, ['quantidade_inspecionada']])
    
    importances = pipeline_rf.named_steps['classifier'].feature_importances_
    feature_importance_df = pd.DataFrame({'Feature': all_features, 'Importance': importances})
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
    print(feature_importance_df.head(5).to_string(index=False))
    
    # 4. Salvando o modelo
    print("\nSalvando o modelo...")
    os.makedirs("models", exist_ok=True)
    caminho_modelo = "models/modelo_rf.joblib"
    joblib.dump(
        {
            "artifact_version": 1,
            "model_version": "random_forest_v1",
            "training_seed": 42,
            "feature_names": ["produto", "turno", "operador", "quantidade_inspecionada"],
            "model": pipeline_rf,
            "threshold": melhor_threshold,
        },
        caminho_modelo,
    )
    print(f"✅ Modelo salvo com sucesso em: {caminho_modelo}")
    
    print("\n=== TREINAMENTO CONCLUÍDO ===")

if __name__ == "__main__":
    treinar_e_avaliar()
