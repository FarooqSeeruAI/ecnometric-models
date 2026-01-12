#!/bin/bash
# Check if all required files for the econometric model are available on AWS instance

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="13.203.193.142"
REMOTE_DIR="~/cge_model"

echo "🔍 Checking Required Files on AWS Instance"
echo "==========================================="
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

# Check files on host
echo "📁 Checking files on HOST (${REMOTE_DIR}):"
echo "--------------------------------------------"
MISSING_HOST=()
EXISTS_HOST=()

for file in "${REQUIRED_FILES[@]}"; do
    if ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} "test -f ${REMOTE_DIR}/${file}" 2>/dev/null; then
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
    if ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} "docker exec cge-model-api test -f /app/${file}" 2>/dev/null; then
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

# Check file sizes for key files
echo ""
echo "📏 File Sizes (Key Files):"
echo "--------------------------"
KEY_FILES=("orani.model" "default.yml" "database/oranignm.xlsx" "closures/base2023.txt" "closures/pol2023.txt")

for file in "${KEY_FILES[@]}"; do
    HOST_SIZE=$(ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} "stat -f%z ${REMOTE_DIR}/${file} 2>/dev/null || echo '0'")
    CONTAINER_SIZE=$(ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} "docker exec cge-model-api stat -c%s /app/${file} 2>/dev/null || echo '0'")
    
    if [ "$HOST_SIZE" != "0" ] && [ "$HOST_SIZE" != "" ]; then
        echo "Host ${file}: $(numfmt --to=iec-i --suffix=B ${HOST_SIZE} 2>/dev/null || echo ${HOST_SIZE} bytes)"
    fi
    
    if [ "$CONTAINER_SIZE" != "0" ] && [ "$CONTAINER_SIZE" != "" ]; then
        echo "Container ${file}: $(numfmt --to=iec-i --suffix=B ${CONTAINER_SIZE} 2>/dev/null || echo ${CONTAINER_SIZE} bytes)"
    fi
done

# Final status
echo ""
if [ ${#MISSING_HOST[@]} -eq 0 ] && [ ${#MISSING_CONTAINER[@]} -eq 0 ]; then
    echo "✅ All required files are present!"
    exit 0
else
    echo "⚠️  Some files are missing. Please upload them to the instance."
    exit 1
fi
