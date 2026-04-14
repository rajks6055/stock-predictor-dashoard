import yfinance as yf
import numpy as np
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import timedelta

def predict_stock(ticker, days_to_forecast):
    print(f"--- Fetching 60 days of data for {ticker} ---")
    
    # 1. Fetch exactly 60 days of data
    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(period="60d")
    
    if df.empty:
        return None, None, None, None
        
    df.reset_index(inplace=True)
    
    # 2. Prepare Features (X) and Target (Y)
    X = np.array([i for i in range(len(df))]).reshape(-1, 1)
    Y = df['Close'].values
    
    # 3. Split the dataset (90% Train, 10% Test)
    # CRITICAL: shuffle=False ensures we train on the oldest 54 days, and test on the newest 6 days
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1, shuffle=False)
    
    # 4. Hyperparameter Tuning using GridSearchCV with RBF Kernel
    print("--- Running GridSearchCV (This might take a few seconds) ---")
    param_grid = {
        'C': [0.1, 1, 10, 100, 1000],
        'gamma': [1, 0.1, 0.01, 0.001, 0.0001]
    }
    
    # cv=5 means 5-fold cross-validation
    gsc = GridSearchCV(estimator=SVR(kernel='rbf'), param_grid=param_grid, cv=5, scoring='neg_mean_squared_error')
    grid_result = gsc.fit(X_train, Y_train)
    
    # Get the best model from the grid search
    best_svr = grid_result.best_estimator_
    print(f"--- Best Parameters Found: {grid_result.best_params_} ---")
    
    # 5. Test the model's performance on the 10% testing data
    Y_pred = best_svr.predict(X_test)
    mse = mean_squared_error(Y_test, Y_pred)
    mae = mean_absolute_error(Y_test, Y_pred)
    
    # 6. Generate Future Forecast
    last_day = X[-1][0]
    future_days = np.array([last_day + i for i in range(1, days_to_forecast + 1)]).reshape(-1, 1)
    predicted_prices = best_svr.predict(future_days)
    
    # Convert numbers back to real date
    # Convert numbers back to real dates
    last_real_date = df['Date'].iloc[-1]
    future_dates = [last_real_date + timedelta(days=i) for i in range(1, days_to_forecast + 1)]
    
    # NEW: Grab the historical data so we can connect the lines on the graph
    historical_dates = df['Date'].tolist()
    historical_prices = df['Close'].tolist()
    
    # NEW: Return 6 variables instead of 4
    return historical_dates, historical_prices, future_dates, predicted_prices, mse, mae