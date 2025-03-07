import sqlite3
from excel_utils import load_wrestlers_from_excel, load_teams_from_excel, load_teams_wrestlers_from_excel, load_all_americans_from_excel
from models import Wrestler, Team
from scoring import get_score_dictionary

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """Create tables for Wrestlers, Teams, and TeamWrestlers."""
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
        
        sql_create_team_wrestlers_table = """
        CREATE TABLE IF NOT EXISTS team_wrestlers (
            team_id INTEGER NOT NULL,
            wrestler_id INTEGER NOT NULL,
            FOREIGN KEY (team_id) REFERENCES teams (id),
            FOREIGN KEY (wrestler_id) REFERENCES wrestlers (id),
            PRIMARY KEY (team_id, wrestler_id)
        );
        """
        
        cursor = conn.cursor()
        cursor.execute(sql_create_teams_table)
        cursor.execute(sql_create_wrestlers_table)
        cursor.execute(sql_create_team_wrestlers_table)
    except sqlite3.Error as e:
        print(e)

def add_wrestler(conn, wrestler):
    """Add a new wrestler to the wrestlers table."""
    sql = ''' INSERT INTO wrestlers(name, seed, weight_class, score, all_american, medal, finalist, team_id)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (wrestler.name, wrestler.seed, wrestler.weight_class, wrestler.score, wrestler.all_american, wrestler.medal, wrestler.finalist, None))
    conn.commit()
    return cur.lastrowid

def get_wrestler_id(conn, wrestler_name):
    """Get the wrestler ID by name."""
    sql = ''' SELECT id FROM wrestlers WHERE name = ? '''
    cur = conn.cursor()
    cur.execute(sql, (wrestler_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    return None

def update_wrestler_all_american(conn, wrestler_id, all_american):
    """Update the all_american status of a wrestler in the wrestlers table."""
    sql = ''' UPDATE wrestlers SET all_american = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (all_american, wrestler_id))
    conn.commit()

def update_wrestler_finalist(conn, wrestler_id, finalist):
    """Update the finalist status of a wrestler in the wrestlers table."""
    sql = ''' UPDATE wrestlers SET finalist = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (finalist, wrestler_id))
    conn.commit()

def update_wrestler_score(conn, wrestler_id, score):
    """Update the score of a wrestler in the wrestlers table."""
    sql = ''' UPDATE wrestlers SET score = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (score, wrestler_id))
    conn.commit()

def add_team(conn, team):
    """Add a new team to the teams table."""
    sql = ''' INSERT INTO teams(name, score, tie_breaker_team, tie_breaker_score)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (team.name, team.score, team.tie_breaker_team, team.tie_breaker_score))
    conn.commit()
    return cur.lastrowid

def update_team_score(conn, team_id, score):
    """Update the score of a team in the teams table."""
    sql = ''' UPDATE teams SET score = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (score, team_id))
    conn.commit()

def add_wrestler_to_team(conn, team_id, wrestler_id):
    """Add a wrestler to a team in the team_wrestlers table."""
    sql = ''' INSERT INTO team_wrestlers(team_id, wrestler_id)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (team_id, wrestler_id))
    conn.commit()

def query_teams(database):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM teams")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()

def main():
    database = "wrestling.db"
    
    # Create a database connection
    conn = create_connection(database)
    
    # Create tables
    if conn is not None:
        create_tables(conn)

        # Load wrestlers from Excel
        wrestlers_file_path = "wrestlers.xlsx"
        wrestlers = load_wrestlers_from_excel(wrestlers_file_path)

        # Add wrestlers to the database
        for wrestler in wrestlers:
            add_wrestler(conn, wrestler)

        # Load All Americans and finalists from Excel
        all_americans_file_path = "all_americans.xlsx"
        all_americans, finalists, medals = load_all_americans_from_excel(all_americans_file_path)

        # Update All American status in the database
        for wrestler_name in all_americans:
            wrestler_id = get_wrestler_id(conn, wrestler_name)
            if wrestler_id:
                update_wrestler_all_american(conn, wrestler_id, True)

        # Update finalist status in the database
        for wrestler_name in finalists:
            wrestler_id = get_wrestler_id(conn, wrestler_name)
            if wrestler_id:
                update_wrestler_finalist(conn, wrestler_id, True)

        # Load teams from Excel
        teams_file_path = "teams.xlsx"
        teams = load_teams_from_excel(teams_file_path)

        # Add teams to the database
        team_ids = {}
        for team in teams:
            team_id = add_team(conn, team)
            team_ids[team.name] = team_id

        # Get the score dictionary
        score_dict = get_score_dictionary()

        # Update wrestler scores in the database
        for wrestler_name, score in score_dict.items():
            wrestler_id = get_wrestler_id(conn, wrestler_name)
            if wrestler_id:
                update_wrestler_score(conn, wrestler_id, score)

        # Load wrestlers for each team from a separate file
        teams_wrestlers_file_path = "teams_wrestlers.xlsx"
        teams_wrestlers = load_teams_wrestlers_from_excel(teams_wrestlers_file_path)
        for team_name, wrestlers in teams_wrestlers.items():
            team_id = team_ids.get(team_name)
            if team_id:
                team_score = 0
                for wrestler in wrestlers:
                    wrestler_id = get_wrestler_id(conn, wrestler.name)
                    if not wrestler_id:
                        wrestler_id = add_wrestler(conn, wrestler)
                    add_wrestler_to_team(conn, team_id, wrestler_id)
                    team_score += wrestler.score
                update_team_score(conn, team_id, team_score)

        
        conn.commit()
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
    query_teams("wrestling.db")