#!/bin/bash
# filepath: /Users/rohitmac/Desktop/data-service-framework-new/scripts/trigger_job.sh

# Define API base URL
API_BASE="http://localhost:8000/api/v1"

# Check if job_id was provided as an argument
if [ -z "$1" ]; then
    echo "⚠️ No job ID provided as argument. Please provide a job ID."
    echo "Usage: $0 <job_id>"
    echo "Example: $0 4bb6488c-5637-4e0f-92f0-9120e0efa9e0"
    exit 1
fi

# Job ID to trigger - use the first command line argument
JOB_ID="$1"

# Trigger the job execution
echo "🚀 Triggering job execution for job ID: $JOB_ID"

# Use -w to get HTTP status code and -o to redirect response body to a separate file
HTTP_STATUS=$(curl -s -w "%{http_code}" -o /tmp/job_response.txt -X POST "$API_BASE/jobs/$JOB_ID/trigger" \
  -H "Content-Type: application/json" \
  -d '{
    "execution_host": "trigger_job.sh",
    "override_payload": {
      "additional_parameter": "test_value"
    }
  }')

# Get the response body
TRIGGER_RESPONSE=$(cat /tmp/job_response.txt)

echo "Response status code: $HTTP_STATUS"
echo "Response body: $TRIGGER_RESPONSE"

# Check HTTP status code
if [ "$HTTP_STATUS" == "202" ]; then
    # 202 Accepted - Job was successfully triggered
    echo "✅ Job triggered successfully! (202 Accepted)"
    
    # Check if the response is valid JSON with a task_id
    if echo "$TRIGGER_RESPONSE" | jq -e '.task_id' > /dev/null 2>&1; then
        TASK_ID=$(echo "$TRIGGER_RESPONSE" | jq -r '.task_id')
        echo "🔄 Task assigned to Celery with task_id: $TASK_ID"
        echo "Response details:"
        echo "$TRIGGER_RESPONSE" | jq '.'
    else
        echo "⚠️ Response is valid but missing task_id"
        echo "$TRIGGER_RESPONSE" | jq '.' 2>/dev/null || echo "$TRIGGER_RESPONSE"
    fi
    exit 0
elif [ "$HTTP_STATUS" == "404" ]; then
    echo "❌ ERROR: Job ID not found (404 Not Found)"
    echo "$TRIGGER_RESPONSE"
    exit 1
elif [ "$HTTP_STATUS" == "500" ]; then
    echo "❌ SERVER ERROR: Internal Server Error (500)"
    echo "$TRIGGER_RESPONSE"
    exit 1
else
    echo "❌ ERROR: Something went wrong while triggering the job"
    echo "Status code: $HTTP_STATUS"
    echo "Response: $TRIGGER_RESPONSE"
    echo ""
    echo "Possible issues:"
    echo "  1. API server is not running"
    echo "  2. Job ID does not exist: $JOB_ID"
    echo "  3. Job is disabled"
    echo "  4. Server error processing the job"
    exit 1
fi