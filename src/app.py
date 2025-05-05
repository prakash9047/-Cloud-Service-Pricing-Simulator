import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from typing import Optional, Dict, List, Union, Tuple

# Ensure the parent directory is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import utility functions
from src.utils import (
    load_pricing_data, 
    calculate_cost, 
    calculate_total_cost,
    filter_pricing_data, 
    compare_providers,
    get_performance_ratio,
    apply_reserved_discount
)

# Import visualization functions
from src.visualizations import (
    plot_cost_comparison,
    plot_price_performance_ratio,
    plot_regional_pricing,
    plot_reserved_savings,
    plot_cost_breakdown
)

# Page configuration
st.set_page_config(
    page_title="Cloud Service Pricing Simulator",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4285F4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #5F6368;
        margin-bottom: 1rem;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 5px;
        padding: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #5F6368;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<div class="main-header">Cloud Service Pricing Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Model cloud pricing scenarios based on your specific needs</div>', unsafe_allow_html=True)

st.markdown("""
This simulator helps organizations compare and model cloud pricing across different providers, services, and regions.
Evaluate cost structures, compare performance metrics, and find the most cost-effective solution for your workloads.
""")

# Create tabs for different features
tab1, tab2, tab3, tab4 = st.tabs(["Price Comparison", "Performance Analysis", "Regional Pricing", "Cost Simulator"])

# Load pricing data
pricing_df = load_pricing_data()

if pricing_df is not None:
    # Sidebar filters that apply across all tabs
    st.sidebar.markdown('<div class="sidebar-header">Filter Options</div>', unsafe_allow_html=True)
    
    providers = ["All"] + sorted(pricing_df['Provider'].unique().tolist())
    services = ["All"] + sorted(pricing_df['Usage Type'].unique().tolist())
    regions = ["All"] + sorted(pricing_df['Region'].unique().tolist())
    
    selected_provider = st.sidebar.selectbox("Cloud Provider", providers)
    selected_service_type = st.sidebar.selectbox("Service Type", services)
    selected_region = st.sidebar.selectbox("Region", regions)
    
    # Apply filters
    filtered_df = pricing_df.copy()
    filtered_df = filter_pricing_data(
        filtered_df, 
        provider=selected_provider, 
        usage_type=selected_service_type, 
        region=selected_region
    )
    
    # Tab 1: Price Comparison
    with tab1:
        st.header("Price Comparison")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.subheader("Usage Parameters")
            usage_amount = st.number_input(
                "Usage Amount", 
                min_value=0.1, 
                value=100.0, 
                step=10.0,
                help="Amount of resources to use in the calculation"
            )
            
            # Determine the unit based on selected service
            if selected_service_type != "All" and not filtered_df.empty:
                service_unit = filtered_df[filtered_df['Usage Type'] == selected_service_type]['Units'].iloc[0]
                st.write(f"Unit: {service_unit}")
            
            include_reserved = st.checkbox("Include Reserved Instance Pricing", value=True)
            
        with col1:
            if not filtered_df.empty:
                # Generate comparison data
                comparison_df = compare_providers(
                    filtered_df,
                    selected_service_type if selected_service_type != "All" else filtered_df['Usage Type'].iloc[0],
                    usage_amount,
                    selected_region if selected_region != "All" else None
                )
                
                if not comparison_df.empty:
                    # Visualization
                    cost_fig = plot_cost_comparison(comparison_df)
                    if cost_fig:
                        st.plotly_chart(cost_fig, use_container_width=True)
                    
                    # If reserved pricing should be included
                    if include_reserved:
                        reserved_fig = plot_reserved_savings(comparison_df)
                        if reserved_fig:
                            st.plotly_chart(reserved_fig, use_container_width=True)
                    
                    # Raw data in a table
                    st.subheader("Detailed Pricing Data")
                    st.dataframe(comparison_df.style.highlight_min(subset=['On-Demand Cost'], color='lightgreen'))
                else:
                    st.info("No matching services found with the current filters. Please adjust your selections.")
            else:
                st.info("Please select a service type and region to compare prices.")
    
    # Tab 2: Performance Analysis
    with tab2:
        st.header("Performance Analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.subheader("Performance Parameters")
            perf_usage_amount = st.number_input(
                "Usage Amount for Calculation", 
                min_value=0.1, 
                value=100.0, 
                step=10.0,
                key="perf_usage"
            )
            
            if 'Performance Score' in filtered_df.columns:
                st.info("Performance score is on a scale of 0-100, with 100 being the best performance.")
            else:
                st.warning("Performance data is not available in the current dataset.")
            
        with col1:
            if 'Performance Score' in filtered_df.columns and not filtered_df.empty:
                # Get performance metrics
                performance_df = get_performance_ratio(filtered_df, perf_usage_amount)
                
                if not performance_df.empty:
                    # Create performance visualization
                    perf_fig = plot_price_performance_ratio(performance_df)
                    if perf_fig:
                        st.plotly_chart(perf_fig, use_container_width=True)
                    
                    # Display performance data table
                    st.subheader("Price-Performance Details")
                    st.dataframe(performance_df.sort_values('Price/Performance Ratio').style.highlight_min(subset=['Price/Performance Ratio'], color='lightgreen'))
                else:
                    st.info("No performance data available with the current filters.")
            else:
                st.info("Performance data is not available in the current dataset or no services match your filters.")
    
    # Tab 3: Regional Pricing
    with tab3:
        st.header("Regional Pricing Analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.subheader("Regional Filter")
            regional_service = st.selectbox(
                "Service Type for Regional Analysis",
                options=["All"] + sorted(pricing_df['Usage Type'].unique().tolist()),
                key="regional_service"
            )
            
            st.info("Compare how pricing varies across different geographic regions.")
            
        with col1:
            if regional_service != "All" and not pricing_df.empty:
                # Create regional visualization
                region_fig = plot_regional_pricing(pricing_df, regional_service)
                if region_fig:
                    st.plotly_chart(region_fig, use_container_width=True)
                    
                    # Filter data for this specific service type
                    regional_data = pricing_df[pricing_df['Usage Type'] == regional_service].copy()
                    regional_data = regional_data.sort_values(['Provider', 'Region'])
                    
                    # Display regional data table
                    st.subheader("Regional Pricing Details")
                    st.dataframe(regional_data[['Provider', 'Service', 'Region', 'Price Per Unit', 'Units', 'Currency']])
                    
                    # Show percentage difference from cheapest region
                    st.subheader("Regional Price Variance")
                    
                    for provider in regional_data['Provider'].unique():
                        provider_data = regional_data[regional_data['Provider'] == provider].copy()
                        if not provider_data.empty:
                            min_price = provider_data['Price Per Unit'].min()
                            provider_data['% Above Lowest'] = ((provider_data['Price Per Unit'] - min_price) / min_price * 100).round(2)
                            
                            st.write(f"**{provider}** price variance:")
                            st.dataframe(provider_data[['Region', 'Price Per Unit', '% Above Lowest']].sort_values('Price Per Unit'))
                else:
                    st.info("Insufficient regional pricing data for the selected service type.")
            else:
                st.info("Please select a specific service type to analyze regional pricing differences.")
    
    # Tab 4: Cost Simulator
    with tab4:
        st.header("Cost Simulator")
        
        st.write("Simulate costs for different scenarios and workloads.")
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.subheader("Simulator Settings")
            
            # Service selection
            selected_services = st.multiselect(
                "Select Services to Include",
                options=pricing_df['Service'].unique().tolist(),
                default=pricing_df['Service'].unique().tolist()[0:2] if len(pricing_df['Service'].unique()) > 1 else pricing_df['Service'].unique().tolist()
            )
            
            # Time period selection
            time_period = st.selectbox(
                "Billing Period",
                options=["month", "day", "year"],
                index=0
            )
            
            # Reserved instance option
            reservation_type = st.selectbox(
                "Pricing Model",
                options=["on-demand", "1yr", "3yr"],
                index=0
            )
            
        with col1:
            if selected_services:
                st.subheader("Usage Configuration")
                
                # Create usage inputs for each selected service
                usage_values = {}
                for service in selected_services:
                    service_rows = pricing_df[pricing_df['Service'] == service]
                    
                    if not service_rows.empty:
                        service_unit = service_rows['Units'].iloc[0]
                        default_value = 100.0 if 'GB' in service_unit else 730.0 if 'Hour' in service_unit else 10.0
                        
                        usage_values[service] = st.number_input(
                            f"{service} ({service_unit})",
                            min_value=0.0,
                            value=default_value,
                            step=10.0,
                            key=f"usage_{service}"
                        )
                
                # Calculate button
                if st.button("Calculate Total Cost", key="calc_total"):
                    # Calculate costs for each selected service
                    service_costs = []
                    total_cost = 0.0
                    currency = ""
                    
                    for service in selected_services:
                        service_rows = filtered_df[filtered_df['Service'] == service]
                        
                        if not service_rows.empty:
                            # Find the lowest cost option for this service
                            min_cost_row = None
                            min_cost = float('inf')
                            
                            for _, row in service_rows.iterrows():
                                cost_info = calculate_total_cost(
                                    row, 
                                    usage_values[service], 
                                    time_period, 
                                    reservation_type
                                )
                                
                                if cost_info['final_cost'] < min_cost:
                                    min_cost = cost_info['final_cost']
                                    min_cost_row = row
                                    currency = cost_info['currency']
                            
                            if min_cost_row is not None:
                                cost_info = calculate_total_cost(
                                    min_cost_row, 
                                    usage_values[service], 
                                    time_period, 
                                    reservation_type
                                )
                                
                                service_costs.append({
                                    'name': f"{min_cost_row['Provider']} {service}",
                                    'cost': cost_info['final_cost'],
                                    'currency': cost_info['currency']
                                })
                                
                                total_cost += cost_info['final_cost']
                    
                    # Display results
                    if service_costs:
                        st.subheader("Estimated Costs")
                        
                        # Total cost metrics
                        st.metric(
                            label=f"Total Estimated Cost ({currency}/{time_period})",
                            value=f"{currency} {total_cost:.2f}"
                        )
                        
                        # Cost breakdown
                        cost_breakdown_cols = st.columns(len(service_costs))
                        for i, cost_item in enumerate(service_costs):
                            with cost_breakdown_cols[i]:
                                st.metric(
                                    label=cost_item['name'],
                                    value=f"{cost_item['currency']} {cost_item['cost']:.2f}"
                                )
                        
                        # Cost breakdown chart
                        breakdown_fig = plot_cost_breakdown(service_costs)
                        if breakdown_fig:
                            st.plotly_chart(breakdown_fig, use_container_width=True)
                        
                        # Cost optimization suggestions
                        st.subheader("Cost Optimization Suggestions")
                        
                        # Generate some suggestions based on the data
                        suggestions = []
                        
                        # Check if reserved instances would save money
                        if reservation_type == "on-demand":
                            suggestions.append("Consider using reserved instances for significant savings on predictable workloads.")
                        
                        # Check for cheaper regions
                        if selected_region != "All":
                            suggestions.append("Evaluate using different regions, as pricing can vary significantly by location.")
                        
                        # Check for alternative providers
                        if selected_provider != "All":
                            suggestions.append("Compare pricing across multiple cloud providers to find the best value.")
                        
                        # Display suggestions
                        for i, suggestion in enumerate(suggestions):
                            st.write(f"{i+1}. {suggestion}")
                    else:
                        st.warning("Could not calculate costs with the current selections.")
            else:
                st.info("Please select at least one service to simulate costs.")

# Display the raw data
with st.expander("View Raw Pricing Data"):
    if pricing_df is not None:
        st.dataframe(pricing_df)
    else:
        st.error("Failed to load pricing data.")

# Add a footer
st.markdown("""
<div class="footer">
    <p>Cloud Service Pricing Simulator | Data is for demonstration purposes only</p>
</div>
""", unsafe_allow_html=True)