import sqlite3

conn = sqlite3.connect('odds.db')
cursor = conn.cursor()

command1 = """CREATE TABLE IF NOT EXISTS events
(
    contest_id INTEGER PRIMARY KEY, 
    contenders TEXT NOT NULL
)"""
cursor.execute(command1)

command2 = """CREATE TABLE IF NOT EXISTS sites
(
    site_id INTEGER NOT NULL,
    site_name TEXT NOT NULL,
    favorite TEXT NOT NULL,
    fav_odds INTEGER NOT NULL,
    underdog TEXT NOT NULL,
    under_odds INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    updated INTEGER NOT NULL,
    updated_clean TEXT,
    FOREIGN KEY(event_id) REFERENCES events(contest_id),
    PRIMARY KEY(event_id, site_id)
)"""
cursor.execute(command2)