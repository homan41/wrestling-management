import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """Create tables for Wrestlers and Teams."""
    try:
        sql_create_wrestlers_table = """
        CREATE TABLE IF NOT EXISTS wrestlers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            seed INTEGER,
            weight_class TEXT,
            score INTEGER NOT NULL DEFAULT 0,
            all_american BOOLEAN NOT NULL DEFAULT 0,
            medal INTEGER NOT NULL DEFAULT 0,
            finalist BOOLEAN NOT NULL DEFAULT 0,
            number_of_times_picked INTEGER NOT NULL DEFAULT 0,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams (id)
        );
        """

        sql_create_teams_table = """
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER,
            tie_breaker_team TEXT,
            tie_breaker_score INTEGER
        );
        """

        cursor = conn.cursor()
        cursor.execute(sql_create_teams_table)
        cursor.execute(sql_create_wrestlers_table)
    except sqlite3.Error as e:
        print(e)

def main():
    database = "wrestling.db"

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()