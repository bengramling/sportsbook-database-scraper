import sqlite3
import pandas as pd

conn = sqlite3.connect('odds.db')
cursor = conn.cursor()

# cursor.execute('DROP TABLE sites')
# cursor.execute('DROP TABLE events')

# cursor.execute('SELECT * FROM events WHERE contest_id=?',(12345,))
# #if event is not in database, insert it
# if cursor.fetchall() == []:
#     cursor.execute('INSERT INTO events VALUES (?,?)',(12345,"team1:team2"))
# #otherwise add odd to database
# cursor.execute('INSERT INTO sites VALUES (?,?,?,?,?,?,?)',(
#     1,
#     'BetPop',
#     'team1',
#     -110,
#     'team2',
#     110,
#     12345,
# ))

print(pd.read_sql_query("SELECT * FROM events", conn))
print("-----------------------------")
print(pd.read_sql_query("SELECT favorite, fav_odds, underdog, under_odds, event_id, updated_clean FROM sites", conn))