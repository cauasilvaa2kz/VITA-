from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from database import init_db, get_db
from datetime import date
import csv, io

app = Flask(__name__)
app.secret_key = "vita-plus-local-dev-key"
init_db()

@app.context_processor
def inject_today():
    return {"today": date.today().isoformat()}

@app.route("/")
def index():
    db = get_db()
    today = date.today().isoformat()
    profile = db.execute("SELECT * FROM profile WHERE id=1").fetchone()
    meals = db.execute("""SELECT m.*, f.name food_name FROM meals m JOIN foods f ON f.id=m.food_id
                          WHERE m.day=? ORDER BY m.id DESC""", (today,)).fetchall()
    totals = db.execute("SELECT COALESCE(SUM(kcal),0) kcal, COALESCE(SUM(protein),0) protein, COALESCE(SUM(carbs),0) carbs, COALESCE(SUM(fat),0) fat FROM meals WHERE day=?", (today,)).fetchone()
    water = db.execute("SELECT COALESCE(SUM(amount),0) amount FROM water WHERE day=?", (today,)).fetchone()["amount"]
    workouts = db.execute("SELECT COUNT(*) n FROM workouts WHERE day=?", (today,)).fetchone()["n"]
    weights = db.execute("SELECT * FROM weights ORDER BY day, id").fetchall()
    return render_template("index.html", profile=profile, meals=meals, totals=totals, water=water, workouts=workouts, weights=weights)

@app.route("/perfil", methods=["GET", "POST"])
def profile():
    db = get_db()
    current = db.execute("SELECT * FROM profile WHERE id=1").fetchone()
    if request.method == "POST":
        try:
            name = request.form.get("name","").strip()
            age = int(request.form.get("age", 0))
            height = float(request.form.get("height", 0))
            weight = float(request.form.get("weight", 0))
            goal = request.form.get("goal","Organizar a alimentação")
            activity = request.form.get("activity","Moderado")
            preferences = request.form.get("preferences","").strip()
            restrictions = request.form.get("restrictions","").strip()
            if not name or not 1 <= age <= 120 or not 50 <= height <= 250 or not 2 <= weight <= 400:
                raise ValueError("Confira o nome, a idade, a altura e o peso informados.")
            db.execute("""INSERT INTO profile(id,name,age,height,weight,goal,activity,preferences,restrictions)
                VALUES(1,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,age=excluded.age,
                height=excluded.height,weight=excluded.weight,goal=excluded.goal,activity=excluded.activity,
                preferences=excluded.preferences,restrictions=excluded.restrictions""",
                (name,age,height,weight,goal,activity,preferences,restrictions))
            db.execute("INSERT INTO weights(day,kg) VALUES(?,?)", (date.today().isoformat(), weight))
            db.commit()
            flash("Perfil salvo com sucesso!", "success")
            return redirect(url_for("profile"))
        except (ValueError, TypeError):
            flash("Dados inválidos. Verifique os campos e tente novamente.", "error")
    return render_template("profile.html", profile=current)

@app.route("/alimentacao", methods=["GET", "POST"])
def food():
    db = get_db()
    if request.method == "POST":
        try:
            food_id = int(request.form["food_id"])
            qty = float(request.form["quantity"])
            day = request.form.get("day") or date.today().isoformat()
            kind = request.form.get("kind","Almoço")
            food = db.execute("SELECT * FROM foods WHERE id=?", (food_id,)).fetchone()
            if not food or qty <= 0 or qty > 3000:
                raise ValueError()
            factor = qty / 100
            db.execute("INSERT INTO meals(day,kind,food_id,quantity,kcal,protein,carbs,fat) VALUES(?,?,?,?,?,?,?,?)",
                       (day,kind,food_id,qty,food["kcal"]*factor,food["protein"]*factor,food["carbs"]*factor,food["fat"]*factor))
            db.commit()
            flash("Alimento registrado!", "success")
            return redirect(url_for("food", day=day))
        except (ValueError, KeyError):
            flash("Confira o alimento e a quantidade informados.", "error")
    day = request.args.get("day", date.today().isoformat())
    foods = db.execute("SELECT * FROM foods ORDER BY name").fetchall()
    meals = db.execute("SELECT m.*,f.name food_name FROM meals m JOIN foods f ON f.id=m.food_id WHERE m.day=? ORDER BY m.id DESC", (day,)).fetchall()
    totals = db.execute("SELECT COALESCE(SUM(kcal),0) kcal,COALESCE(SUM(protein),0) protein,COALESCE(SUM(carbs),0) carbs,COALESCE(SUM(fat),0) fat FROM meals WHERE day=?", (day,)).fetchone()
    return render_template("food.html", foods=foods, meals=meals, totals=totals, day=day)

@app.post("/alimentacao/excluir/<int:meal_id>")
def delete_meal(meal_id):
    db = get_db()
    db.execute("DELETE FROM meals WHERE id=?", (meal_id,))
    db.commit()
    flash("Registro excluído.", "success")
    return redirect(url_for("food"))

