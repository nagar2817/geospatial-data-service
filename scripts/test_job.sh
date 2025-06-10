#!/bin/bash
# filepath: /Users/rohitmac/Desktop/data-service-framework-new/scripts/test_job.sh

# Set the base URL for the API
API_BASE="http://localhost:8000/api/v1"

echo "🚀 Testing Job Creation for Geospatial Data Service"

# Create a job with all required fields
echo -e "\n1. Creating a new job..."
JOB_RESPONSE=$(curl -s -X POST "$API_BASE/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "NDVI Calculation Test",
    "job_type": "metric_calc",
    "schedule_type": "event_triggered",
    "enabled": true,
    "payload": {
      "coordinates": [[-122.4194, 37.7749]],
      "satellite_type": "Sentinel-2",
      "metrics": ["ndvi", "evi"],
      "date_range": {
        "start": "2023-01-01",
        "end": "2023-12-31"
      }
    },
    "target_function": "process_satellite_metrics"
  }')

echo "Job Creation Response:"
echo "$JOB_RESPONSE" | jq '.'

# Check if job was created successfully
if echo "$JOB_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.id')
    echo "✅ Job created successfully with ID: $JOB_ID"
    
    # Get job details
    echo -e "\n2. Getting job details..."
    JOB_DETAILS=$(curl -s "$API_BASE/jobs/$JOB_ID")
    echo "$JOB_DETAILS" | jq '.'

    
else
    echo "❌ Job creation failed"
    echo "Response: $JOB_RESPONSE"
fi