import pandas as pd
import os
import numpy as np
from typing import Optional, Dict, List, Union, Tuple

def load_pricing_data(file_path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Load cloud service pricing data from a CSV file.
    
    Args:
        file_path: Path to the CSV file containing pricing data.
                  If None, uses default sample data.
    
    Returns:
        DataFrame containing the pricing data or None if file not found.
    """
    if file_path is None:
        # Check common locations
        possible_paths = [
            "data/cloud_storage_pricing.csv",
            "../data/cloud_storage_pricing.csv",
            "data/cloud_storage_pricing(1).csv",
            "../data/cloud_storage_pricing(1).csv",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/cloud_storage_pricing.csv"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        # If no file is found, create sample data
        if file_path is None or not os.path.exists(file_path):
            print("No pricing data file found. Creating sample data.")
            return create_sample_pricing_data()
    
    try:
        absolute_path = os.path.abspath(file_path)
        print(f"Loading pricing data from: {absolute_path}")
        df = pd.read_csv(absolute_path)
        return df
    except Exception as e:
        print(f"Error loading pricing data: {e}")
        print("Creating sample data instead.")
        return create_sample_pricing_data()

def create_sample_pricing_data() -> pd.DataFrame:
    """
    Create sample cloud pricing data.
    
    Returns:
        DataFrame with sample pricing data.
    """
    data = {
        'Provider': ['AWS', 'AWS', 'AWS', 'Azure', 'Azure', 'Azure', 'Google Cloud', 'Google Cloud', 'Google Cloud', 
                    'AWS', 'Azure', 'Google Cloud', 'AWS', 'Azure', 'Google Cloud'],
        'Service': ['S3 Standard', 'S3 Standard', 'S3 Standard', 'Blob Storage', 'Blob Storage', 'Blob Storage', 
                   'Cloud Storage', 'Cloud Storage', 'Cloud Storage', 'EC2', 'Virtual Machine', 'Compute Engine',
                   'RDS', 'SQL Database', 'Cloud SQL'],
        'Instance Type': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 
                         't2.micro', 'B1s', 'e2-micro', 'db.t3.micro', 'General Purpose', 'db-f1-micro'],
        'Region': ['US East', 'EU West', 'Asia Pacific', 'US East', 'EU West', 'Asia Pacific', 
                  'US East', 'EU West', 'Asia Pacific', 'US East', 'US East', 'US East', 'US East', 'US East', 'US East'],
        'Usage Type': ['Storage', 'Storage', 'Storage', 'Storage', 'Storage', 'Storage', 
                      'Storage', 'Storage', 'Storage', 'Compute', 'Compute', 'Compute', 'Database', 'Database', 'Database'],
        'Price Per Unit': [0.023, 0.024, 0.025, 0.018, 0.02, 0.022, 0.02, 0.021, 0.023, 
                          0.0116, 0.0104, 0.01, 0.017, 0.016, 0.015],
        'Units': ['GB/Month', 'GB/Month', 'GB/Month', 'GB/Month', 'GB/Month', 'GB/Month', 
                 'GB/Month', 'GB/Month', 'GB/Month', 'Hour', 'Hour', 'Hour', 'Hour', 'Hour', 'Hour'],
        'Currency': ['USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD'],
        'Performance Score': [85, 83, 80, 82, 80, 78, 87, 85, 83, 75, 78, 80, 88, 85, 86],
        'Availability': [99.99, 99.99, 99.95, 99.99, 99.95, 99.9, 99.99, 99.95, 99.9, 99.95, 99.95, 99.99, 99.99, 99.95, 99.95],
        'Reserved Discount 1yr': [20, 20, 20, 25, 25, 25, 15, 15, 15, 30, 33, 28, 25, 27, 20],
        'Reserved Discount 3yr': [40, 40, 40, 45, 45, 45, 35, 35, 35, 60, 62, 58, 50, 52, 45],
    }
    
    df = pd.DataFrame(data)
    
    # Save the sample data to a file for future use
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/cloud_storage_pricing.csv', index=False)
    print("Sample data created and saved to data/cloud_storage_pricing.csv")
    
    return df

def calculate_cost(
    usage: float, 
    price_per_unit: float, 
    time_period: str = 'month', 
    reserved_instance: str = 'on-demand'
) -> float:
    """
    Calculate the total cost for a given usage and price.
    
    Args:
        usage: Amount of usage in the specified units
        price_per_unit: Price per unit of resource
        time_period: Time period for calculation ('day', 'month', or 'year')
        reserved_instance: Type of instance pricing ('on-demand', '1yr', or '3yr')
    
    Returns:
        Total calculated cost
    """
    # Base calculation
    cost = float(usage) * float(price_per_unit)
    
    # Adjust for time period
    if time_period == 'day':
        cost = cost / 30  # Approximate daily cost
    elif time_period == 'year':
        cost = cost * 12  # Annual cost
    
    return cost

def apply_reserved_discount(
    cost: float, 
    discount_percentage: float
) -> float:
    """
    Apply reserved instance discount to cost.
    
    Args:
        cost: Original cost
        discount_percentage: Percentage discount to apply
    
    Returns:
        Discounted cost
    """
    return cost * (1 - discount_percentage / 100)

def calculate_total_cost(
    pricing_row: pd.Series,
    usage: float,
    time_period: str = 'month',
    reserved_instance: str = 'on-demand'
) -> Dict[str, Union[float, str]]:
    """
    Calculate total cost with all applicable factors.
    
    Args:
        pricing_row: Row from pricing dataframe
        usage: Amount of usage
        time_period: Time period for calculation
        reserved_instance: Type of instance pricing
    
    Returns:
        Dictionary with cost details
    """
    base_cost = calculate_cost(usage, pricing_row['Price Per Unit'], time_period)
    
    # Apply reserved instance discount if applicable
    final_cost = base_cost
    discount = 0
    
    if reserved_instance == '1yr' and 'Reserved Discount 1yr' in pricing_row:
        discount = pricing_row['Reserved Discount 1yr']
        final_cost = apply_reserved_discount(base_cost, discount)
    elif reserved_instance == '3yr' and 'Reserved Discount 3yr' in pricing_row:
        discount = pricing_row['Reserved Discount 3yr']
        final_cost = apply_reserved_discount(base_cost, discount)
    
    return {
        'base_cost': base_cost,
        'discount_percentage': discount,
        'final_cost': final_cost,
        'currency': pricing_row['Currency'],
        'time_period': time_period
    }

def filter_pricing_data(
    df: pd.DataFrame,
    provider: Optional[str] = None,
    service: Optional[str] = None,
    instance_type: Optional[str] = None,
    region: Optional[str] = None,
    usage_type: Optional[str] = None
) -> pd.DataFrame:
    """
    Filter pricing data based on user selections.
    
    Args:
        df: DataFrame with pricing data
        provider: Cloud provider name
        service: Service name
        instance_type: Type of instance
        region: Geographic region
        usage_type: Type of usage (storage, compute, etc.)
    
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    if provider and provider != "All":
        filtered_df = filtered_df[filtered_df['Provider'] == provider]
    if service and service != "All":
        filtered_df = filtered_df[filtered_df['Service'] == service]
    if instance_type and instance_type != "All":
        filtered_df = filtered_df[filtered_df['Instance Type'] == instance_type]
    if region and region != "All":
        filtered_df = filtered_df[filtered_df['Region'] == region]
    if usage_type and usage_type != "All":
        filtered_df = filtered_df[filtered_df['Usage Type'] == usage_type]
        
    return filtered_df

def compare_providers(
    df: pd.DataFrame,
    service_type: str,
    usage_amount: float,
    region: Optional[str] = None
) -> pd.DataFrame:
    """
    Compare pricing across providers for a specific service type.
    
    Args:
        df: DataFrame with pricing data
        service_type: Type of service to compare
        usage_amount: Amount of usage for calculation
        region: Optional region filter
    
    Returns:
        DataFrame with comparison results
    """
    # Filter by service type and region if specified
    filtered_df = df[df['Usage Type'] == service_type]
    if region and region != "All":
        filtered_df = filtered_df[filtered_df['Region'] == region]
    
    if filtered_df.empty:
        return pd.DataFrame()
    
    # Calculate costs for each service
    results = []
    for idx, row in filtered_df.iterrows():
        on_demand_cost = calculate_cost(usage_amount, row['Price Per Unit'])
        
        reserved_1yr_cost = on_demand_cost
        if 'Reserved Discount 1yr' in row:
            reserved_1yr_cost = apply_reserved_discount(on_demand_cost, row['Reserved Discount 1yr'])
            
        reserved_3yr_cost = on_demand_cost
        if 'Reserved Discount 3yr' in row:
            reserved_3yr_cost = apply_reserved_discount(on_demand_cost, row['Reserved Discount 3yr'])
        
        results.append({
            'Provider': row['Provider'],
            'Service': row['Service'],
            'Region': row['Region'],
            'On-Demand Cost': on_demand_cost,
            '1-Year Reserved Cost': reserved_1yr_cost,
            '3-Year Reserved Cost': reserved_3yr_cost,
            'Currency': row['Currency'],
            'Performance Score': row['Performance Score'] if 'Performance Score' in row else None,
            'Availability': row['Availability'] if 'Availability' in row else None
        })
    
    return pd.DataFrame(results)

def get_performance_ratio(df: pd.DataFrame, usage_amount: float) -> pd.DataFrame:
    """
    Calculate price-to-performance ratio for services.
    
    Args:
        df: DataFrame with pricing data
        usage_amount: Amount of usage for calculation
    
    Returns:
        DataFrame with price-to-performance metrics
    """
    if 'Performance Score' not in df.columns:
        return pd.DataFrame()
    
    results = []
    for idx, row in df.iterrows():
        cost = calculate_cost(usage_amount, row['Price Per Unit'])
        
        # Calculate price-to-performance ratio (lower is better)
        if row['Performance Score'] > 0:
            performance_ratio = cost / row['Performance Score']
        else:
            performance_ratio = float('inf')
            
        results.append({
            'Provider': row['Provider'],
            'Service': row['Service'],
            'Region': row['Region'],
            'Cost': cost,
            'Performance Score': row['Performance Score'],
            'Price/Performance Ratio': performance_ratio,
            'Currency': row['Currency']
        })
    
    return pd.DataFrame(results).sort_values('Price/Performance Ratio')