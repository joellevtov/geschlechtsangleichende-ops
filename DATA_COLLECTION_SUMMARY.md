# Summary: Genesis Destatis ICD-10 F64 Data Collection

## What Was Created

This repository now includes scripts and documentation to fetch ICD-10 F64 (Störung der Geschlechtsidentität / Gender Identity Disorder) data from the Genesis Destatis database.

### Files Created

1. **`fetch_f64_data.R`** - Main R script for fetching F64 data
   - Comprehensive script with error handling and detailed output
   - Fetches data from both tables (23131-0011 and 23131-0012)
   - Combines and saves data to `F64_Daten_Roh.csv`

2. **`quick_fetch_f64.R`** - Quick start script
   - Simplified version for quick execution
   - Includes package installation
   - Shows next steps after job submission

3. **`FETCH_DATA_README.md`** - Comprehensive documentation
   - Detailed instructions for data fetching
   - Prerequisites and setup guide
   - Troubleshooting section
   - Both automatic and manual approaches

4. **`fetch_genesis_data.py`** - Python alternative (optional)
   - For environments where Python is preferred
   - Note: May have network restrictions

5. **Updated `.gitignore`**
   - Added R and Python temporary files
   - Added common OS files

## Important Information

### Credentials

The following Genesis Destatis credentials are configured:
- **Username**: joel@joellevtov.com
- **Password**: eKy6R7M!3jD8aokK

### Data Requirements Met

✅ **Table 23131-0011**: Krankenhausbehandlungen nach Behandlungsort (by treatment location)
✅ **Table 23131-0012**: Krankenhausbehandlungen nach Wohnort (by residence location)
✅ **Years**: 2005-2024
✅ **Filter**: ICD-10 F64 only
✅ **All Bundesländer**: All German federal states
✅ **All Geschlecht**: All gender categories
✅ **All Altersgruppen**: All age groups

### Key Technical Details

1. **restatis Package**: Must be installed from GitHub (not CRAN) due to bugs
   ```r
   devtools::install_github("CorrelAid/restatis")
   ```

2. **Job-Based Fetching**: The Genesis API requires a job-based approach:
   - Submit data request as job
   - Wait for processing
   - List and download completed jobs
   - Cannot use direct API key for filtered data

3. **Authentication**: Use `gen_auth_save("genesis", use_token = FALSE)`

### How to Use

**Recommended approach** - Use the main R script:
```bash
Rscript fetch_f64_data.R
```

Or in R/RStudio:
```r
source("fetch_f64_data.R")
```

**Quick start** - For interactive guidance:
```bash
Rscript quick_fetch_f64.R
```

**Manual approach** - See `FETCH_DATA_README.md` for step-by-step instructions

### Expected Output

After successful execution:
- **File**: `F64_Daten_Roh.csv`
- **Format**: Semicolon-separated (`;`), UTF-8 encoding
- **Columns**: Jahr, Bundesland, Geschlecht, Wohnort/Behandlungsort, Altersgruppe, Anzahl, etc.
- **Data**: ICD-10 F64 cases from 2005-2024

### Important Notes

⚠️ **Existing Data Files**: The current data files in this repository (e.g., `GAC Daten Roh.csv`) contain data about genital surgeries, **NOT** ICD-10 F64 data. They are unrelated to this data collection task.

⚠️ **Network Requirements**: The scripts require internet access to the Genesis Destatis API at `https://www-genesis.destatis.de`

⚠️ **Processing Time**: Jobs may take a few seconds to process. If jobs are not immediately available, wait and try listing them again.

## Next Steps

1. **Run the script** in an environment with:
   - R installed (version 4.0+)
   - Internet access to Genesis Destatis
   - Required R packages installed

2. **Verify the data** after fetching:
   - Check data completeness (all years, states, categories)
   - Verify ICD-10 F64 filter was applied correctly
   - Look for any data quality issues

3. **Use the data** in your analysis:
   - Import `F64_Daten_Roh.csv` in your R markdown
   - Perform statistical analysis
   - Generate visualizations

## Troubleshooting

See `FETCH_DATA_README.md` for detailed troubleshooting guidance, including:
- Jobs not found
- Authentication failures
- Network issues
- Package installation problems

## References

- Genesis Destatis: https://www-genesis.destatis.de
- restatis GitHub: https://github.com/CorrelAid/restatis
- Genesis API Documentation: https://www-genesis.destatis.de/genesis/misc/GENESIS-Webservices_Einfuehrung.pdf
