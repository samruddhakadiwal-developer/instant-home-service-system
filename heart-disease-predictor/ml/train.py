import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import xgboost as xgb
import json

def main():
    print("Loading dataset...")
    df = pd.read_csv("dataset.csv")
    
    # Sl No is an ID column, Target is the label
    X = df.drop(columns=["Sl No", "Target"])
    y = df["Target"]
    
    # Save the feature names so we can use them in the backend
    feature_names = list(X.columns)
    with open("feature_names.json", "w") as f:
        json.dump(feature_names, f)
        
    print(f"Features used: {feature_names}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Performing Hyperparameter Tuning with GridSearchCV...")
    param_grid = {
        'max_depth': [3, 4, 5],
        'learning_rate': [0.01, 0.1, 0.2],
        'n_estimators': [50, 100, 200]
    }
    
    base_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    grid_search = GridSearchCV(estimator=base_model, param_grid=param_grid, cv=3, scoring='accuracy', n_jobs=-1)
    
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters found: {grid_search.best_params_}")
    
    best_model = grid_search.best_estimator_
    
    print("Evaluating best model...")
    y_pred = best_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy on test set: {acc * 100:.2f}%")
    
    print("Saving model to model.json...")
    best_model.save_model("model.json")
    print("Model saved successfully!")

if __name__ == '__main__':
    main()
