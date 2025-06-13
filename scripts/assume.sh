#!/bin/bash

ROLE_ARN="arn:aws:iam::585768148346:role/gcp-wif-access-role"
SESSION_NAME="localGeeSession"
TMP_EXPIRY_FILE="/tmp/gee_aws_token_expiry"

# Ensure dependencies exist
command -v aws >/dev/null 2>&1 || { echo "❌ aws CLI is not installed."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "❌ jq is not installed."; exit 1; }

# Check if credentials already exist and are valid
if [[ -f "$TMP_EXPIRY_FILE" ]]; then
  EXPIRATION_TIME=$(cat "$TMP_EXPIRY_FILE")
  EXPIRY_EPOCH=$(python3 -c "import datetime; import sys; print(int(datetime.datetime.strptime(sys.argv[1], '%Y-%m-%dT%H:%M:%S%z').timestamp()))" "$EXPIRATION_TIME")
  NOW_EPOCH=$(date "+%s")
  if [[ "$EXPIRY_EPOCH" -gt "$NOW_EPOCH" ]]; then
    echo "✅ Reusing valid AWS credentials. Expire at: $EXPIRATION_TIME"
    return 0 2>/dev/null || exit 0
  fi
fi

echo "🔐 Setting AWS profile to 'gee-federation'..."
export AWS_PROFILE=gee-federation

echo "🔄 Assuming role ..."
CREDS=$(aws sts assume-role --role-arn "$ROLE_ARN" --role-session-name "$SESSION_NAME" --output json)

if [[ -z "$CREDS" ]]; then
  echo "❌ Failed to assume role. Make sure the role exists and is trusted."
  exit 1
fi

export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r .Credentials.AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r .Credentials.SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r .Credentials.SessionToken)
EXPIRATION=$(echo "$CREDS" | jq -r .Credentials.Expiration)

if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$EXPIRATION" ]]; then
  echo "❌ Failed to parse temporary credentials."
  exit 1
fi

echo "$EXPIRATION" > "$TMP_EXPIRY_FILE"

echo "✅ Credentials set. Temporary credentials expire at: $EXPIRATION" 