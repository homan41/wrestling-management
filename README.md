# Wrestling Management Project

This project is designed to manage wrestlers and teams using an SQLite database. It provides functionalities to add, update, and query information about wrestlers and teams, including their attributes such as name, seed, team score, tie breaker team, and tie breaker score.

## Project Structure

```
wrestling-management
├── src
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── main.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd wrestling-management
   ```

2. **Install dependencies**:
   Make sure you have Python installed. Then, install the required packages using:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   You can start the application by running:
   ```
   python src/main.py
   ```

## Database Schema

### Wrestler
- **name**: The name of the wrestler (string).
- **seed**: The seed number of the wrestler (integer).
- **team_score**: The score of the team the wrestler belongs to (integer).
- **tie_breaker_team**: The team used for tie-breaking (string).
- **tie_breaker_score**: The score used for tie-breaking (integer).

### Team
- **name**: The name of the team (string).
- **score**: The total score of the team (integer).

## Usage Examples

- To add a new wrestler, use the function provided in `main.py`.
- To query wrestlers or teams, utilize the database functions defined in `database.py`.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.