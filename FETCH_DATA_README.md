# Fetching ICD-10 F64 Data from Genesis Destatis

This document explains how to fetch ICD-10 F64 (Störung der Geschlechtsidentität / Gender Identity Disorder) data from the Genesis Destatis database.

## Overview

We need to fetch data from two Genesis Destatis tables:
- **Table 23131-0011**: Krankenhausbehandlungen nach Behandlungsort (hospital treatments by treatment location)
- **Table 23131-0012**: Krankenhausbehandlungen nach Wohnort (hospital treatments by residence location)

### Data Requirements

- **Years**: 2005-2024
- **Bundesländer**: All German federal states
- **Geschlecht**: All gender categories
- **Altersgruppen**: All age groups
- **Filter**: ICD-10 F64 only

### Important Notes

⚠️ **The existing data files in this repository** (e.g., `GAC Daten Roh.csv`) contain data about genital surgeries, **NOT** ICD-10 F64 data. They are unrelated to this task.

## Prerequisites

### R Environment

1. **Install R** (version 4.0 or higher recommended)
   - Download from: https://cran.r-project.org/

2. **Install required packages**:
   ```r
   # Install devtools if not already installed
   install.packages("devtools")
   install.packages("tidyverse")
   
   # IMPORTANT: Install restatis from GitHub (NOT from CRAN)
   # The CRAN version has bugs
   devtools::install_github("CorrelAid/restatis")
   ```

3. **Genesis Destatis Credentials**:
   - Username: joel@joellevtov.com
   - Password: eKy6R7M!3jD8aokK

## How to Fetch the Data

### Method 1: Using the R Script (Recommended)

Run the provided R script:

```bash
Rscript fetch_f64_data.R
```

Or in R/RStudio:

```r
source("fetch_f64_data.R")
```

The script will:
1. Authenticate with Genesis Destatis
2. Request data jobs for both tables (23131-0011 and 23131-0012)
3. Filter for ICD-10 F64
4. Download the completed jobs
5. Combine data from both tables
6. Save to `F64_Daten_Roh.csv`

### Method 2: Manual Step-by-Step Process

If you need to fetch the data manually:

```r
library(tidyverse)
library(restatis)

# Step 1: Authenticate (no token needed)
gen_auth_save("genesis", use_token = FALSE)

# Step 2: Request data job for table 23131-0011 (nach Behandlungsort)
gen_table(
    database = "genesis",
    name = "23131-0011",
    startyear = "2005",
    endyear = "2024",
    classifyingvariable1 = "ICD10C",  # ICD-10 codes
    classifyingkey1 = "F64",          # Filter for F64 only
    job = TRUE                        # Must use job-based approach
)

# Step 3: Request data job for table 23131-0012 (nach Wohnort)
gen_table(
    database = "genesis",
    name = "23131-0012",
    startyear = "2005",
    endyear = "2024",
    classifyingvariable1 = "ICD10C",
    classifyingkey1 = "F64",
    job = TRUE
)

# Step 4: Wait for jobs to process (a few seconds)
Sys.sleep(10)

# Step 5: List available jobs
jobs <- gen_list_jobs(database = "genesis")
print(jobs)

# Step 6: Download the completed jobs
# Look for job names containing "23131-0011" or "23131-0012" in the jobs list
data_behandlungsort <- gen_download_job(
    database = "genesis",
    name = "YOUR_JOB_NAME_FOR_23131-0011"  # Replace with actual job name
)

data_wohnort <- gen_download_job(
    database = "genesis",
    name = "YOUR_JOB_NAME_FOR_23131-0012"  # Replace with actual job name
)

# Step 7: Combine and save
data_behandlungsort <- data_behandlungsort %>%
    mutate(`Wohnort/Behandlungsort` = "nach Behandlungsort")

data_wohnort <- data_wohnort %>%
    mutate(`Wohnort/Behandlungsort` = "nach Wohnort")

combined_data <- bind_rows(data_behandlungsort, data_wohnort)

write_csv2(combined_data, "F64_Daten_Roh.csv")
```

## Understanding the Genesis API

### Why Job-Based Approach?

The Genesis API requires a job-based approach for filtered queries:

1. **Request a job**: You submit a data request with filters
2. **Job processing**: Genesis processes your request in the background
3. **List jobs**: You check available jobs to find your completed job
4. **Download job**: You download the processed data

You **cannot** fetch filtered data directly with an API key.

### Why GitHub restatis Package?

The CRAN version of `restatis` has bugs that prevent proper data fetching. The GitHub version (`CorrelAid/restatis`) has fixes for these issues.

## Expected Output

After successful execution, you should have:

- **File**: `F64_Daten_Roh.csv`
- **Format**: Semicolon-separated CSV (`;`)
- **Encoding**: UTF-8
- **Columns**: 
  - Jahr (Year)
  - Bundesland (Federal State)
  - Geschlecht (Gender)
  - Wohnort/Behandlungsort (Residence/Treatment Location)
  - Altersgruppe (Age Group)
  - Anzahl (Count)
  - Additional columns from Genesis

## Troubleshooting

### Problem: "No jobs found"

**Solution**: Jobs may still be processing. Wait a few more seconds and run:
```r
jobs <- gen_list_jobs(database = "genesis")
print(jobs)
```

### Problem: "Authentication failed"

**Solution**: Make sure you've run:
```r
gen_auth_save("genesis", use_token = FALSE)
```

Then enter your credentials when prompted.

### Problem: "Package not found"

**Solution**: Install from GitHub:
```r
devtools::install_github("CorrelAid/restatis")
```

### Problem: Network/DNS errors

**Solution**: 
- Check your internet connection
- Verify you can access: https://www-genesis.destatis.de
- Some corporate networks may block access

## Alternative: Python Script

A Python script (`fetch_genesis_data.py`) is also provided, but note:
- It may not work in all environments due to network restrictions
- The R approach is the primary recommended method
- The Python `pystatis` library may have different capabilities

## Data Structure

The fetched data will include:

- **Jahre**: 2005, 2006, ..., 2024
- **Bundesländer**: All 16 German federal states plus aggregate categories
- **Geschlecht**: Gender categories (männlich, weiblich, divers, etc.)
- **Altersgruppen**: Age groups (unter 1 Jahr, 1-5 Jahre, 5-10 Jahre, etc.)
- **ICD-10 F64**: Only records for Störung der Geschlechtsidentität

## Next Steps

After fetching the data:

1. Verify data completeness (all years, states, categories)
2. Check for missing values or data quality issues
3. Use the data in your analysis workflow
4. Update your R markdown analysis file to use the new data

## References

- Genesis Destatis: https://www-genesis.destatis.de
- restatis GitHub: https://github.com/CorrelAid/restatis
- Genesis API Documentation: https://www-genesis.destatis.de/genesis/misc/GENESIS-Webservices_Einfuehrung.pdf
