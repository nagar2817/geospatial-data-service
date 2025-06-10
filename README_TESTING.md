# Job Discovery Pipeline Testing Guide

## Quick Start

1. **Setup Environment**
   ```bash
       make setup
   ```

2. **Run Full Test Suite**
    ```bash
    make test-job-discovery
    ```

3. **Test Individual Flows**
    ```bash
    # Test all trigger types
    python3 playground/job_discovery_pipeline.py
    
    # Test specific triggers
    python3 playground/test_job_discovery_cron.py
    python3 playground/test_job_discovery_api.py
    ```