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

Note: This doesn't work (fully). It only is fetching data for 2005. 
"""

import pandas as pd
from pystatis import Table
from pystatis import config
import sys
import os


def setup_genesis_credentials(username=None, password=None):
    """
    Set up Genesis Destatis credentials using pystatis's native method.
    
    Args:
        username: Genesis API username (email)
        password: Genesis API password
    """
    try:
        from pystatis.config import init_config, write_config
        
        # If credentials are provided, set them
        if username and password:
            # Initialize configuration for genesis database
            # Note: init_config doesn't take db_name as parameter in newer versions
            init_config(
                username=username,
                password=password
            )
            
            # Write the configuration to file
            write_config()
            
            print(f"✓ Credentials configured for Genesis API")
            return True
        else:
            print("⚠ No credentials provided. Using existing configuration.")
            print("  Please set GENESIS_USERNAME and GENESIS_PASSWORD environment variables")
            return False
            
    except Exception as e:
        print(f"✗ Error setting up credentials: {e}")
        import traceback
        traceback.print_exc()
        return False


def fetch_table_data(table_code, startyear="2005", endyear="2024"):
    """
    Fetch data from a Genesis table, fetching year by year to avoid size limits.
    
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
        print(f"   Filter: ICD-10 F64 (Gender Identity Disorder)")
        
        # For table 23131-0011, we need to fetch in smaller chunks due to size limits
        # We'll fetch year by year to avoid the "table too large" error
        all_data = []
        
        for year in range(int(startyear), int(endyear) + 1):
            try:
                print(f"   Fetching year {year}...", end=" ")
                
                # Create table object
                table = Table(name=table_code)
                
                # Fetch data for this year only
                table.get_data(
                    startyear=str(year),
                    endyear=str(year),
                    prettify=True,
                    language='de'  # German language for labels
                )
                
                if table.data is not None and len(table.data) > 0:
                    # Filter for F64 diagnoses
                    # The ICD column name might vary, so we'll check for common variations
                    icd_columns = [col for col in table.data.columns if 'ICD' in col.upper() or 'DIAGNOSE' in col.upper()]
                    
                    if icd_columns:
                        icd_col = icd_columns[0]
                        # Filter for F64 and its subcategories (F64.0, F64.1, F64.2, F64.8, F64.9)
                        filtered_data = table.data[table.data[icd_col].astype(str).str.startswith('F64')]
                        
                        if len(filtered_data) > 0:
                            all_data.append(filtered_data)
                            print(f"✓ {len(filtered_data)} F64 rows")
                        else:
                            print("(no F64 data)")
                    else:
                        # If we can't find ICD column, keep all data (will filter later)
                        all_data.append(table.data)
                        print(f"✓ {len(table.data)} rows (ICD column not found, keeping all)")
                else:
                    print("(no data)")
                    
            except Exception as year_error:
                error_msg = str(year_error)
                if "43917120" in error_msg or "Tabelle enthält" in error_msg:
                    print(f"✗ Table too large even for single year")
                else:
                    print(f"✗ Error: {year_error}")
                continue
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            print(f"\n✓ Successfully fetched {len(combined_data)} total rows from table {table_code}")
            print(f"  Columns: {combined_data.columns.tolist()}")
            return combined_data
        else:
            print(f"\n✗ No data returned from table {table_code}")
            return None
            
    except Exception as e:
        print(f"\n✗ Error fetching data from table {table_code}: {e}")
        import traceback
        traceback.print_exc()
        return None


def combine_and_save_data(data_behandlungsort, data_wohnort, output_file="F64_Daten_Roh.csv"):
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
    # Fetching year by year to avoid "table too large" error
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
            output_file="F64_Daten_Roh.csv"
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