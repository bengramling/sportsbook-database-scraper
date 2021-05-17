from datetime import date, datetime, tzinfo
from pytz import timezone
import logging
import pymysql

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#main
def main(event, context):
    now = datetime.now(timezone('US/Eastern'))
    ten_min = 60*10

    #connect to DB
    try:
        host = 'odds-db.cwlgxzudqrlz.us-east-2.rds.amazonaws.com'
        user = 'admin'
        password = 'Benbenben108'
        database = 'odds'
    
        conn = pymysql.connect(host=host, user=user, passwd=password, db=database)
        logger.info("Success: connected to database")
        cursor = conn.cursor()
    except Exception as e:
        logger.error(e)
        return

    try:
        #delete rows older than ten minutes
        threshold = round(now.timestamp())-ten_min
        cursor.execute("""DELETE FROM sites WHERE updated<=%s;""", (threshold))
        logger.info("Success: deleted rows older than 10 minutes")
    except Exception as e:
        logger.error(e)
        pass
    try:
        #delete events that have no bets associated with them
        cursor.execute("""DELETE FROM events WHERE NOT EXISTS (SELECT 1 FROM sites WHERE contest_id=event_id)""")
        logger.info("Success: deleted events with no bets associated with them")
    except Exception as e:
        logger.error(e)
    conn.commit()

                  


