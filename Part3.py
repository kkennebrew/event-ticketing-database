'''
Before you can run this code, please do the following:
    Fill up the information in line 23 below "connStr = "host='cmpstudb-01.cmp.uea.ac.uk' dbname= '' user='' password = " + pw"
    using the Russell Smith's provided credentials', add your password in the pw.txt file.
    
    Get connected to VPN (Details on installing this can be found at: https://supportwiki.cmp.uea.ac.uk/public/globalprotect) if you are running this code from an off-campus location.
    
    Get the server running in https://pgadmin.cmp.uea.ac.uk/ by log into the server. 
    
'''
# ------------------- Ignore Warning -------------------

import warnings
warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy connectable",
    category=UserWarning
)


import psycopg2
import pandas as pd

# ------------------- Utility Functions -------------------
def getConn():
    pwFile = open("pw.txt", "r")
    pw = pwFile.read().strip()
    pwFile.close()
    connStr = "host='cmpstudb-01.cmp.uea.ac.uk' dbname='dym25feu' user='dym25feu' password=" + pw
    conn = psycopg2.connect(connStr)
    return conn

def clearOutput():
    with open("output.txt", "w") as f:
        f.write('')

def writeOutput(text):
    print (text)
    with open("output.txt", "a") as f:
        f.write(text + "\n")

# ------------------- Main Program -------------------
try:
    conn = getConn()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('SET SEARCH_PATH TO "Assessment_1", public;')

    clearOutput()
    with open("input.txt", "r") as infile:
        for line in infile:
            line = line.strip()
            if not line: continue
            task = line[0]
            writeOutput(f"TASK {task}")
            try:
                if task == 'A':  # Insert spectator
                    _, sno, sname, semail = line.split("#")
                    sql = "INSERT INTO spectator (sno, sname, semail) VALUES (%s, %s, %s)"
                    cur.execute(sql, (sno, sname, semail))
                    writeOutput("Spectator inserted successfully.")

                elif task == 'B':  # Insert event
                    _, ecode, edesc, elocation, edate, etime, emax = line.split("#")
                    sql = """INSERT INTO event (ecode, edesc, elocation, edate, etime, emax)
                             VALUES (%s, %s, %s, %s, %s, %s)"""
                    cur.execute(sql, (ecode, edesc, elocation, edate, etime, emax))
                    writeOutput("Event inserted successfully.")
                    
                elif task == 'E':  # Issue ticket
                    _, ecode, sno = line.split("#")
                    cur.execute("SELECT COALESCE(MAX(tno), 0) + 1 FROM ticket")
                    next_tno = cur.fetchone()[0]
                    sql = "INSERT INTO ticket (tno, ecode, sno) VALUES (%s, %s, %s)"
                    cur.execute(sql, (next_tno, ecode, sno))
                    writeOutput(f"Ticket {next_tno} issued successfully.")

                elif task == 'F':  # Travel query
                    sql = """SELECT elocation, edate, COUNT(DISTINCT sno) AS spectators
                             FROM event e JOIN ticket t ON e.ecode = t.ecode
                             WHERE t.tno NOT IN (SELECT tno FROM cancel)
                             GROUP BY elocation, edate"""
                    df = pd.read_sql_query(sql, conn)
                    writeOutput(df.to_string())

                elif task == 'G':  # Total tickets per event
                    sql = """SELECT edesc, COUNT(t.tno) AS total_tickets
                             FROM event e LEFT JOIN ticket t ON e.ecode = t.ecode
                             GROUP BY edesc ORDER BY edesc"""
                    df = pd.read_sql_query(sql, conn)
                    writeOutput(df.to_string())
                    
                elif task == 'H':  # Tickets for a given event
                    _, ecode = line.split("#")
                    sql = """SELECT edesc, COUNT(t.tno) AS total_tickets
                             FROM event e LEFT JOIN ticket t ON e.ecode = t.ecode
                             WHERE e.ecode = %s GROUP BY edesc"""
                    df = pd.read_sql_query(sql, conn, params=(ecode,))
                    writeOutput(df.to_string())


                elif task == 'I':  # Schedule for spectator
                    _, sno = line.split("#")
                    sql = """SELECT s.sname, e.edate, e.elocation, e.etime, e.edesc
                             FROM spectator s JOIN ticket t ON s.sno = t.sno
                             JOIN event e ON t.ecode = e.ecode
                             WHERE s.sno = %s"""
                    df = pd.read_sql_query(sql, conn, params=(sno,))
                    writeOutput(df.to_string())
                    
                elif task == 'J':  # Ticket details
                    _, tno = line.split("#")
                    sql = """SELECT s.sname, t.ecode,
                             CASE WHEN t.tno IN (SELECT tno FROM cancel) THEN 'Cancelled' ELSE 'Valid' END AS status
                             FROM ticket t JOIN spectator s ON t.sno = s.sno
                             WHERE t.tno = %s"""
                    df = pd.read_sql_query(sql, conn, params=(tno,))
                    writeOutput(df.to_string())

                    
                elif task == 'D':  # Delete event
                    _, ecode = line.split("#")
                    sql = """DELETE FROM event WHERE ecode = %s
                            AND ecode NOT IN (SELECT ecode FROM ticket)"""
                    cur.execute(sql, (ecode,))
                    if cur.rowcount == 0:
                        writeOutput(f"No event {ecode} deleted (tickets exist or event does not exist)")
                    else:
                        writeOutput(f"Event {ecode} deleted successfully")


                elif task == 'K':  # Cancelled tickets for event
                    _, ecode = line.split("#")
                    sql = "SELECT * FROM cancel WHERE ecode = %s"
                    df = pd.read_sql_query(sql, conn, params=(ecode,))
                    if df.empty:
                        writeOutput(f"No cancelled tickets for event {ecode}")
                    else:
                        writeOutput(df.to_string(index=False))

                elif task == 'C':  # Delete spectator
                    _, sno = line.split("#")
                    sql = "DELETE FROM spectator WHERE sno = %s"
                    cur.execute(sql, (sno,))
                    if cur.rowcount == 0:
                        writeOutput(f"No spectator {sno} deleted (tickets exist or spectator does not exist)")
                    else:
                        writeOutput(f"Spectator {sno} deleted successfully")
                        
                elif task == 'L':  # Empty tables
                    cur.execute("TRUNCATE ticket, cancel, spectator, event CASCADE")
                    writeOutput("All tables emptied.")

                elif task == 'X':  # Exit
                    writeOutput("Exit program!")
                    break

            except Exception as e:
                writeOutput(f"Error: {str(e)}")
                
        print("Success")

except Exception as e:
    print("Connection error:", e)
    
