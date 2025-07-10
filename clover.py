#!/usr/bin/env python3
"""
Clover API Batch/Closeout Information Retrieval Script

This script retrieves batch/closeout information from Clover's API based on month.
Uses the /v3/merchants/{merchantId}/batches endpoint to get data that corresponds
to the closeout information shown in the Clover web dashboard.
Requires Clover API credentials and proper authentication.
"""

import requests
import json
import os
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Optional
import argparse
import csv


class CloverAPI:
    """Class to handle Clover API interactions for batch/closeout data."""
    
    def __init__(self, access_token: str, merchant_id: str, base_url: str = "https://api.clover.com"):
        """
        Initialize Clover API client.
        
        Args:
            access_token: Clover API access token
            merchant_id: Merchant ID from Clover
            base_url: Base URL for Clover API (default: production)
        """
        self.access_token = access_token
        self.merchant_id = merchant_id
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make authenticated request to Clover API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response from API
        """
        url = f"{self.base_url}/v3/merchants/{self.merchant_id}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise
    
    def get_closeouts_by_month(self, year: int, month: int) -> List[Dict]:
        """
        Retrieve batch/closeout information for a specific month.
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            
        Returns:
            List of batch records
        """
        # Calculate start and end timestamps for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Convert to Unix timestamps (milliseconds)
        
        print(f"Fetching batches/closeouts for {calendar.month_name[month]} {year}...")
        print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        try:
            # Fetch all batches first
            response = self._make_request('/batches?limit=901')
            all_batches = response.get('elements', [])
            
            # Filter batches by the specified month using createdTime
            filtered_batches = []
            for batch in all_batches:
                batch_timestamp = batch.get('createdTime', 0)
                if batch_timestamp:
                    batch_date = datetime.fromtimestamp(batch_timestamp / 1000)
                    if batch_date.year == year and batch_date.month == month:
                        filtered_batches.append(batch)
            
            return filtered_batches
        except Exception as e:
            print(f"Error fetching batches: {e}")
            return []
    
    def get_batch_details(self, batch_id: str) -> Dict:
        """
        Get detailed information for a specific batch.
        
        Args:
            batch_id: ID of the batch
            
        Returns:
            Detailed batch information
        """
        try:
            return self._make_request(f'/batches/{batch_id}')
        except Exception as e:
            print(f"Error fetching batch details for {batch_id}: {e}")
            return {}
    
    def view_single_batch(self, batch_id: str) -> str:
        """
        Get and format detailed information for a single batch by ID.
        
        Args:
            batch_id: ID of the batch to view
            
        Returns:
            Formatted batch details string
        """
        print(f"Fetching batch details for ID: {batch_id}...")
        
        try:
            batch = self._make_request(f'/batches/{batch_id}')
            
            if not batch:
                return f"No batch found with ID: {batch_id}"
            
            batch_data = self._format_single_batch(batch)
            return f"Date: {batch_data['date']}, Debit: ${batch_data['debit']:.2f}, Tips: ${batch_data['tip']:.2f}, Total: ${batch_data['total']:.2f}"
            
        except Exception as e:
            return f"Error fetching batch {batch_id}: {e}"
    
    def _format_single_batch(self, batch: Dict) -> Dict:
        """
        Format a single batch record for CSV data.
        
        Args:
            batch: Single batch record
            
        Returns:
            Dict with date, debit, tip, and total amounts
        """
        created_time = batch.get('createdTime', 0)
        
        # Format created time
        if created_time:
            created_date = datetime.fromtimestamp(created_time / 1000).strftime('%Y-%m-%d')
        else:
            created_date = "Unknown"
        
        # Initialize default values
        sales_amount = 0.0
        tip_amount = 0.0
        debit = 0.0
        
        # Extract batch information
        if 'batchDetails' in batch and batch['batchDetails']:
            details = batch['batchDetails']
            batch_totals = details.get('batchTotals', {})
            
            if batch_totals:
                # Sales
                sales = batch_totals.get('sales', {})
                if sales:
                    sales_amount = sales.get('total', 0) / 100
                
                # Tips
                tips = batch_totals.get('tips', {})
                if tips and tips.get('count', 0) > 0:
                    tip_amount = tips.get('total', 0) / 100

                debit = sales_amount - tip_amount
                
        return {
            'date': created_date,
            'debit': debit,
            'tip': tip_amount,
            'total': sales_amount
        }
    
    def generate_monthly_csv_data(self, year: int, month: int) -> List[Dict]:
        """
        Generate CSV data for all dates in a month.
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            
        Returns:
            List of dictionaries with date, debit, tip, total for each day
        """
        # Get all batches for the month
        batches = self.get_closeouts_by_month(year, month)
        
        # Group batches by date
        daily_data = {}
        for batch in batches:
            batch_info = self._format_single_batch(batch)
            date = batch_info['date']
            
            if date not in daily_data:
                daily_data[date] = {
                    'date': date,
                    'debit': 0.0,
                    'tip': 0.0,
                    'total': 0.0
                }
            
            # Sum up amounts for the same date
            daily_data[date]['debit'] += batch_info['debit']
            daily_data[date]['tip'] += batch_info['tip']
            daily_data[date]['total'] += batch_info['total']
        
        # Get all dates in the month (including days with no data)
        num_days = calendar.monthrange(year, month)[1]
        all_dates_data = []
        
        for day in range(1, num_days + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            if date_str in daily_data:
                all_dates_data.append(daily_data[date_str])
            else:
                # Add zero values for dates with no transactions
                all_dates_data.append({
                    'date': date_str,
                    'debit': 0.0,
                    'tip': 0.0,
                    'total': 0.0
                })
        
        return all_dates_data
    
    def export_monthly_csv(self, year: int, month: int, filename: str = None) -> str:
        """
        Export monthly data to CSV file with header.
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            filename: Output filename (optional)
            
        Returns:
            Path to created CSV file
        """
        if filename is None:
            filename = f"clover_monthly_data_{year}_{month:02d}.csv"
        
        # Get the data
        monthly_data = self.generate_monthly_csv_data(year, month)
        
        # Calculate totals
        total_debit = sum(row['debit'] for row in monthly_data)
        total_tips = sum(row['tip'] for row in monthly_data)
        total_sales = sum(row['total'] for row in monthly_data)
        
        # Write CSV file with header
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Write header lines
            csvfile.write("Belle Nails and Spa\n")
            csvfile.write(f"Sales for the month of {calendar.month_name[month]} {year}\n")
            
            # Write CSV data
            writer = csv.writer(csvfile)
            writer.writerow(['date', 'debit', 'tip', 'total'])
            
            for row in monthly_data:
                writer.writerow([
                    row['date'],
                    f"{row['debit']:.2f}",
                    f"{row['tip']:.2f}",
                    f"{row['total']:.2f}"
                ])
            
            # Write totals row
            writer.writerow([
                'TOTAL',
                f"{total_debit:.2f}",
                f"{total_tips:.2f}",
                f"{total_sales:.2f}"
            ])
        
        print(f"CSV file created: {filename}")
        return filename
    
    def export_multiple_months_csv(self, year_months: List[tuple], filename: str = None) -> str:
        """
        Export data for multiple months to a single CSV file.
        
        Args:
            year_months: List of (year, month) tuples
            filename: Output filename (optional)
            
        Returns:
            Path to created CSV file
        """
        if filename is None:
            months_str = "_".join([f"{year}_{month:02d}" for year, month in year_months])
            filename = f"clover_combined_months_{months_str}.csv"
        
        all_data = []
        grand_total_debit = 0.0
        grand_total_tips = 0.0
        grand_total_sales = 0.0
        
        # Collect data from all months
        for year, month in year_months:
            monthly_data = self.generate_monthly_csv_data(year, month)
            all_data.extend(monthly_data)
            
            # Calculate monthly totals for grand total
            monthly_debit = sum(row['debit'] for row in monthly_data)
            monthly_tips = sum(row['tip'] for row in monthly_data)
            monthly_sales = sum(row['total'] for row in monthly_data)
            
            grand_total_debit += monthly_debit
            grand_total_tips += monthly_tips
            grand_total_sales += monthly_sales
        
        # Create header with multiple months
        months_names = [f"{calendar.month_name[month]} {year}" for year, month in year_months]
        months_header = ", ".join(months_names)
        
        # Write CSV file
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Write header lines
            csvfile.write("Belle Nails and Spa\n")
            csvfile.write(f"Sales for the months of {months_header}\n")
            
            # Write CSV data
            writer = csv.writer(csvfile)
            writer.writerow(['date', 'debit', 'tip', 'total'])
            
            for row in all_data:
                writer.writerow([
                    row['date'],
                    f"{row['debit']:.2f}",
                    f"{row['tip']:.2f}",
                    f"{row['total']:.2f}"
                ])
            
            # Write grand totals row
            writer.writerow([
                'GRAND TOTAL',
                f"{grand_total_debit:.2f}",
                f"{grand_total_tips:.2f}",
                f"{grand_total_sales:.2f}"
            ])
        
        print(f"Multi-month CSV file created: {filename}")
        return filename


def load_config_from_env() -> Dict[str, str]:
    """Load API configuration from environment variables."""
    return {
        'access_token': os.getenv('CLOVER_ACCESS_TOKEN'),
        'merchant_id': os.getenv('CLOVER_MERCHANT_ID'),
        'base_url': os.getenv('CLOVER_BASE_URL', 'https://api.clover.com')
    }


def load_config_from_file() -> Dict[str, str]:
    """Load API configuration from config.py file."""
    try:
        import config
        return {
            'access_token': getattr(config, 'CLOVER_ACCESS_TOKEN', ''),
            'merchant_id': getattr(config, 'CLOVER_MERCHANT_ID', ''),
            'base_url': getattr(config, 'CLOVER_BASE_URL', 'https://api.clover.com')
        }
    except ImportError:
        print("Warning: config.py file not found. Create one from config_template.py")
        return {
            'access_token': '',
            'merchant_id': '',
            'base_url': 'https://api.clover.com'
        }


def save_to_file(data: str, filename: str):
    """Save data to a file."""
    try:
        with open(filename, 'w') as f:
            f.write(data)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to file: {e}")


def main():
    """Main function to run the script."""
    # Calculate previous month as default
    today = datetime.now()
    if today.month == 1:
        default_year = today.year - 1
        default_month = 12
    else:
        default_year = today.year
        default_month = today.month - 1
    
    parser = argparse.ArgumentParser(description='Retrieve Clover batch/closeout information by month')
    parser.add_argument('--year', type=int, default=default_year, 
                       help=f'Year (default: {default_year} - previous month\'s year)')
    parser.add_argument('--month', type=str, default=str(default_month),
                       help=f'Month 1-12 or comma-separated months like "1,2,3" (default: {default_month} - previous month). For multiple months, generates both individual monthly reports and a combined report.')
    parser.add_argument('--token', type=str, help='Clover API access token')
    parser.add_argument('--merchant', type=str, help='Clover merchant ID')
    parser.add_argument('--output', type=str, help='Output CSV file path (optional, defaults to clover_monthly_data_YYYY_MM.csv)')
    parser.add_argument('--env', action='store_true', 
                       help='Load credentials from environment variables')
    
    args = parser.parse_args()
    
    # Parse and validate months
    try:
        if ',' in args.month:
            # Multiple months specified
            months = [int(m.strip()) for m in args.month.split(',')]
            year_months = [(args.year, month) for month in months]
        else:
            # Single month specified
            month = int(args.month)
            if not 1 <= month <= 12:
                print("Error: Month must be between 1 and 12")
                return
            year_months = [(args.year, month)]
        
        # Validate all months
        for year, month in year_months:
            if not 1 <= month <= 12:
                print(f"Error: Month {month} must be between 1 and 12")
                return
                
    except ValueError:
        print("Error: Invalid month format. Use single month (e.g., 6) or comma-separated (e.g., 1,2,3)")
        return
    
    # Get API credentials - default to config file, then other methods
    if args.env:
        config = load_config_from_env()
        access_token = config['access_token']
        merchant_id = config['merchant_id']
        base_url = config['base_url']
    elif args.token and args.merchant:
        # Direct command line arguments override config file
        access_token = args.token
        merchant_id = args.merchant
        base_url = 'https://api.clover.com'
    else:
        # Default: try to load from config file first
        config = load_config_from_file()
        access_token = config['access_token']
        merchant_id = config['merchant_id']
        base_url = config['base_url']
    
    if not access_token or not merchant_id:
        print("Error: Missing required credentials.")
        print("By default, the script tries to load from config.py file.")
        print("Choose one of the following options:")
        print("1. Create config.py with your credentials (recommended):")
        print("   Copy config_template.py to config.py and fill in your credentials")
        print("2. Use --env with environment variables:")
        print("   CLOVER_ACCESS_TOKEN")
        print("   CLOVER_MERCHANT_ID")
        print("   CLOVER_BASE_URL (optional)")
        print("3. Use --token and --merchant arguments for one-time use")
        return
    
    # Initialize API client
    try:
        clover = CloverAPI(access_token, merchant_id, base_url)
        
        if len(year_months) == 1:
            # Single month
            year, month = year_months[0]
            print(f"Generating CSV report for {calendar.month_name[month]} {year}...")
            csv_filename = clover.export_monthly_csv(year, month, args.output)
            print(f"CSV report completed: {csv_filename}")
        else:
            # Multiple months - generate individual reports and combined report
            months_str = ", ".join([f"{calendar.month_name[month]} {year}" for year, month in year_months])
            print(f"Generating CSV reports for multiple months: {months_str}...")
            
            individual_files = []
            
            # Generate individual monthly reports
            print("\nGenerating individual monthly reports:")
            for year, month in year_months:
                individual_filename = f"clover_monthly_data_{year}_{month:02d}.csv"
                csv_file = clover.export_monthly_csv(year, month, individual_filename)
                individual_files.append(csv_file)
                print(f"  - {calendar.month_name[month]} {year}: {csv_file}")
            
            # Generate combined report
            print(f"\nGenerating combined report for all months...")
            combined_filename = clover.export_multiple_months_csv(year_months, args.output)
            
            print(f"\nAll reports completed!")
            print(f"Individual monthly reports: {len(individual_files)} files")
            for file in individual_files:
                print(f"  - {file}")
            print(f"Combined report: {combined_filename}")
        
    except Exception as e:
        print(f"Script execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()