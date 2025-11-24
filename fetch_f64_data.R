#!/usr/bin/env Rscript
#
# Script to fetch ICD-10 F64 data from Genesis Destatis database
#
# This script fetches data from two tables:
# - Table 23131-0011: Krankenhausbehandlungen nach Behandlungsort (by treatment location)
# - Table 23131-0012: Krankenhausbehandlungen nach Wohnort (by residence location)
#
# Requirements:
# - Years: 2005-2024
# - All Bundesländer (federal states)
# - All Geschlecht (gender categories)
# - All Altersgruppen (age groups)
# - Filter: ICD-10 F64 (Störung der Geschlechtsidentität / Gender Identity Disorder)
#
# NOTE: The restatis package must be installed from GitHub, not CRAN, due to bugs:
#   devtools::install_github("CorrelAid/restatis")
#
# IMPORTANT: Data cannot be fetched directly with API key. Must use job-based approach:
#   1. Request data as a job
#   2. List jobs to find the job name
#   3. Download the completed job

library(tidyverse)
library(restatis)

# ============================================================================
# Configuration
# ============================================================================

# Authenticate with Genesis (no token needed)
cat("Authenticating with Genesis Destatis...\n")
gen_auth_save("genesis", use_token = FALSE)
cat("✓ Authentication configured\n\n")

# ============================================================================
# Function to fetch data from a table
# ============================================================================

fetch_table_data <- function(table_code, table_name) {
    cat(sprintf("============================================================\n"))
    cat(sprintf("Fetching data from table %s (%s)\n", table_code, table_name))
    cat(sprintf("============================================================\n"))
    
    # Step 1: Request metadata to understand table structure
    cat("\nStep 1: Fetching table metadata...\n")
    tryCatch({
        metadata <- gen_metadata_table(
            code = table_code,
            database = "genesis"
        )
        cat("✓ Metadata fetched successfully\n")
        print(metadata)
    }, error = function(e) {
        cat(sprintf("⚠ Warning: Could not fetch metadata: %s\n", e$message))
    })
    
    # Step 2: Request data as a job (must use job=TRUE for filtering)
    cat("\nStep 2: Requesting data job...\n")
    cat(sprintf("  Table: %s\n", table_code))
    cat("  Years: 2005-2024\n")
    cat("  Filter: ICD-10 F64\n")
    
    tryCatch({
        # Request data for all years from 2005 to 2024
        # Filter for ICD-10 code F64
        job_response <- gen_table(
            database = "genesis",
            name = table_code,
            startyear = "2005",
            endyear = "2024",
            classifyingvariable1 = "ICD10C",  # ICD-10 codes
            classifyingkey1 = "F64",          # Filter for F64 only
            job = TRUE
        )
        
        cat("✓ Data job requested successfully\n")
        if (!is.null(job_response)) {
            print(job_response)
        }
        
        # Step 3: Wait a moment for job to be processed
        cat("\nStep 3: Waiting for job to be processed...\n")
        Sys.sleep(5)  # Wait 5 seconds
        
        # Step 4: List all jobs to find our job
        cat("\nStep 4: Listing available jobs...\n")
        jobs <- gen_list_jobs(database = "genesis")
        
        if (!is.null(jobs) && nrow(jobs) > 0) {
            cat(sprintf("✓ Found %d job(s)\n", nrow(jobs)))
            print(jobs)
            
            # Find jobs related to our table
            relevant_jobs <- jobs[grepl(table_code, jobs$Code, fixed = TRUE), ]
            
            if (nrow(relevant_jobs) > 0) {
                cat(sprintf("\n✓ Found %d job(s) for table %s\n", nrow(relevant_jobs), table_code))
                
                # Get the most recent job
                job_name <- relevant_jobs$Code[1]
                cat(sprintf("  Using job: %s\n", job_name))
                
                # Step 5: Download the job data
                cat("\nStep 5: Downloading job data...\n")
                data <- gen_download_job(
                    database = "genesis",
                    name = job_name
                )
                
                if (!is.null(data) && nrow(data) > 0) {
                    cat(sprintf("✓ Successfully downloaded %d rows\n", nrow(data)))
                    return(data)
                } else {
                    cat("✗ No data returned from job\n")
                    return(NULL)
                }
            } else {
                cat(sprintf("⚠ No jobs found for table %s\n", table_code))
                cat("  The job may still be processing. Please try again in a few moments.\n")
                return(NULL)
            }
        } else {
            cat("⚠ No jobs available\n")
            return(NULL)
        }
        
    }, error = function(e) {
        cat(sprintf("✗ Error: %s\n", e$message))
        print(e)
        return(NULL)
    })
}

