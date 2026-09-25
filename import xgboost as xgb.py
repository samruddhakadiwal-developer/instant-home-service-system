import xgboost as xgb

model = xgb.XGBRegressor()
model.fit(X_train, y_train)

score = model.predict([[distance, rating, experience, price]])