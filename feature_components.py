import plotly.express as px
import plotly.graph_objects as go

# Render feature line plot
def render_feature_plot(plot_title, feature_data, feature_name, feature_description, y_min_value, y_max_value, overtopping_times_df):
    feature_fig = go.Figure()
    feature_fig.add_trace(go.Scatter(x=feature_data['time'], y=feature_data[feature_name], mode='lines', name=feature_description, line_color='#478DB4'))

    feature_fig.add_trace(go.Scatter(
        x=overtopping_times_df['time'],
        y=overtopping_times_df[feature_name],
        mode='markers',
        marker=dict(size=8),
        name='Overtopping event'
    ))

    feature_fig.update_layout(
        title=dict(
            text=plot_title,  # Just the text title
            font=dict(
                family='Helvetica Neue',
                size=22,
                color='#3279B7',
                weight=500
            ),
        ),
        plot_bgcolor='white',  # Set the plot background color to white
        xaxis=dict(
            showgrid=True,  # Show x-axis gridlines
            gridcolor='#8A8D90',  # Set x-axis gridline color to light gray
            linecolor='#8A8D90',  # Set x-axis line color to gray
            title=dict(text='')
        ),
        yaxis=dict(
            range=[y_min_value, y_max_value],
            showgrid=True,  # Show y-axis gridlines
            gridcolor='#8A8D90',  # Set y-axis gridline color to light gray
            linecolor='#8A8D90',  # Set y-axis line color to gray
            title=dict(text='')
        ),
        showlegend=True,
    )

    return feature_fig