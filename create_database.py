import sqlite3

conn = sqlite3.connect("telemetry_results.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS benchmark_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    pattern TEXT,
    language TEXT,
    messages INTEGER,
    execution_time_ms REAL,
    average_power_w REAL,
    energy_j REAL
)
""")

conn.commit()
conn.close()

print("Database created successfully.")
