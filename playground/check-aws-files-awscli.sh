#!/bin/bash
# Check required files on AWS instance using AWS CLI and SSM

INSTANCE_ID="i-045456211a080a8bc"
AWS_REGION="ap-south-1"
REMOTE_DIR="~/cge_model"

echo "🔍 Checking Required Files on AWS Instance (via AWS CLI)"
echo "========================================================="
echo ""

# Required files list
REQUIRED_FILES=(
    "orani.model"
    "default.yml"
    "database/oranignm.xlsx"
    "closures/base2023.txt"
    "closures/base2024.txt"
    "closures/base2025.txt"
    "closures/base2026.txt"
    "closures/base2027.txt"
    "closures/base2028.txt"
    "closures/base2029.txt"
    "closures/base2030.txt"
    "closures/base2031.txt"
    "closures/base2032.txt"
    "closures/base2033.txt"
    "closures/base2034.txt"
    "closures/base2035.txt"
    "closures/base2036.txt"
    "closures/base2037.txt"
    "closures/base2038.txt"
    "closures/base2039.txt"
    "closures/base2040.txt"
    "closures/pol2023.txt"
    "closures/pol2024.txt"
    "closures/pol2025.txt"
    "closures/pol2026.txt"
    "closures/pol2027.txt"
    "closures/pol2028.txt"
    "closures/pol2029.txt"
    "closures/pol2030.txt"
    "closures/pol2031.txt"
    "closures/pol2032.txt"
    "closures/pol2033.txt"
    "closures/pol2034.txt"
    "closures/pol2035.txt"
    "closures/pol2036.txt"
    "closures/pol2037.txt"
    "closures/pol2038.txt"
    "closures/pol2039.txt"
    "closures/pol2040.txt"
)

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed"
    exit 1
fi

# Check SSM status
SSM_STATUS=$(aws ssm describe-instance-information --filters "Key=InstanceIds,Values=${INSTANCE_ID}" --region ${AWS_REGION} --query 'InstanceInformationList[0].PingStatus' --output text 2>/dev/null)

if [ "$SSM_STATUS" != "Online" ]; then
    echo "❌ SSM Agent is not Online (Status: ${SSM_STATUS:-Not found})"
    echo ""
    echo "Cannot check files without SSM. Please:"
    echo "1. Enable SSM on the instance (attach IAM role with SSM permissions)"
    echo "2. Or run check-aws-files.sh via SSH from your location"
    exit 1
fi

echo "✅ SSM Agent is Online"
echo ""

# Function to check file via SSM
check_file_ssm() {
    local file_path=$1
    local location=$2
    local check_cmd
    
    if [ "$location" = "host" ]; then
        check_cmd="test -f ${REMOTE_DIR}/${file_path} && echo EXISTS || echo MISSING"
    else
        check_cmd="docker exec cge-model-api test -f /app/${file_path} && echo EXISTS || echo MISSING"
    fi
    
    COMMAND_ID=$(aws ssm send-command --instance-ids ${INSTANCE_ID} --region ${AWS_REGION} --document-name "AWS-RunShellScript" --parameters "commands=[\"${check_cmd}\"]" --query 'Command.CommandId' --output text)
    sleep 2
    aws ssm get-command-invocation --command-id ${COMMAND_ID} --instance-id ${INSTANCE_ID} --region ${AWS_REGION} --query 'StandardOutputContent' --output text 2>/dev/null | grep -q "EXISTS" && echo "EXISTS" || echo "MISSING"
}

# Check files on host
echo "📁 Checking files on HOST (${REMOTE_DIR}):"
echo "--------------------------------------------"
MISSING_HOST=()
EXISTS_HOST=()

for file in "${REQUIRED_FILES[@]}"; do
    STATUS=$(check_file_ssm "$file" "host")
    if [ "$STATUS" = "EXISTS" ]; then
        EXISTS_HOST+=("$file")
        echo "✅ ${file}"
    else
        MISSING_HOST+=("$file")
        echo "❌ ${file} - MISSING"
    fi
done

echo ""
echo "📦 Checking files in DOCKER CONTAINER (/app):"
echo "--------------------------------------------"
MISSING_CONTAINER=()
EXISTS_CONTAINER=()

for file in "${REQUIRED_FILES[@]}"; do
    STATUS=$(check_file_ssm "$file" "container")
    if [ "$STATUS" = "EXISTS" ]; then
        EXISTS_CONTAINER+=("$file")
        echo "✅ ${file}"
    else
        MISSING_CONTAINER+=("$file")
        echo "❌ ${file} - MISSING"
    fi
done

# Summary
echo ""
echo "📊 SUMMARY"
echo "=========="
echo ""
echo "Host Files:"
echo "  ✅ Found: ${#EXISTS_HOST[@]} / ${#REQUIRED_FILES[@]}"
echo "  ❌ Missing: ${#MISSING_HOST[@]} / ${#REQUIRED_FILES[@]}"

if [ ${#MISSING_HOST[@]} -gt 0 ]; then
    echo ""
    echo "Missing files on HOST:"
    for file in "${MISSING_HOST[@]}"; do
        echo "  - ${file}"
    done
fi

echo ""
echo "Container Files:"
echo "  ✅ Found: ${#EXISTS_CONTAINER[@]} / ${#REQUIRED_FILES[@]}"
echo "  ❌ Missing: ${#MISSING_CONTAINER[@]} / ${#REQUIRED_FILES[@]}"

if [ ${#MISSING_CONTAINER[@]} -gt 0 ]; then
    echo ""
    echo "Missing files in CONTAINER:"
    for file in "${MISSING_CONTAINER[@]}"; do
        echo "  - ${file}"
    done
fi

# Final status
echo ""
if [ ${#MISSING_HOST[@]} -eq 0 ] && [ ${#MISSING_CONTAINER[@]} -eq 0 ]; then
    echo "✅ All required files are present!"
    exit 0
else
    echo "⚠️  Some files are missing. Please upload them to the instance."
    exit 1
fi
