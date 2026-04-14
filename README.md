# 📈 Stock Intelligence & Machine Learning Dashboard

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Dash](https://img.shields.io/badge/Dash-Plotly-008080)
![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-F7931E)
![Status](https://img.shields.io/badge/Status-Live-success)

A modern, enterprise-grade web application built to visualize historical stock market data and generate future price forecasts using Machine Learning (Support Vector Regression). 

## ✨ Key Features

* **Interactive Financial UI:** A sleek, modern dashboard built with Dash and CSS Grid, featuring real-time KPI metrics (Current Price, 52-Week High/Low, Market Cap).
* **Live Market Data:** Integrates directly with the `yfinance` API to pull the most up-to-date historical market data.
* **Machine Learning Forecasting:** Utilizes an advanced Support Vector Regression (SVR) model with an RBF kernel.
* **Automated Hyperparameter Tuning:** Implements `GridSearchCV` to mathematically determine the best `C` and `gamma` parameters for each unique stock.
* **Seamless Visualization:** Employs Plotly to render dynamic, interactive charts where historical data seamlessly connects to dashed future predictions.
* **Performance Metrics:** Evaluates model accuracy in real-time, displaying Mean Squared Error (MSE) and Mean Absolute Error (MAE) for every forecast.

---

## 🏗️ System Architecture

The following flowchart illustrates the data pipeline and user request lifecycle within the application:

```mermaid
graph TD
    %% Define Nodes
    UI[🖥️ User Interface<br>React/Dash Frontend]
    App[⚙️ app.py<br>Routing & Callbacks]
    YF[(📊 yfinance API<br>Live Market Data)]
    Model[🧠 model.py<br>ML Engine]
    SVR[📈 SVR + GridSearchCV<br>Training Pipeline]
    
    %% Define Connections
    UI -->|1. Enters Ticker & Days| App
    App -->|2. Requests 60-day History| YF
    YF -->|3. Returns DataFrame & KPIs| App
    App -->|4. Sends Data for Training| Model
    Model -->|5. Initiates Tuning| SVR
    SVR -->|6. Predicts Future Prices| Model
    Model -->|7. Returns Dates, Prices & Metrics| App
    App -->|8. Renders Plotly Graph| UI

    %% Styling
    style UI fill:#1e293b,stroke:#1488CC,stroke-width:2px,color:#fff
    style App fill:#f4f7f6,stroke:#1488CC,stroke-width:2px
    style YF fill:#e2e8f0,stroke:#f59e0b,stroke-width:2px
    style Model fill:#f4f7f6,stroke:#1488CC,stroke-width:2px
    style SVR fill:#e2e8f0,stroke:#f59e0b,stroke-width:2px
