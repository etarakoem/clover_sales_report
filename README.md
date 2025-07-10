# Clover API Batch/Closeout Information Retrieval Script

This Python script retrieves batch/closeout information from Clover's API and generates CSV reports for monthly sales data.

## Features

- Retrieve batch/closeout data from Clover API by month
- Generate CSV reports with proper formatting (2 decimal places for currency)
- Support for single month or multiple months reporting
- For multiple months: generates both individual monthly reports AND a combined report
- Includes business header: "Belle Nails and Spa" and month information
- Automatic totals calculation at the end of each report

## Requirements

- Python 3.7+
- Clover API access token and merchant ID
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/etarakoem/clover_sales_report.git
cd PythonDev
```

2. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Configure your Clover API credentials:

```bash
cp config_template.py config.py
```

Then edit `config.py` with your actual Clover API credentials.

## Configuration

### Option 1: Configuration File (Recommended)

1. Copy `config_template.py` to `config.py`
2. Edit `config.py` and replace the placeholder values with your actual:
   - `CLOVER_ACCESS_TOKEN`: Your Clover API access token
   - `CLOVER_MERCHANT_ID`: Your merchant ID
   - `CLOVER_BASE_URL`: API base URL (production or sandbox)

### Option 2: Environment Variables

Set the following environment variables:

```bash
export CLOVER_ACCESS_TOKEN="your_access_token_here"
export CLOVER_MERCHANT_ID="your_merchant_id_here"
export CLOVER_BASE_URL="https://api.clover.com"
```

### Option 3: Command Line Arguments

Pass credentials directly via command line (not recommended for production):

```bash
python clover.py --token "your_token" --merchant "your_merchant_id"
```

## Usage

### Basic Usage (Previous Month)

```bash
python clover.py
```

Generates a CSV report for the previous month.

### Specific Month

```bash
python clover.py --year 2025 --month 6
```

Generates a CSV report for June 2025.

### Multiple Months

```bash
python clover.py --year 2025 --month "5,6,7"
```

Generates:

- Individual CSV reports: `clover_monthly_data_2025_05.csv`, `clover_monthly_data_2025_06.csv`, `clover_monthly_data_2025_07.csv`
- Combined CSV report: `clover_combined_months_2025_05_2025_06_2025_07.csv`

### Custom Output File

```bash
python clover.py --output "my_custom_report.csv"
```

### Using Environment Variables

```bash
python clover.py --env
```

## CSV Output Format

Each CSV file includes:

1. **Header Lines:**

   ```
   Belle Nails and Spa
   Sales for the month of [Month Year] (or "months of [Month1 Year1, Month2 Year2]" for combined reports)
   ```
2. **Data Columns:**

   - `date`: Transaction date (YYYY-MM-DD)
   - `debit`: Debit amount (sales minus tips, formatted to 2 decimal places)
   - `tip`: Tips amount (formatted to 2 decimal places)
   - `total`: Total sales amount (formatted to 2 decimal places)
3. **Totals Row:**

   - For single month: `TOTAL` row with sum of all amounts
   - For combined reports: `GRAND TOTAL` row with sum across all months

### Example CSV Output:

```csv
Belle Nails and Spa
Sales for the month of June 2025
date,debit,tip,total
2025-06-01,0.00,0.00,0.00
2025-06-02,128.50,19.28,147.78
2025-06-03,0.00,0.00,0.00
...
TOTAL,2547.89,382.18,2930.07
```

## Command Line Options

- `--year YEAR`: Year (default: current year or previous month's year)
- `--month MONTH`: Month 1-12 or comma-separated months like "1,2,3" (default: previous month)
- `--token TOKEN`: Clover API access token
- `--merchant MERCHANT`: Clover merchant ID
- `--output OUTPUT`: Output CSV file path (optional)
- `--env`: Load credentials from environment variables
- `--help`: Show help message

## Files

- `clover.py`: Main script
- `config_template.py`: Template for API credentials (copy to config.py)
- `requirements.txt`: Python package dependencies
- `test_example.py`: Example showing CSV output format

## Security Notes

- Never commit `config.py` with real credentials to version control
- The `config.py` file is already in `.gitignore`
- Use environment variables or secure credential management in production
- Keep your Clover API tokens secure and rotate them regularly

## Troubleshooting

### Common Issues

1. **Missing credentials error:**

   - Ensure you've created `config.py` from `config_template.py`
   - Verify your API credentials are correct
2. **API request failed:**

   - Check your internet connection
   - Verify your API token has proper permissions
   - Ensure the merchant ID is correct
3. **No data returned:**

   - Verify transactions exist for the specified month
   - Check if the date range is correct
   - Ensure your API token has access to batch data

## API Reference

This script uses the Clover REST API:

- Endpoint: `/v3/merchants/{merchantId}/batches`
- Documentation: [Clover API Documentation](https://docs.clover.com/reference)

## License

This project is provided as-is for business use. Please ensure compliance with Clover's API terms of service.
