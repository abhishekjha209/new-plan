#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

API_URL="http://localhost:8000"
RESP_FILE=$(mktemp)

# Clean up temporary file on exit
cleanup() {
    rm -f "$RESP_FILE"
}
trap cleanup EXIT

echo -e "${BLUE}=== Starting Day 5 API Integration Test ===${NC}\n"

# 1. Health Check
echo "Testing GET /health..."
HEALTH_CODE=$(curl -s -w "%{http_code}" -o "$RESP_FILE" "$API_URL/health")
HEALTH_BODY=$(cat "$RESP_FILE")

if [ "$HEALTH_CODE" -eq 200 ]; then
    echo -e "${GREEN}✔ Health check passed: $HEALTH_BODY${NC}"
else
    echo -e "${RED}✘ Health check failed with status $HEALTH_CODE${NC}"
    exit 1
fi

# 2. Register a new user
echo -e "\nTesting POST /auth/register..."
REG_DATA='{"email":"developer@example.com","name":"Abe Developer","password":"securepassword123"}'
REG_CODE=$(curl -s -w "%{http_code}" -o "$RESP_FILE" -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d "$REG_DATA")
REG_BODY=$(cat "$RESP_FILE")

if [ "$REG_CODE" -eq 201 ]; then
    echo -e "${GREEN}✔ User registration passed (201 Created): $REG_BODY${NC}"
elif [ "$REG_CODE" -eq 400 ] && [[ "$REG_BODY" == *"already registered"* ]]; then
    echo -e "${BLUE}ℹ User already registered in this process lifecycle, continuing...${NC}"
else
    echo -e "${RED}✘ User registration failed with status $REG_CODE: $REG_BODY${NC}"
    exit 1
fi

# 3. Prevent duplicate registration
echo -e "\nTesting duplicate registration block..."
DUP_CODE=$(curl -s -w "%{http_code}" -o "$RESP_FILE" -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d "$REG_DATA")
DUP_BODY=$(cat "$RESP_FILE")

if [ "$DUP_CODE" -eq 400 ]; then
    echo -e "${GREEN}✔ Duplicate registration successfully blocked (400 Bad Request): $DUP_BODY${NC}"
else
    echo -e "${RED}✘ Duplicate registration allowed or failed with unexpected status $DUP_CODE: $DUP_BODY${NC}"
    exit 1
fi

# 4. Login
echo -e "\nTesting POST /auth/login..."
LOGIN_DATA='{"email":"developer@example.com","password":"securepassword123"}'
LOGIN_CODE=$(curl -s -w "%{http_code}" -o "$RESP_FILE" -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "$LOGIN_DATA")
LOGIN_BODY=$(cat "$RESP_FILE")

if [ "$LOGIN_CODE" -eq 200 ]; then
    echo -e "${GREEN}✔ User login passed (200 OK): $LOGIN_BODY${NC}"
else
    echo -e "${RED}✘ User login failed with status $LOGIN_CODE: $LOGIN_BODY${NC}"
    exit 1
fi

# Extract token using Python for perfect JSON parsing
TOKEN=$(echo "$LOGIN_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
if [ -z "$TOKEN" ]; then
    echo -e "${RED}✘ Failed to extract token from response!${NC}"
    exit 1
fi
echo -e "${BLUE}Extracted Session Token: $TOKEN${NC}"

# 5. GET /users/me (using token)
echo -e "\nTesting GET /users/me..."
ME_CODE=$(curl -s -w "%{http_code}" -o "$RESP_FILE" -X GET "$API_URL/users/me" \
    -H "Authorization: Bearer $TOKEN")
ME_BODY=$(cat "$RESP_FILE")

if [ "$ME_CODE" -eq 200 ]; then
    echo -e "${GREEN}✔ GET /users/me authenticated successfully (200 OK): $ME_BODY${NC}"
else
    echo -e "${RED}✘ GET /users/me failed with status $ME_CODE: $ME_BODY${NC}"
    exit 1
fi

# 6. POST /documents (Upload Document)
echo -e "\nTesting POST /documents..."
DOC_DATA='{"filename":"ai_trends_2026.txt","content":"In 2026, AI engineering is focused heavily on production reliability, observability, and cost-effective model usage."}'
DOC_CODE=$(curl -s -w "%{http_code}" -o "$RESP_FILE" -X POST "$API_URL/documents" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$DOC_DATA")
DOC_BODY=$(cat "$RESP_FILE")

if [ "$DOC_CODE" -eq 201 ]; then
    echo -e "${GREEN}✔ Document uploaded successfully (201 Created): $DOC_BODY${NC}"
else
    echo -e "${RED}✘ Document upload failed with status $DOC_CODE: $DOC_BODY${NC}"
    exit 1
fi

# Extract document ID
DOC_ID=$(echo "$DOC_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo -e "${BLUE}Uploaded Document ID: $DOC_ID${NC}"

# 7. GET /documents
echo -e "\nTesting GET /documents..."
LIST_CODE=$(curl -s -w "%{http_code}" -o "$RESP_FILE" -X GET "$API_URL/documents" \
    -H "Authorization: Bearer $TOKEN")
LIST_BODY=$(cat "$RESP_FILE")

if [ "$LIST_CODE" -eq 200 ]; then
    echo -e "${GREEN}✔ Documents listed successfully (200 OK): $LIST_BODY${NC}"
else
    echo -e "${RED}✘ Document listing failed with status $LIST_CODE: $LIST_BODY${NC}"
    exit 1
fi

# 8. POST /chat (Interactive Conversation)
echo -e "\nTesting POST /chat (Start conversation)..."
CHAT_DATA="{\"message\":\"What is the main focus of AI engineering in 2026?\",\"document_id\":$DOC_ID}"
CHAT_CODE=$(curl -s -w "%{http_code}" -o "$RESP_FILE" -X POST "$API_URL/chat" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$CHAT_DATA")
CHAT_BODY=$(cat "$RESP_FILE")

if [ "$CHAT_CODE" -eq 200 ]; then
    echo -e "${GREEN}✔ Chat responded successfully (200 OK):$NC"
    echo "$CHAT_BODY" | python3 -m json.tool
else
    echo -e "${RED}✘ Chat failed with status $CHAT_CODE: $CHAT_BODY${NC}"
    exit 1
fi

# Extract conversation ID
CONV_ID=$(echo "$CHAT_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['conversation_id'])")
echo -e "${BLUE}Conversation ID: $CONV_ID${NC}"

# 9. POST /chat with existing conversation_id
echo -e "\nTesting POST /chat (Continue conversation)..."
CHAT_CONT_DATA="{\"message\":\"Awesome! Tell me more about reliability.\",\"document_id\":$DOC_ID,\"conversation_id\":$CONV_ID}"
CHAT_CONT_CODE=$(curl -s -w "%{http_code}" -o "$RESP_FILE" -X POST "$API_URL/chat" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$CHAT_CONT_DATA")
CHAT_CONT_BODY=$(cat "$RESP_FILE")

if [ "$CHAT_CONT_CODE" -eq 200 ]; then
    echo -e "${GREEN}✔ Chat continuation responded successfully (200 OK):$NC"
    echo "$CHAT_CONT_BODY" | python3 -m json.tool
else
    echo -e "${RED}✘ Chat continuation failed with status $CHAT_CONT_CODE: $CHAT_CONT_BODY${NC}"
    exit 1
fi

echo -e "\n${GREEN}=== All Day 5 Integration Tests Passed Successfully! ===${NC}"
