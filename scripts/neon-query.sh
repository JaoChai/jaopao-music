#!/bin/bash
# Query Neon PostgreSQL via psql-compatible URL
# Usage: ./neon-query.sh "SELECT * FROM channels WHERE name = 'เจ้าเปา'"
SQL="$1"
if [ -z "$SQL" ]; then
  echo "Usage: ./neon-query.sh \"SQL QUERY\""
  exit 1
fi

curl -s -X POST "https://console.neon.tech/api/v2/projects/dawn-frost-22911856/branches/br-late-sky-aha4c0nb/sql" \
  -H "Authorization: Bearer ${NEON_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$SQL\"}" 2>/dev/null
