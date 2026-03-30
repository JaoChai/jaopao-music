#!/bin/bash
# Query Neon PostgreSQL via Python/psycopg2
# Usage: ./neon-query.sh "SELECT * FROM channels WHERE name = 'เจ้าเปา'"
# Uses connection string from env NEON_DB_URL or default jaopao-music project
#
# Connection: postgresql://neondb_owner:npg_bzaOu9p7fmyq@ep-rapid-salad-ampewq36.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require
# Project: bold-union-38769064 (jaopao-music)

SQL="$1"
if [ -z "$SQL" ]; then
  echo "Usage: ./neon-query.sh \"SQL QUERY\""
  exit 1
fi

DB_URL="${NEON_DB_URL:-postgresql://neondb_owner:npg_bzaOu9p7fmyq@ep-rapid-salad-ampewq36.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require}"

python3 -c "
import psycopg2, json, sys
conn = psycopg2.connect('$DB_URL')
cur = conn.cursor()
cur.execute(sys.argv[1])
cols = [d[0] for d in cur.description]
rows = [dict(zip(cols, row)) for row in cur.fetchall()]
print(json.dumps(rows, ensure_ascii=False, default=str))
cur.close(); conn.close()
" "$SQL"
