from flask import Flask, render_template
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from excel_utils import load_wrestlers_from_excel, load_teams_from_excel, load_teams_wrestlers_from_excel, load_all_americans_from_excel
from scoring_two import get_table_from_web, get_score_dictionary_two

app = Flask(__name__)

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def update_wrestler_scores():
    """Update the scores of wrestlers."""
    conn = create_connection('wrestling.db')
    cur = conn.cursor()
    # Add your logic to update wrestler scores here
    # Example: cur.execute("UPDATE wrestlers SET score = ? WHERE id = ?", (new_score, wrestler_id))
    conn.commit()
    conn.close()
    print("Wrestler scores updated")

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

def update_wrestler_medal(conn, wrestler_id, medal):
    """Update the medal of a wrestler in the wrestlers table."""
    sql = ''' UPDATE wrestlers SET medal = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (medal, wrestler_id))
    conn.commit()

def update_wrestler_score(conn, wrestler_id, score):
    """Update the score of a wrestler in the wrestlers table."""
    sql = ''' UPDATE wrestlers SET score = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (score, wrestler_id))
    conn.commit()

def update_scoring():
    database = "wrestling.db"
    
    # Create a database connection
    conn = create_connection(database)
    
    # Create tables if they do not exist
    if conn is not None:
        # Load All Americans, finalists, and medals from Excel
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

        # Update medal status in the database
        for wrestler_name, medal in medals.items():
            wrestler_id = get_wrestler_id(conn, wrestler_name)
            if wrestler_id:
                update_wrestler_medal(conn, wrestler_id, medal)

        # Get the score dictionary
        score_dict = get_score_dictionary_two()

        # Update wrestler scores in the database
        for wrestler_name, score in score_dict.items():
            wrestler_id = get_wrestler_id(conn, wrestler_name)
            if wrestler_id:
                update_wrestler_score(conn, wrestler_id, score)

        update_team_scores(conn)

    print("Wrestling Scores Updated")

def update_team_scores(conn):
    """Update the score of each team based on the sum of their wrestlers' scores."""
    cur = conn.cursor()

    # Get all teams
    cur.execute("SELECT id FROM teams")
    teams = cur.fetchall()

    for team in teams:
        team_id = team[0]

        # Calculate the sum of all wrestlers' scores for the team
        cur.execute("SELECT SUM(score) FROM wrestlers INNER JOIN team_wrestlers ON wrestlers.id = team_wrestlers.wrestler_id WHERE team_wrestlers.team_id = ?", (team_id,))
        team_score = cur.fetchone()[0] or 0


        # Update the team's score
        cur.execute("UPDATE teams SET score = ? WHERE id = ?", (team_score, team_id))

    conn.commit()

@app.route('/')
def index():
    conn = create_connection('wrestling.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM teams ORDER BY score DESC")
    teams = cur.fetchall()

    teams_with_stats = []
    for team in teams:
        team_id = team[0]
        
        # Get wrestler IDs for the team from the team_wrestlers table
        cur.execute("SELECT wrestler_id FROM team_wrestlers WHERE team_id = ?", (team_id,))
        wrestler_ids = cur.fetchall()
        
        total_all_americans = 0
        total_finalists = 0
        for wrestler_id in wrestler_ids:
            cur.execute("SELECT all_american, finalist FROM wrestlers WHERE id = ?", (wrestler_id[0],))
            wrestler = cur.fetchone()
            if wrestler[0]:
                total_all_americans += 1
            if wrestler[1]:
                total_finalists += 1
        
        teams_with_stats.append((team, total_all_americans, total_finalists))
    
    conn.close()
    
    # Get the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template('index.html', teams=teams_with_stats, current_time=current_time)

@app.route('/team/<int:team_id>')
def team(team_id):
    conn = create_connection('wrestling.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    team = cur.fetchone()
    
    # Get wrestler IDs for the team from the team_wrestlers table
    cur.execute("SELECT wrestler_id FROM team_wrestlers WHERE team_id = ?", (team_id,))
    wrestler_ids = cur.fetchall()
    
    wrestlers = []
    for wrestler_id in wrestler_ids:
        cur.execute("SELECT * FROM wrestlers WHERE id = ?", (wrestler_id[0],))
        wrestler = cur.fetchone()
        wrestlers.append(wrestler)
    
    # Sort wrestlers: first ten seeded between 1 and 8 by weight class, remaining by seed
    first_ten_sorted = sorted([w for w in wrestlers if w[2] <= 8], key=lambda x: x[3])
    remaining_sorted = sorted([w for w in wrestlers if w[2] > 8], key=lambda x: x[2])
    wrestlers_sorted = first_ten_sorted + remaining_sorted
    
    # Calculate the total number of All Americans and finalists
    total_all_americans = sum(1 for wrestler in wrestlers_sorted if wrestler[5])
    total_finalists = sum(1 for wrestler in wrestlers_sorted if wrestler[7])
    
    conn.close()
    return render_template('team.html', team=team, wrestlers=wrestlers_sorted, total_all_americans=total_all_americans, total_finalists=total_finalists)

@app.route('/wrestlers_by_seed')
def wrestlers_by_seed():
    conn = create_connection('wrestling.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM wrestlers ORDER BY seed")
    wrestlers = cur.fetchall()
    conn.close()
    return render_template('wrestlers_by_seed.html', wrestlers=wrestlers)

@app.route('/wrestlers_by_weight')
def wrestlers_by_weight():
    conn = create_connection('wrestling.db')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT weight_class FROM wrestlers ORDER BY weight_class")
    weight_classes = cur.fetchall()
    wrestlers_by_weight = {}
    for weight_class in weight_classes:
        cur.execute("SELECT * FROM wrestlers WHERE weight_class = ? ORDER BY seed", (weight_class[0],))
        wrestlers_by_weight[weight_class[0]] = cur.fetchall()
    conn.close()
    return render_template('wrestlers_by_weight.html', wrestlers_by_weight=wrestlers_by_weight)

@app.route('/wrestlers_by_picks')
def wrestlers_by_picks():
    conn = create_connection('wrestling.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM wrestlers WHERE number_of_times_picked > 0 ORDER BY number_of_times_picked DESC")
    wrestlers = cur.fetchall()
    conn.close()
    return render_template('wrestlers_by_picks.html', wrestlers=wrestlers)

@app.route('/info')
def info():
    return render_template('info.html')

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_scoring, trigger="interval", minutes=10)
    scheduler.start()
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()