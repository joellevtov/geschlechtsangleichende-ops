#!/usr/bin/env Rscript
#
# Quick Start: Fetch ICD-10 F64 Data from Genesis Destatis
#
# This is a simplified version for quick execution.
# For full documentation, see: FETCH_DATA_README.md
# For detailed script, see: fetch_f64_data.R

cat("Installing/loading required packages...\n")

# Install packages if needed
if (!require("tidyverse", quietly = TRUE)) {
    install.packages("tidyverse")
}

if (!require("restatis", quietly = TRUE)) {
    cat("Installing restatis from GitHub...\n")
    if (!require("devtools", quietly = TRUE)) {
        install.packages("devtools")
    }
    devtools::install_github("CorrelAid/restatis")
}

library(tidyverse)
library(restatis)

cat("\n===============================================\n")
cat("Fetching ICD-10 F64 Data from Genesis Destatis\n")
cat("===============================================\n\n")

# Authenticate
cat("Step 1: Authenticating...\n")
gen_auth_save("genesis", use_token = FALSE)
cat("✓ Authenticated\n\n")

# Request jobs
cat("Step 2: Requesting data jobs...\n")

cat("  Requesting table 23131-0011 (nach Behandlungsort)...\n")
gen_table(
    database = "genesis",
    name = "23131-0011",
    startyear = "2005",
    endyear = "2024",
    classifyingvariable1 = "ICD10C",
    classifyingkey1 = "F64",
    job = TRUE
)

cat("  Requesting table 23131-0012 (nach Wohnort)...\n")
gen_table(
    database = "genesis",
    name = "23131-0012",
    startyear = "2005",
    endyear = "2024",
    classifyingvariable1 = "ICD10C",
    classifyingkey1 = "F64",
    job = TRUE
)

cat("✓ Jobs requested\n\n")

# Wait for processing
cat("Step 3: Waiting for jobs to process (10 seconds)...\n")
Sys.sleep(10)

# List jobs
cat("\nStep 4: Listing available jobs...\n")
jobs <- gen_list_jobs(database = "genesis")
print(jobs)

cat("\n\n===============================================\n")
cat("Next Steps:\n")
cat("===============================================\n")
cat("1. Check the jobs list above\n")
cat("2. Find job names containing '23131-0011' and '23131-0012'\n")
cat("3. Download the jobs:\n\n")

cat("   data1 <- gen_download_job(database = 'genesis', name = 'JOB_NAME_1')\n")
cat("   data2 <- gen_download_job(database = 'genesis', name = 'JOB_NAME_2')\n\n")

cat("4. Or run the full script:\n")
cat("   source('fetch_f64_data.R')\n\n")

cat("For more help, see: FETCH_DATA_README.md\n")
