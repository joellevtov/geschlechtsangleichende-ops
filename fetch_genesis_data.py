#!/usr/bin/env python3
"""
Script to fetch data from Genesis Destatis database for ICD-10 F64 analysis.

This script fetches data from two tables:
- Table 23131-0011: Krankenhausbehandlungen nach Behandlungsort (by treatment location)
- Table 23131-0012: Krankenhausbehandlungen nach Wohnort (by residence location)

Requirements:
- Years: 2005-2024
- All Bundesländer (federal states)
- All Geschlecht (gender categories)
- All Altersgruppen (age groups)
- Filter: ICD-10 F64 (Störung der Geschlechtsidentität / Gender Identity Disorder)

Credentials are required to access the Genesis API. Configure them by running:
    from pystatis import config
    config.setup_credentials()

Or set them programmatically as shown below.
"""

import pandas as pd
from pystatis import Table
from pystatis import config
import sys
import os


def setup_genesis_credentials(username=None, password=None):
    """
    Set up Genesis Destatis credentials.
    
    Args:
        username: Genesis API username (email)
        password: Genesis API password
    """
    try:
        cfg = config.load_config()
        
        # If credentials are provided, set them
        if username and password:
            cfg.set('genesis', 'username', username)
            cfg.set('genesis', 'password', password)
            
            # Write config file
            config_file = os.path.join(config.DEFAULT_CONFIG_DIR, "config.ini")
            with open(config_file, 'w') as f:
                cfg.write(f)
            print(f"✓ Credentials configured for Genesis API")
        else:
            print("⚠ No credentials provided. Using existing configuration.")
            
        # Verify credentials are set
        if not cfg.get('genesis', 'username'):
            print("⚠ Warning: No username configured for Genesis API")
            print("  Please set credentials using:")
            print("    from pystatis import config")
            print("    config.setup_credentials()")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error setting up credentials: {e}")
        return False


def fetch_table_data(table_code, startyear="2005", endyear="2024"):
    """
    Fetch data from a Genesis table.
    
    Args:
        table_code: Genesis table code (e.g., "23131-0011")
        startyear: Start year for data (default: 2005)
        endyear: End year for data (default: 2024)
        
    Returns:
        pandas.DataFrame: Fetched data
    """
    try:
        print(f"\n📊 Fetching data from table {table_code}...")
        print(f"   Years: {startyear}-{endyear}")
        
        # Create table object
        table = Table(name=table_code)
        
        # Fetch data
        # The prettify parameter reformats the table into a readable format
        table.get_data(
            startyear=startyear,
            endyear=endyear,
            prettify=True,
            language='de'  # German language for labels
        )
        
        if table.data is not None:
            print(f"✓ Successfully fetched {len(table.data)} rows from table {table_code}")
            print(f"  Columns: {table.data.columns.tolist()}")
            return table.data
        else:
            print(f"✗ No data returned from table {table_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error fetching data from table {table_code}: {e}")
        import traceback
        traceback.print_exc()
        return None


def combine_and_save_data(data_behandlungsort, data_wohnort, output_file="GAC_Daten_Roh.csv"):
    """
    Combine data from both tables and save to CSV.
    
    Args:
        data_behandlungsort: DataFrame from table 23131-0011 (nach Behandlungsort)
        data_wohnort: DataFrame from table 23131-0012 (nach Wohnort)
        output_file: Output CSV filename
    """
    try:
        print(f"\n📝 Combining data from both tables...")
        
        # Add identifier column to distinguish the source
        if data_behandlungsort is not None:
            data_behandlungsort = data_behandlungsort.copy()
            data_behandlungsort['Wohnort/Behandlungsort'] = 'nach Behandlungsort'
            print(f"   Behandlungsort data: {len(data_behandlungsort)} rows")
        
        if data_wohnort is not None:
            data_wohnort = data_wohnort.copy()
            data_wohnort['Wohnort/Behandlungsort'] = 'nach Wohnort'
            print(f"   Wohnort data: {len(data_wohnort)} rows")
        
        # Combine dataframes
        if data_behandlungsort is not None and data_wohnort is not None:
            combined_data = pd.concat([data_behandlungsort, data_wohnort], ignore_index=True)
        elif data_behandlungsort is not None:
            combined_data = data_behandlungsort
        elif data_wohnort is not None:
            combined_data = data_wohnort
        else:
            print("✗ No data to save")
            return False
        
        # Sort by Jahr (year) and other relevant columns
        if 'Jahr' in combined_data.columns:
            combined_data = combined_data.sort_values('Jahr')
        
        # Save to CSV with semicolon separator (standard for German data)
        combined_data.to_csv(output_file, sep=';', index=False, encoding='utf-8')
        print(f"✓ Combined data saved to {output_file}")
        print(f"  Total rows: {len(combined_data)}")
        print(f"  Columns: {combined_data.columns.tolist()}")
        
        # Display summary statistics
        if 'Jahr' in combined_data.columns:
            print(f"\n📈 Data summary:")
            print(f"  Years: {combined_data['Jahr'].min()} - {combined_data['Jahr'].max()}")
            if 'Bundesland' in combined_data.columns:
                print(f"  Bundesländer: {combined_data['Bundesland'].nunique()}")
            if 'Geschlecht' in combined_data.columns:
                print(f"  Geschlecht categories: {combined_data['Geschlecht'].nunique()}")
            if 'Altersgruppe' in combined_data.columns:
                print(f"  Age groups: {combined_data['Altersgruppe'].nunique()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error combining and saving data: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to fetch and process Genesis data."""
    
    print("=" * 70)
    print("Genesis Destatis Data Fetcher")
    print("ICD-10 F64: Störung der Geschlechtsidentität")
    print("=" * 70)
    
    # Check for credentials in environment variables
    username = os.environ.get('GENESIS_USERNAME')
    password = os.environ.get('GENESIS_PASSWORD')
    
    if not username or not password:
        print("\n⚠ Credentials not found in environment variables.")
        print("  Set GENESIS_USERNAME and GENESIS_PASSWORD environment variables,")
        print("  or edit this script to include credentials directly.")
        print("\n  Alternatively, configure credentials using:")
        print("    from pystatis import config")
        print("    config.setup_credentials()")
        print()
    
    # Setup credentials
    if not setup_genesis_credentials(username, password):
        print("\n⚠ Continuing without credential setup...")
    
    # Fetch data from both tables
    print("\n" + "=" * 70)
    print("Fetching data from Genesis Destatis tables")
    print("=" * 70)
    
    # Table 23131-0011: nach Behandlungsort (by treatment location)
    data_behandlungsort = fetch_table_data(
        table_code="23131-0011",
        startyear="2005",
        endyear="2024"
    )
    
    # Table 23131-0012: nach Wohnort (by residence location)
    data_wohnort = fetch_table_data(
        table_code="23131-0012",
        startyear="2005",
        endyear="2024"
    )
    
    # Combine and save data
    if data_behandlungsort is not None or data_wohnort is not None:
        print("\n" + "=" * 70)
        print("Saving data")
        print("=" * 70)
        
        success = combine_and_save_data(
            data_behandlungsort,
            data_wohnort,
            output_file="GAC_Daten_Roh.csv"
        )
        
        if success:
            print("\n" + "=" * 70)
            print("✓ Data fetching completed successfully!")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("✗ Failed to save data")
            print("=" * 70)
            return 1
    else:
        print("\n" + "=" * 70)
        print("✗ Failed to fetch data from Genesis tables")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
