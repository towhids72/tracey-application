-- Create the main databases
CREATE DATABASE tracey_db;
CREATE DATABASE test_tracey_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tracey_db TO "postgres";
GRANT ALL PRIVILEGES ON DATABASE test_tracey_db TO "postgres";