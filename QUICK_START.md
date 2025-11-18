# Quick Start Guide - Fetch ICD-10 F64 Data

## You're Ready to Fetch the Data! 🚀

All scripts and documentation are ready. Follow these steps:

## Step 1: Install Prerequisites

Make sure you have R installed (version 4.0+). Then install required packages:

```r
# In R console or RStudio:
install.packages("devtools")
install.packages("tidyverse")

# IMPORTANT: Install restatis from GitHub (NOT CRAN)
devtools::install_github("CorrelAid/restatis")
```

## Step 2: Run the Script

Choose one of these methods:

### Option A: Main Script (Recommended)
```bash
Rscript fetch_f64_data.R
```

### Option B: Quick Start Script
```bash
Rscript quick_fetch_f64.R
```

### Option C: In RStudio
```r
source("fetch_f64_data.R")
```

## Step 3: What Happens

The script will:
1. ✅ Authenticate with Genesis Destatis
2. ✅ Request data jobs for tables 23131-0011 and 23131-0012
3. ✅ Filter for ICD-10 F64 only
4. ✅ Wait for jobs to process
5. ✅ Download completed jobs
6. ✅ Combine data from both tables
7. ✅ Save to **F64_Daten_Roh.csv**

## Step 4: Expected Output

You should get a file named **F64_Daten_Roh.csv** with:
- ICD-10 F64 cases
- Years 2005-2024
- All Bundesländer
- All gender categories
- All age groups
- Data from both treatment location and residence location

## If Something Goes Wrong

Check **FETCH_DATA_README.md** for detailed troubleshooting, including:
- Jobs not found → Wait a bit longer and try again
- Authentication failed → Check credentials
- Package errors → Install from GitHub
- Network issues → Check internet connection

## Files in This Repository

- **fetch_f64_data.R** - Main comprehensive script ⭐
- **quick_fetch_f64.R** - Quick start with package installation
- **FETCH_DATA_README.md** - Full documentation 📖
- **DATA_COLLECTION_SUMMARY.md** - Technical summary
- **fetch_genesis_data.py** - Python alternative (optional)

## Credentials

Your Genesis Destatis credentials are already configured in the scripts:
- Username: joel@joellevtov.com
- Password: eKy6R7M!3jD8aokK

## Need Help?

1. Read **FETCH_DATA_README.md** for comprehensive guide
2. Read **DATA_COLLECTION_SUMMARY.md** for technical details
3. Check the troubleshooting section in the README

## After Fetching

Once you have **F64_Daten_Roh.csv**, you can:
1. Verify data completeness
2. Import into your analysis
3. Update your R markdown file to use the new data

---

**Ready?** Run `Rscript fetch_f64_data.R` to start! 🎯
