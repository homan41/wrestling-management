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
    conn.close()
    return render_template('index.html', teams=teams)

@app.route('/team/<int:team_id>')
def team(team_id):
    conn = create_connection('wrestling.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    team = cur.fetchone()
    cur.execute("SELECT * FROM wrestlers WHERE team_id = ?", (team_id,))
    wrestlers = cur.fetchall()
    conn.close()
    return render_template('team.html', team=team, wrestlers=wrestlers)

if __name__ == '__main__':
    app.run(debug=True)