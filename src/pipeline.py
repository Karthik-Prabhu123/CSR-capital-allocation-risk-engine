import numpy as np
import pandas as pd
import sqlite3
import os
import pickle
from sklearn.linear_model import Ridge
from src.database import DB_NAME, get_db_connection, BASE_DIR

def run_analytics_pipeline():
    np.random.seed(42)
    num_entities = 120
    entity_ids = [f"PRJ_{i:03d}" for i in range(1, num_entities + 1)]
    themes = np.random.choice(["Healthcare Access", "Primary Education", "Renewable Infrastructure", "Clean Water Delivery"], size=num_entities)
    funding_reqs = np.random.uniform(500000, 7500000, num_entities)
    years_active = np.random.randint(1, 12, size=num_entities)
    
    df_proposals = pd.DataFrame({
        'entity_id': entity_ids, 
        'project_name': [f"Initiative {i}" for i in range(1, num_entities + 1)],
        'thematic_area': themes, 
        'requested_funding_inr': funding_reqs, 
        'track_record_years': years_active
    })
    
    env_scores = np.random.uniform(40, 100, num_entities)
    social_scores = np.random.uniform(45, 100, num_entities)
    gov_risk = np.random.uniform(10, 50, num_entities)
    cost_per_head = np.random.uniform(200, 2500, num_entities)
    
    df_metrics = pd.DataFrame({
        'entity_id': entity_ids, 
        'environmental_score': env_scores,
        'social_efficacy_score': social_scores, 
        'governance_risk_rating': gov_risk,
        'cost_per_beneficiary': cost_per_head
    })
    
    conn = get_db_connection()
    df_proposals.to_sql('proposals', conn, if_exists='replace', index=False)
    df_metrics.to_sql('risk_metrics', conn, if_exists='replace', index=False)
    
    query = """
        SELECT p.entity_id, p.thematic_area, p.requested_funding_inr, p.track_record_years,
               r.environmental_score, r.social_efficacy_score, r.governance_risk_rating, r.cost_per_beneficiary
        FROM proposals p
        JOIN risk_metrics r ON p.entity_id = r.entity_id
    """
    df_master = pd.read_sql_query(query, conn)
    
    df_master['allocation_priority_index'] = (
        (df_master['environmental_score'] * 0.25) + 
        (df_master['social_efficacy_score'] * 0.35) + 
        (df_master['track_record_years'] * 2.0) - 
        (df_master['governance_risk_rating'] * 0.4)
    ).clip(0, 100)
    
    features = ['requested_funding_inr', 'track_record_years', 'environmental_score', 'social_efficacy_score', 'governance_risk_rating']
    X = df_master[features]
    y = df_master['allocation_priority_index']
    
    reg_model = Ridge(alpha=1.0)
    reg_model.fit(X, y)
    
    df_master.to_sql('optimized_allocation_matrix', conn, if_exists='replace', index=False)
    conn.close()
    
    output_folder = os.path.join(BASE_DIR, "output")
    os.makedirs(output_folder, exist_ok=True)
    with open(os.path.join(output_folder, "allocation_regressor.pkl"), "wb") as f:
        pickle.dump(reg_model, f)
        
    print(f"📊 Processed {num_entities} requests. Optimization models saved successfully.")

if __name__ == "__main__":
    run_analytics_pipeline()