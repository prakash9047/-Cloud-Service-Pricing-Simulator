import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import altair as alt
from typing import List, Dict, Optional, Union, Tuple

def plot_cost_comparison(comparison_df: pd.DataFrame, cost_column: str = 'On-Demand Cost') -> Optional[go.Figure]:
    """
    Create a bar chart comparing costs across providers.
    
    Args:
        comparison_df: DataFrame with comparison data
        cost_column: Column name with cost data to visualize
    
    Returns:
        Plotly figure object or None if DataFrame is empty
    """
    if comparison_df.empty:
        return None
    
    # Create identifiers combining provider and service
    comparison_df['Provider_Service'] = comparison_df['Provider'] + ' - ' + comparison_df['Service']
    
    fig = px.bar(
        comparison_df,
        x='Provider_Service',
        y=cost_column,
        color='Provider',
        labels={
            'Provider_Service': 'Provider - Service',
            cost_column: f'Cost ({comparison_df["Currency"].iloc[0]})'
        },
        title=f'Cloud Service {cost_column} Comparison',
        hover_data=['Region', 'Performance Score', 'Availability']
    )
    
    fig.update_layout(
        xaxis_title='Provider - Service',
        yaxis_title=f'Cost ({comparison_df["Currency"].iloc[0]})',
        legend_title='Provider',
        height=500
    )
    
    return fig

def plot_price_performance_ratio(performance_df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create a scatter plot showing price-to-performance ratio.
    
    Args:
        performance_df: DataFrame with performance metrics
    
    Returns:
        Plotly figure object or None if DataFrame is empty
    """
    if performance_df.empty or 'Performance Score' not in performance_df.columns:
        return None
    
    fig = px.scatter(
        performance_df,
        x='Performance Score',
        y='Cost',
        color='Provider',
        size='Price/Performance Ratio',
        hover_name='Service',
        text='Service',
        labels={
            'Performance Score': 'Performance Score (higher is better)',
            'Cost': f'Cost ({performance_df["Currency"].iloc[0]})',
            'Price/Performance Ratio': 'Price/Performance (lower is better)'
        },
        title='Price vs Performance Comparison'
    )
    
    # Add diagonal lines representing constant price/performance ratios
    max_perf = performance_df['Performance Score'].max() * 1.1
    max_cost = performance_df['Cost'].max() * 1.1
    
    ratio_lines = [0.1, 0.2, 0.3, 0.4, 0.5]
    for ratio in ratio_lines:
        fig.add_trace(
            go.Scatter(
                x=[0, max_perf],
                y=[0, max_perf * ratio],
                mode='lines',
                line=dict(color='gray', width=1, dash='dot'),
                name=f'Ratio = {ratio}',
                hoverinfo='none',
                showlegend=False
            )
        )
    
    fig.update_layout(
        height=600,
        xaxis_title='Performance Score (higher is better)',
        yaxis_title=f'Cost ({performance_df["Currency"].iloc[0]})'
    )
    
    # Add annotations for better ratio lines explanation
    fig.add_annotation(
        x=max_perf * 0.8,
        y=max_perf * 0.8 * 0.3,
        text="Better price/performance →",
        showarrow=True,
        arrowhead=3,
        ax=30,
        ay=-30
    )
    
    return fig

def plot_regional_pricing(df: pd.DataFrame, service_type: str) -> Optional[go.Figure]:
    """
    Create a choropleth map showing pricing by region.
    
    Args:
        df: DataFrame with pricing data
        service_type: Type of service to visualize
    
    Returns:
        Plotly figure object or None if insufficient data
    """
    # For now, simplify to a bar chart by region since we don't have precise geo coordinates
    filtered_df = df[df['Usage Type'] == service_type].copy()
    
    if filtered_df.empty:
        return None
    
    fig = px.bar(
        filtered_df,
        x='Region',
        y='Price Per Unit',
        color='Provider',
        barmode='group',
        labels={
            'Price Per Unit': f'Price Per {filtered_df["Units"].iloc[0]} ({filtered_df["Currency"].iloc[0]})',
            'Region': 'Region'
        },
        title=f'Regional Pricing Comparison for {service_type}'
    )
    
    fig.update_layout(
        xaxis_title='Region',
        yaxis_title=f'Price Per {filtered_df["Units"].iloc[0]} ({filtered_df["Currency"].iloc[0]})',
        legend_title='Provider'
    )
    
    return fig

def plot_reserved_savings(comparison_df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create a chart showing savings from reserved instances.
    
    Args:
        comparison_df: DataFrame with comparison data including reserved pricing
    
    Returns:
        Plotly figure object or None if DataFrame is empty
    """
    if comparison_df.empty or 'On-Demand Cost' not in comparison_df.columns:
        return None
    
    # Create a new DataFrame for visualization
    plot_data = []
    
    for _, row in comparison_df.iterrows():
        provider_service = f"{row['Provider']} - {row['Service']}"
        
        # Add on-demand data
        plot_data.append({
            'Provider_Service': provider_service,
            'Pricing Type': 'On-Demand',
            'Cost': row['On-Demand Cost'],
            'Provider': row['Provider'],
            'Currency': row['Currency']
        })
        
        # Add 1-year reserved data if available
        if '1-Year Reserved Cost' in row:
            plot_data.append({
                'Provider_Service': provider_service,
                'Pricing Type': '1-Year Reserved',
                'Cost': row['1-Year Reserved Cost'],
                'Provider': row['Provider'],
                'Currency': row['Currency']
            })
            
        # Add 3-year reserved data if available
        if '3-Year Reserved Cost' in row:
            plot_data.append({
                'Provider_Service': provider_service,
                'Pricing Type': '3-Year Reserved',
                'Cost': row['3-Year Reserved Cost'],
                'Provider': row['Provider'],
                'Currency': row['Currency']
            })
    
    plot_df = pd.DataFrame(plot_data)
    
    # Create the visualization
    fig = px.bar(
        plot_df,
        x='Provider_Service',
        y='Cost',
        color='Pricing Type',
        barmode='group',
        labels={
            'Provider_Service': 'Provider - Service',
            'Cost': f'Cost ({plot_df["Currency"].iloc[0]})',
            'Pricing Type': 'Pricing Type'
        },
        title='On-Demand vs Reserved Instance Pricing Comparison'
    )
    
    fig.update_layout(
        xaxis_title='Provider - Service',
        yaxis_title=f'Cost ({plot_df["Currency"].iloc[0]})',
        legend_title='Pricing Type'
    )
    
    return fig

def plot_cost_breakdown(costs_list: List[Dict[str, Union[str, float]]]) -> Optional[go.Figure]:
    """
    Create a pie chart showing cost breakdown.
    
    Args:
        costs_list: List of dictionaries with cost components
    
    Returns:
        Plotly figure object or None if insufficient data
    """
    if not costs_list:
        return None
    
    # Extract relevant data
    labels = [item['name'] for item in costs_list]
    values = [item['cost'] for item in costs_list]
    
    fig = px.pie(
        names=labels,
        values=values,
        title='Cost Breakdown',
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    
    return fig