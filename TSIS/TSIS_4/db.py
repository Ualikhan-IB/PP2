# db.py
import psycopg2
from psycopg2 import sql, extras
from datetime import datetime
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = None
        try:
            self.connect()
            self.create_tables()
        except Exception as e:
            print(f"Database not available: {e}")
            self.conn = None
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            self.conn.autocommit = True
        except Exception as e:
            print(f"Connection error: {e}")
            self.conn = None
    
    def create_tables(self):
        if not self.conn:
            return
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
                    score INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT NOW()
                )
            """)
    
    def get_or_create_player(self, username):
        if not self.conn:
            return None
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
                return cur.fetchone()[0]
    
    def save_game_result(self, player_id, score, level_reached):
        if not self.conn or player_id is None:
            return
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO game_sessions (player_id, score, level_reached)
                VALUES (%s, %s, %s)
            """, (player_id, score, level_reached))
    
    def get_top_scores(self, limit=10):
        if not self.conn:
            return []
        with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute("""
                SELECT p.username, gs.score, gs.level_reached, gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()
    
    def get_personal_best(self, player_id):
        if not self.conn or player_id is None:
            return 0
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(MAX(score), 0) FROM game_sessions
                WHERE player_id = %s
            """, (player_id,))
            return cur.fetchone()[0]
    
    def close(self):
        if self.conn:
            self.conn.close()

db = Database()