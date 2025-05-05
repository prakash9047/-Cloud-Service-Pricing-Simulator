# Cloud Service Pricing Simulator

A comprehensive web application to model and compare cloud pricing scenarios across different providers, services, and regions.

## Features

- **Price Comparison**: Compare pricing across cloud providers (AWS, Azure, Google Cloud)
- **Performance Analysis**: Evaluate price-to-performance ratios for various cloud services
- **Regional Pricing**: Analyze how prices vary by geographic region
- **Cost Simulator**: Model costs for different cloud service combinations and usage patterns
- **Reserved Instance Analysis**: Compare on-demand vs. reserved instance pricing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cloud-service-pricing-simulator.git
cd cloud-service-pricing-simulator
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit application:
```bash
streamlit run src/app.py
```

## Project Structure

```
csm2/
├── data/
│   └── cloud_storage_pricing.csv      # Pricing data (sample data will be created if not found)
├── src/
│   ├── __init__.py                    # Python package indicator
│   ├── app.py                         # Main Streamlit application
│   ├── utils.py                       # Utility functions for pricing calculations
│   └── visualizations.py              # Data visualization functions
├── README.md                          # Project documentation
└── requirements.txt                   # Required Python packages
```

## Data Format

The application expects a CSV file with cloud pricing data in the following format:

| Provider | Service | Instance Type | Region | Usage Type | Price Per Unit | Units | Currency | Performance Score | Availability | Reserved Discount 1yr | Reserved Discount 3yr |
|----------|---------|--------------|--------|------------|----------------|-------|----------|-------------------|--------------|------------------------|------------------------|
| AWS      | S3      | -            | US East| Storage    | 0.023          | GB/Month | USD   | 85                | 99.99        | 20                     | 40                     |
| Azure    | Blob    | -            | EU West| Storage    | 0.020          | GB/Month | USD   | 80                | 99.95        | 25                     | 45                     |

If no data file is found, the application will generate sample data automatically.

## Usage

1. Use the sidebar filters to select providers, services, and regions of interest
2. Navigate between tabs to explore different analysis views:
   - **Price Comparison**: Compare base pricing across providers
   - **Performance Analysis**: Evaluate price-to-performance ratio
   - **Regional Pricing**: See how prices vary by region
   - **Cost Simulator**: Build complex scenarios with multiple services

## Extending the Data

To use your own pricing data, create a CSV file with the format shown above and place it in the `data` directory as `cloud_storage_pricing.csv`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.