import pandas as pd  # Para manipulación y análisis de datos
import dash  # Framework para crear dashboards interactivos
from dash import dcc, html  # Componentes de Dash para UI (gráficos, controles, texto)
from dash.dependencies import Input, Output  # Para crear interactividad en el dashboard
import plotly.express as px  # Para crear gráficos interactivos fácilmente

# Datos de ejemplo
data = {
    'Date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
    'Category': ['Electronics', 'Clothing', 'Furniture', 'Food'] * 25,
    'Sales': [100, 150, 200, 130, 170, 210, 160, 180, 220, 140] * 10
}
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])

# Inicializamos la app Dash
app = dash.Dash(__name__)
app.title = "Dashboard de Ventas - Tema Oscuro"

# Estilos CSS para tema oscuro y layout
styles = {
    'body': {
        'backgroundColor': '#121212',
        'color': '#E0E0E0',
        'fontFamily': 'Arial, sans-serif',
        'margin': '0',
        'padding': '0',
        'height': '100vh',
        'display': 'flex',
        'flexDirection': 'row',
    },
    'sidebar': {
        'backgroundColor': '#1F1F1F',
        'padding': '20px',
        'width': '280px',
        'height': '100vh',
        'boxSizing': 'border-box',
        'borderRight': '1px solid #333',
    },
    'content': {
        'flex': '1',
        'padding': '20px',
        'overflowY': 'auto',
    },
    'header': {
        'textAlign': 'center',
        'marginBottom': '20px',
        'color': '#BB86FC',
    },
    'label': {
        'marginTop': '15px',
        'marginBottom': '5px',
        'fontWeight': 'bold',
        'color': '#CFD8DC',
    }
}

# Layout con sidebar y contenido principal
app.layout = html.Div(style=styles['body'], children=[
    # Sidebar con filtros
    html.Div(style=styles['sidebar'], children=[
        html.H2("Filtros", style={'color': '#BB86FC', 'textAlign': 'center'}),
        
        html.Label("Rango de Fechas", style=styles['label']),
        dcc.DatePickerRange(
            id='date-range',
            min_date_allowed=df['Date'].min(),
            max_date_allowed=df['Date'].max(),
            start_date=df['Date'].min(),
            end_date=df['Date'].max(),
            display_format='YYYY-MM-DD',
            style={'width': '100%'}
        ),

        html.Label("Categorías", style=styles['label']),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': cat, 'value': cat} for cat in df['Category'].unique()],
            value=df['Category'].unique().tolist(),
            multi=True,
            style={'color': '#000000'}
        ),

        html.Label("Tipo de gráfico (Ventas por Categoría)", style=styles['label']),
        dcc.RadioItems(
            id='chart-type',
            options=[
                {'label': 'Barra', 'value': 'bar'},
                {'label': 'Pastel', 'value': 'pie'}
            ],
            value='bar',
            labelStyle={'display': 'inline-block', 'marginRight': '15px', 'color': '#CFD8DC'}
        ),
    ]),

    # Contenido principal con gráficos
    html.Div(style=styles['content'], children=[
        html.H1("Dashboard de Ventas", style=styles['header']),

        dcc.Graph(id='sales-by-category'),

        dcc.Graph(id='sales-over-time')
    ])
])

# Callback para actualizar gráficos según filtros y tipo de gráfico
@app.callback(
    [Output('sales-by-category', 'figure'),
     Output('sales-over-time', 'figure')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('category-dropdown', 'value'),
     Input('chart-type', 'value')]
)
def update_graphs(start_date, end_date, selected_categories, chart_type):
    # Filtrar datos según selección
    filtered_df = df[
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date) &
        (df['Category'].isin(selected_categories))
    ]

    # Agrupar ventas por categoría
    sales_by_category = filtered_df.groupby('Category')['Sales'].sum().reset_index()

    # Crear gráfico según tipo seleccionado
    if chart_type == 'bar':
        fig_category = px.bar(
            sales_by_category,
            x='Category',
            y='Sales',
            title='Ventas por Categoría',
            labels={'Sales': 'Ventas Totales', 'Category': 'Categoría'},
            template='plotly_dark'
        )
    else:  # pie chart
        fig_category = px.pie(
            sales_by_category,
            names='Category',
            values='Sales',
            title='Ventas por Categoría',
            template='plotly_dark'
        )

    # Agrupar ventas por fecha
    sales_over_time = filtered_df.groupby('Date')['Sales'].sum().reset_index()

    # Gráfico de línea para ventas en el tiempo
    fig_time = px.line(
        sales_over_time,
        x='Date',
        y='Sales',
        title='Ventas a lo largo del tiempo',
        labels={'Sales': 'Ventas Totales', 'Date': 'Fecha'},
        template='plotly_dark'
    )

    # Ajustes de diseño para ambos gráficos
    fig_category.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font_color='#E0E0E0'
    )
    fig_time.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font_color='#E0E0E0'
    )

    return fig_category, fig_time

if __name__ == '__main__':
    app.run(debug=True)