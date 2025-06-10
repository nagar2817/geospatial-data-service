#!/bin/bash

API_BASE="http://localhost:8000/api/v1"

echo "🧪 Testing Geospatial Data Service API"

# Test health
echo "1. Health check..."
curl -s "$API_BASE/../health" | jq '.' || echo "Health endpoint failed"

# Test job creation
echo -e "\n2. Creating test job..."
JOB_RESPONSE=$(curl -s -X POST "$API_BASE/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "curl Test Job",
    "job_type": "metric_calc", 
    "schedule_type": "event_triggered",
    "enabled": true,
    "payload": {
      "coordinates": [[-122.4194, 37.7749]],
      "satellite_type": "Sentinel-2",
      "metrics": ["ndvi"]
    },
    "target_function": "test_function"
  }')

echo "Job Response: $JOB_RESPONSE"

# Check if job was created successfully
if echo "$JOB_RESPONSE" | jq -e '.job_id' > /dev/null 2>&1; then
    JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.job_id')
    echo "✅ Job created successfully: $JOB_ID"
    
    # List jobs
    echo -e "\n3. Listing all jobs..."
    curl -s "$API_BASE/jobs/" | jq '.jobs[] | {job_id: .job_id, job_name: .job_name, enabled: .enabled}'
    
else
    echo "❌ Job creation failed"
    echo "Response: $JOB_RESPONSE"
fi