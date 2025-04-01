import plotly.graph_objects as go


def render_feature_scatter_plot(
    feature_fig, feature_data, feature_name, trace_name, trace_color, is_forecast_data
):
    """Render feature scatter plot

    Args:
        feature_fig (Figure): Feature's figure
        feature_data (Dataframe): Feature's data
        feature_name (string): Feature column's name
        trace_name (string): Feature's name to display it on legend
        trace_color (string): Trace's colour
        is_forecast_data (bool): Flag to identify if data is forecast or adjusted forecast
    """

    if is_forecast_data:
        line_size = {"width": 2}
    else:
        line_size = {"width": 1}

    feature_fig.add_trace(
        go.Scatter(
            x=feature_data["time"],
            y=feature_data[feature_name],
            mode="lines",
            name=trace_name,
            line_color=trace_color,
            line=line_size,
        )
    )


def render_overtopping_events_plot(
    feature_fig, cur_overtopping_times_df, feature_name, trace_name, trace_color
):
    """Render overtopping events plot

    Args:
        feature_fig (Figure): Feature's figure
        cur_overtopping_times_df (Dataframe): Adjusted forecast overtopping events times dataframe
        feature_name (string): Feature column's name
        trace_name (string): Feature's name to display it on legend
        trace_color (string): Trace's colour
    """

    feature_fig.add_trace(
        go.Scatter(
            x=cur_overtopping_times_df["time"],
            y=cur_overtopping_times_df[feature_name],
            mode="markers",
            marker=dict(size=12),
            name=trace_name,
            line=dict(color=trace_color, width=4),
        )
    )


def render_feature_plot(
    plot_title,
    prev_feature_data,
    cur_feature_data,
    feature_name,
    features_description,
    overtopping_evts_desc,
    y_min_value,
    y_max_value,
    prev_overtopping_times_df,
    cur_overtopping_times_df,
    show_dynamic_y_axis,
):
    """Render feature line plot

    Args:
        plot_title (string): Plot's title
        prev_feature_data (Dataframe): Feature data
        cur_feature_data (Dataframe): Adjusted feature data
        feature_name (string): Feature's name
        features_description (tuple): Original feature and adjusted feature data descriptions
        overtopping_evts_desc (string): Forecast overtopping events and adjusted forecast overtopping events data descriptions
        y_min_value (integer): Minimum value of y-axis
        y_max_value (integer): Maximum value of y-axis
        prev_overtopping_times_df (Dataframe): Forecast overtopping events dataframe
        cur_overtopping_times_df (Dataframe): Adjusted forecast overtopping events dataframe
        show_dynamic_y_axis (bool): Flag to display y-axis dynamically

    Returns:
        Figure: Feature's line plot and scatter plot
    """

    feature_fig = go.Figure()

    forecast_feature_desc, adjusted_feature_desc = features_description
    forecast_overtopping_evt_desc, adjusted_overtopping_evt_desc = overtopping_evts_desc

    if not prev_feature_data.empty:
        is_forecast_data = False
        forecast_marker_color = "#808080"
        render_feature_scatter_plot(
            feature_fig,
            prev_feature_data,
            feature_name,
            forecast_feature_desc,
            "#000",
            True,
        )
    else:
        is_forecast_data = True
        forecast_marker_color = "#000"
        adjusted_feature_desc = forecast_feature_desc
        adjusted_overtopping_evt_desc = forecast_overtopping_evt_desc

    if not prev_overtopping_times_df.empty:
        render_overtopping_events_plot(
            feature_fig,
            prev_overtopping_times_df,
            feature_name,
            forecast_overtopping_evt_desc,
            "#000",
        )

    render_feature_scatter_plot(
        feature_fig,
        cur_feature_data,
        feature_name,
        adjusted_feature_desc,
        forecast_marker_color,
        is_forecast_data,
    )
    render_overtopping_events_plot(
        feature_fig,
        cur_overtopping_times_df,
        feature_name,
        adjusted_overtopping_evt_desc,
        forecast_marker_color,
    )

    if show_dynamic_y_axis:
        y_axis_dict = dict(
            showgrid=True,
            gridcolor="#8A8D90",
            linecolor="#8A8D90",
            title=dict(text=""),
        )
    else:
        y_axis_dict = dict(
            range=[y_min_value, y_max_value],
            showgrid=True,
            gridcolor="#8A8D90",
            linecolor="#8A8D90",
            title=dict(text=""),
        )

    feature_fig.update_layout(
        title=dict(
            text=plot_title,
            font=dict(family="Helvetica Neue", size=22, color="#3279B7", weight=500),
        ),
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=True,
            gridcolor="#8A8D90",
            linecolor="#8A8D90",
            title=dict(text=""),
        ),
        yaxis=y_axis_dict,
        showlegend=True,
    )

    return feature_fig
