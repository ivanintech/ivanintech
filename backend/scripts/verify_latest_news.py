import sqlite3

def check_results():
    conn = sqlite3.connect('ivanintech.db')
    c = conn.cursor()
    
    print("--- RECENT NEWS ITEMS ---")
    c.execute("SELECT title, sourceName, publishedAt FROM news_items ORDER BY publishedAt DESC LIMIT 20")
    rows = c.fetchall()
    for row in rows:
        print(f"Source: {row[1]} | Title: {row[0]} | Date: {row[2]}")

if __name__ == "__main__":
    check_results()
