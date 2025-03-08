from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

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
    return render_template('index.html', teams=teams_with_stats)

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

if __name__ == '__main__':
    app.run(debug=True)