# ============================================================================
# Main execution
# ============================================================================

cat("============================================================\n")
cat("Genesis Destatis Data Fetcher for ICD-10 F64\n")
cat("Störung der Geschlechtsidentität (Gender Identity Disorder)\n")
cat("============================================================\n\n")

# Fetch data from table 23131-0011 (nach Behandlungsort)
data_behandlungsort <- fetch_table_data(
    table_code = "23131-0011",
    table_name = "nach Behandlungsort (by treatment location)"
)

cat("\n\n")

# Fetch data from table 23131-0012 (nach Wohnort)
data_wohnort <- fetch_table_data(
    table_code = "23131-0012",
    table_name = "nach Wohnort (by residence location)"
)

# ============================================================================
# Combine and save data
# ============================================================================

cat("\n============================================================\n")
cat("Combining and saving data\n")
cat("============================================================\n\n")

# Add identifier columns to distinguish source
if (!is.null(data_behandlungsort) && nrow(data_behandlungsort) > 0) {
    data_behandlungsort <- data_behandlungsort %>%
        mutate(`Wohnort/Behandlungsort` = "nach Behandlungsort")
    cat(sprintf("✓ Behandlungsort data: %d rows\n", nrow(data_behandlungsort)))
}

if (!is.null(data_wohnort) && nrow(data_wohnort) > 0) {
    data_wohnort <- data_wohnort %>%
        mutate(`Wohnort/Behandlungsort` = "nach Wohnort")
    cat(sprintf("✓ Wohnort data: %d rows\n", nrow(data_wohnort)))
}

# Combine datasets
combined_data <- NULL

if (!is.null(data_behandlungsort) && !is.null(data_wohnort)) {
    combined_data <- bind_rows(data_behandlungsort, data_wohnort)
} else if (!is.null(data_behandlungsort)) {
    combined_data <- data_behandlungsort
} else if (!is.null(data_wohnort)) {
    combined_data <- data_wohnort
}

# Save to CSV if we have data
if (!is.null(combined_data) && nrow(combined_data) > 0) {
    output_file <- "F64_Daten_Roh.csv"
    
    cat(sprintf("\nSaving combined data to %s...\n", output_file))
    write_csv2(combined_data, output_file)  # write_csv2 uses semicolon separator
    
    cat(sprintf("✓ Data saved successfully\n"))
    cat(sprintf("  Total rows: %d\n", nrow(combined_data)))
    cat(sprintf("  Columns: %s\n", paste(colnames(combined_data), collapse = ", ")))
    
    # Display summary
    cat("\n📈 Data summary:\n")
    if ("Jahr" %in% colnames(combined_data)) {
        cat(sprintf("  Years: %s - %s\n", min(combined_data$Jahr, na.rm = TRUE), 
                                           max(combined_data$Jahr, na.rm = TRUE)))
    }
    if ("Bundesland" %in% colnames(combined_data)) {
        cat(sprintf("  Bundesländer: %d unique\n", n_distinct(combined_data$Bundesland)))
    }
    if ("Geschlecht" %in% colnames(combined_data)) {
        cat(sprintf("  Geschlecht: %d categories\n", n_distinct(combined_data$Geschlecht)))
    }
    if ("Altersgruppe" %in% colnames(combined_data)) {
        cat(sprintf("  Age groups: %d\n", n_distinct(combined_data$Altersgruppe)))
    }
    
    cat("\n============================================================\n")
    cat("✓ Data fetching completed successfully!\n")
    cat("============================================================\n")
    
} else {
    cat("\n============================================================\n")
    cat("✗ No data available to save\n")
    cat("============================================================\n")
    cat("\nPossible reasons:\n")
    cat("  1. Jobs are still being processed - try running this script again\n")
    cat("  2. Authentication failed - check credentials\n")
    cat("  3. Network or API issues\n")
    cat("  4. Table codes or filters may need adjustment\n")
    
    # Show how to check jobs manually
    cat("\nTo check job status manually:\n")
    cat("  library(restatis)\n")
    cat("  gen_auth_save('genesis', use_token = FALSE)\n")
    cat("  jobs <- gen_list_jobs(database = 'genesis')\n")
    cat("  print(jobs)\n")
}
