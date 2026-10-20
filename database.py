import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "vita_plus.db"

FOODS = [
    ("Arroz branco cozido",130,2.5,28.2,0.3),("Feijão carioca cozido",76,4.8,13.6,0.5),
    ("Peito de frango grelhado",159,32,0,2.5),("Ovo cozido",146,13.3,0.6,9.5),
    ("Carne bovina magra grelhada",219,35,0,7.5),("Leite integral",61,3.2,4.7,3.3),
    ("Banana",89,1.1,22.8,0.3),("Aveia",394,13.9,66.6,8.5),("Pão francês",300,8,58.6,3.1),
    ("Batata cozida",87,1.9,20.1,0.1),("Macarrão cozido",158,5.8,30.9,0.9),("Tomate",18,0.9,3.9,0.2),
    ("Alface",15,1.4,2.9,0.2),("Iogurte natural integral",61,3.5,4.7,3.3),("Maçã com casca",56,0.3,15.2,0.2),
    ("Queijo minas frescal",264,17.4,3.2,20.2),("Lentilha cozida",93,6.3,16.3,0.5),("Brócolis cozido",25,2.1,4.4,0.5)
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS profile(id INTEGER PRIMARY KEY CHECK(id=1),name TEXT NOT NULL,age INTEGER NOT NULL,height REAL NOT NULL,weight REAL NOT NULL,goal TEXT NOT NULL,activity TEXT NOT NULL,preferences TEXT,restrictions TEXT);
        CREATE TABLE IF NOT EXISTS foods(id INTEGER PRIMARY KEY,name TEXT UNIQUE,kcal REAL,protein REAL,carbs REAL,fat REAL,source TEXT);
        CREATE TABLE IF NOT EXISTS meals(id INTEGER PRIMARY KEY,day TEXT,kind TEXT,food_id INTEGER REFERENCES foods(id),quantity REAL,kcal REAL,protein REAL,carbs REAL,fat REAL);
        CREATE TABLE IF NOT EXISTS weights(id INTEGER PRIMARY KEY,day TEXT,kg REAL);
        CREATE TABLE IF NOT EXISTS water(id INTEGER PRIMARY KEY,day TEXT,amount INTEGER);
        CREATE TABLE IF NOT EXISTS workouts(id INTEGER PRIMARY KEY,day TEXT,activity TEXT,minutes INTEGER,notes TEXT);
        CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY,day TEXT,habit TEXT,done INTEGER);
        CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY,day TEXT,kind TEXT,description TEXT,notes TEXT);
        """)
        n = db.execute("SELECT COUNT(*) FROM foods").fetchone()[0]
        if n == 0:
            db.executemany("INSERT INTO foods(name,kcal,protein,carbs,fat,source) VALUES(?,?,?,?,?,'Base educativa local; valores aproximados por 100 g')", FOODS)
        db.commit()
