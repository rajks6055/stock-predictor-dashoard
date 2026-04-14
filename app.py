from model import predict_stock
from dash import Dash, html, dcc, Input, Output, State
import yfinance as yf
import plotly.graph_objs as go
from datetime import date
import pandas as pd

# Initialize the Dash app
app = Dash(__name__)
server = app.server

# --- LAYOUT (From Previous Step) ---
app.layout = html.Div(className='app-container', children=[
    
    # Left Sidebar
    html.Div(className='sidebar', children=[
        html.H2('Stock Intelligence'),
        
        html.Div(className='input-group', children=[
            html.Label('Enter Ticker (e.g., AAPL)'),
            dcc.Input(id='ticker-input', type='text', placeholder='Stock Code...', className='custom-input'),
            html.Button('Search', id='search-btn', className='action-btn')
        ]),
        
        html.Div(className='input-group', children=[
            html.Label('Select Start Date'),
            dcc.DatePickerSingle(
                id='date-picker',
                min_date_allowed=date(2010, 1, 1),
                max_date_allowed=date.today(),
                initial_visible_month=date.today(),
                date=date(2023, 1, 1)
            )
        ]),
        
        # We will wire these up later!
        html.Div(className='input-group', style={'flexDirection': 'row', 'gap': '10px'}, children=[
            html.Button('View Price', id='price-btn', className='action-btn', style={'flex': '1'}),
            html.Button('Indicators', id='indicator-btn', className='action-btn', style={'flex': '1'})
        ]),
        
        html.Div(className='input-group', style={'marginTop': '20px'}, children=[
            html.Label('Forecast Horizon (Days)'),
            dcc.Input(id='forecast-input', type='number', placeholder='e.g., 5', className='custom-input'),
            html.Button('Generate Forecast', id='forecast-btn', className='action-btn')
        ])
    ]),

    # === RIGHT MAIN CONTENT: Data Visualization ===
    html.Div(className='main-content', children=[
        
        # Company Info Card
        html.Div(className='card', id='company-info', children=[
            html.H3('Company Information', style={'marginTop': '0', 'color': '#64748b'}),
            html.P('Search for a stock ticker to see company details here.')
        ]),
        
        # NEW: Empty container for our KPI Cards
        html.Div(id='kpi-cards', className='kpi-row', children=[]),
        
        # Main Graph Card 
        html.Div(className='card', children=[
            dcc.Graph(id='stock-graph')
        ]),
        
        # ML Results Card
        html.Div(className='card', id='forecast-results', children=[
            html.H3('Machine Learning Forecast', style={'marginTop': '0', 'color': '#64748b'}),
            html.P('Input a forecast horizon to see projected prices.')
        ])
    ])

])