@app.route("/medidas", methods=["GET", "POST"])
def measures():
    db = get_db()
    profile = db.execute("SELECT * FROM profile WHERE id=1").fetchone()
    if request.method == "POST":
        try:
            kg = float(request.form["kg"])
            day = request.form.get("day") or date.today().isoformat()
            if not 2 <= kg <= 400: raise ValueError()
            db.execute("INSERT INTO weights(day,kg) VALUES(?,?)", (day,kg))
            db.commit()
            flash("Peso registrado.", "success")
            return redirect(url_for("measures"))
        except (ValueError, KeyError):
            flash("Informe um peso válido.", "error")
    weights = db.execute("SELECT * FROM weights ORDER BY day DESC,id DESC").fetchall()
    bmi = round(profile["weight"] / ((profile["height"]/100)**2), 1) if profile else None
    return render_template("measures.html", profile=profile, weights=weights, bmi=bmi)

@app.route("/rotina", methods=["GET", "POST"])
def routine():
    db = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        day = request.form.get("day") or date.today().isoformat()
        try:
            if action == "water":
                amount = int(request.form.get("amount",0))
                if not 1 <= amount <= 5000: raise ValueError()
                db.execute("INSERT INTO water(day,amount) VALUES(?,?)",(day,amount))
                flash("Consumo de água registrado.", "success")
            elif action == "workout":
                activity = request.form.get("activity","").strip()
                minutes = int(request.form.get("minutes",0))
                if not activity or not 1 <= minutes <= 600: raise ValueError()
                db.execute("INSERT INTO workouts(day,activity,minutes,notes) VALUES(?,?,?,?)",(day,activity,minutes,request.form.get("notes","").strip()))
                flash("Atividade registrada.", "success")
            elif action == "habit":
                habit = request.form.get("habit","").strip()
                if not habit: raise ValueError()
                db.execute("INSERT INTO habits(day,habit,done) VALUES(?,?,?)",(day,habit,1 if request.form.get("done") else 0))
                flash("Hábito registrado.", "success")
            db.commit()
        except (ValueError, TypeError):
            flash("Confira os dados informados.", "error")
        return redirect(url_for("routine"))
    today = date.today().isoformat()
    water_total = db.execute("SELECT COALESCE(SUM(amount),0) n FROM water WHERE day=?", (today,)).fetchone()["n"]
    waters = db.execute("SELECT day,SUM(amount) total FROM water GROUP BY day ORDER BY day DESC LIMIT 7").fetchall()
    workouts = db.execute("SELECT * FROM workouts ORDER BY day DESC,id DESC LIMIT 20").fetchall()
    habits = db.execute("SELECT * FROM habits ORDER BY day DESC,id DESC LIMIT 30").fetchall()
    return render_template("routine.html", water_total=water_total, waters=waters, workouts=workouts, habits=habits)

@app.route("/planejamento", methods=["GET", "POST"])
def planning():
    db = get_db()
    if request.method == "POST":
        day = request.form.get("day") or date.today().isoformat()
        kind = request.form.get("kind","Almoço")
        description = request.form.get("description","").strip()
        if description:
            db.execute("INSERT INTO plans(day,kind,description,notes) VALUES(?,?,?,?)",(day,kind,description,request.form.get("notes","").strip()))
            db.commit()
            flash("Refeição adicionada ao planejamento.", "success")
        else: flash("Descreva a refeição planejada.", "error")
        return redirect(url_for("planning"))
    plans = db.execute("SELECT * FROM plans ORDER BY day,id").fetchall()
    return render_template("planning.html", plans=plans)

@app.post("/planejamento/excluir/<int:plan_id>")
def delete_plan(plan_id):
    db = get_db()
    db.execute("DELETE FROM plans WHERE id=?", (plan_id,))
    db.commit()
    flash("Item removido do planejamento.", "success")
    return redirect(url_for("planning"))

@app.route("/relatorios")
def reports():
    db = get_db()
    start = request.args.get("start", date.today().replace(day=1).isoformat())
    end = request.args.get("end", date.today().isoformat())
    meals = db.execute("""SELECT m.day,f.name food_name,m.kind,m.quantity,m.kcal,m.protein,m.carbs,m.fat
      FROM meals m JOIN foods f ON f.id=m.food_id WHERE m.day BETWEEN ? AND ? ORDER BY m.day""",(start,end)).fetchall()
    daily = db.execute("SELECT day,ROUND(SUM(kcal),1) kcal FROM meals WHERE day BETWEEN ? AND ? GROUP BY day ORDER BY day",(start,end)).fetchall()
    if request.args.get("export") == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Data","Alimento","Refeição","Quantidade (g)","Calorias (kcal)","Proteínas (g)","Carboidratos (g)","Gorduras (g)"])
        for r in meals: writer.writerow([r["day"],r["food_name"],r["kind"],r["quantity"],round(r["kcal"],1),round(r["protein"],1),round(r["carbs"],1),round(r["fat"],1)])
        return Response("\ufeff"+output.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=vita_plus_relatorio.csv"})
    return render_template("reports.html", meals=meals, daily=daily, start=start, end=end)

if __name__ == "__main__":
    app.run(debug=True)