# --- CALLBACKS (The Brains) ---
@app.callback(
    [Output('company-info', 'children'),
     Output('stock-graph', 'figure'),
     Output('kpi-cards', 'children')], # NEW: Output for the KPI cards
    [Input('search-btn', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('date-picker', 'date')]
)
def update_data(n_clicks, ticker_val, start_date):
    if n_clicks is None or not ticker_val:
        return [
            html.Div([
                html.H3('Company Information', style={'marginTop': '0', 'color': '#64748b'}),
                html.P('Search for a stock ticker to see company details here.')
            ]),
            go.Figure(),
            [] # Return empty KPI cards initially
        ]

    try:
        # Fetch Data
        ticker = yf.Ticker(ticker_val)
        info = ticker.info
        df = ticker.history(start=start_date)

        # Build Company Info
        company_name = info.get('longName', ticker_val.upper())
        company_summary = info.get('longBusinessSummary', 'No description available.')
        
        info_div = html.Div([
            html.H3(company_name, style={'marginTop': '0', 'color': '#1e293b'}),
            html.P(company_summary, style={'fontSize': '0.9rem', 'lineHeight': '1.5'})
        ])

        # NEW: Build the KPI Cards!
        # We use .get() safely because yfinance data can sometimes be missing
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        high_52 = info.get('fiftyTwoWeekHigh', 0)
        low_52 = info.get('fiftyTwoWeekLow', 0)
        
        # Format Market Cap to Billions (e.g., "3.14B") for readability
        mcap_raw = info.get('marketCap', 0)
        mcap_formatted = f"${mcap_raw / 1_000_000_000:.2f}B" if mcap_raw else "N/A"

        kpi_divs = [
            html.Div(className='kpi-card', children=[
                html.Div('Current Price', className='kpi-title'),
                html.Div(f"${current_price:.2f}" if current_price else "N/A", className='kpi-value')
            ]),
            html.Div(className='kpi-card', children=[
                html.Div('52-Week High', className='kpi-title'),
                html.Div(f"${high_52:.2f}" if high_52 else "N/A", className='kpi-value')
            ]),
            html.Div(className='kpi-card', children=[
                html.Div('52-Week Low', className='kpi-title'),
                html.Div(f"${low_52:.2f}" if low_52 else "N/A", className='kpi-value')
            ]),
            html.Div(className='kpi-card', children=[
                html.Div('Market Cap', className='kpi-title'),
                html.Div(mcap_formatted, className='kpi-value')
            ])
        ]

        # Build the Graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price', line=dict(color='#1488CC', width=2)))
        fig.update_layout(title=f"{company_name} Historical Prices", xaxis_title="Date", yaxis_title="Price (USD)", template="plotly_white", margin=dict(l=0, r=0, t=40, b=0))

        # Return all 3 outputs!
        return [info_div, fig, kpi_divs]

    except Exception as e:
        error_div = html.Div([
            html.H3("Error", style={'color': 'red'}),
            html.P(f"Could not fetch data for '{ticker_val}'. Please check the ticker code.")
        ])
        return [error_div, go.Figure(), []]

@app.callback(
    Output('forecast-results', 'children'),
    [Input('forecast-btn', 'n_clicks')],
    [State('ticker-input', 'value'),
     State('forecast-input', 'value')]
)
def generate_forecast(n_clicks, ticker, n_days):
    if n_clicks is None:
        return [
            html.H3('Machine Learning Forecast', style={'marginTop': '0', 'color': '#64748b'}),
            html.P('Input a forecast horizon to see projected prices.')
        ]
        
    if not ticker:
        return html.P("⚠️ Error: Please scroll up and enter a Ticker code!", style={'color': 'red', 'fontWeight': 'bold'})
        
    if not n_days:
        return html.P("⚠️ Error: Please enter the number of days to forecast!", style={'color': 'red', 'fontWeight': 'bold'})

    try:
        from model import predict_stock
        
        # 1. Catch all 6 variables from the updated model
        hist_dates, hist_prices, future_dates, predicted_prices, mse, mae = predict_stock(ticker, int(n_days))
        
        if hist_dates is None:
            return html.P("Error: Could not train model on this ticker.", style={'color': 'red'})
            
        # 2. Build the Plotly Graph
        fig = go.Figure()
        
        # Trace 1: The Historical Data (Solid Blue Line)
        fig.add_trace(go.Scatter(
            x=hist_dates, y=hist_prices, mode='lines', name='Historical Data',
            line=dict(color='#1488CC', width=2)
        ))
        
        # Trace 2: The Forecast Data (Dashed Orange Line)
        # We add the last historical point to the start of the forecast so the lines connect seamlessly!
        connected_dates = [hist_dates[-1]] + future_dates
        connected_prices = [hist_prices[-1]] + list(predicted_prices)
        
        fig.add_trace(go.Scatter(
            x=connected_dates, y=connected_prices, mode='lines', name='ML Forecast',
            line=dict(color='#f59e0b', width=2, dash='dash')
        ))
        
        # Style the layout
        fig.update_layout(
            title=f"{ticker.upper()} - 60 Day History vs {n_days} Day Forecast",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            margin=dict(l=0, r=0, t=40, b=0),
            hovermode="x unified" # Adds a nice crosshair when hovering
        )

        # 3. Build the final UI to send back to the browser
        predictions_ui = [
            html.H3('Forecast Results', style={'marginTop': '0', 'color': '#1488CC'}),
            
            html.Div(children=[
                html.P(f"Model Mean Squared Error (MSE): {mse:.2f}", style={'margin': '0', 'fontWeight': 'bold', 'color': '#334155'}),
                html.P(f"Model Mean Absolute Error (MAE): {mae:.2f}", style={'margin': '0', 'fontWeight': 'bold', 'color': '#334155'}),
            ], style={'backgroundColor': '#e2e8f0', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '20px'}),
            
            # The new Graph component replaces the old text list!
            dcc.Graph(figure=fig)
        ]
            
        return predictions_ui
        
    except Exception as e:
        return html.P(f"A Python Error occurred: {str(e)}", style={'color': 'red'})


if __name__ == '__main__':
    app.run(debug=True)