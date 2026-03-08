from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dental"
    )


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# PROBLEM EXPLORER
@app.route("/problems")
def problems():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM dental_problems")
    problems = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("problems.html", problems=problems)


# PROBLEM DETAIL PAGE
@app.route("/problem/<int:id>")
def problem_detail(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM dental_problems WHERE id=%s",
        (id,)
    )

    problem = cursor.fetchone()

    return render_template(
        "problem_detail.html",
        problem=problem
    )


# SYMPTOM CHECKER
@app.route("/symptom-checker", methods=["GET","POST"])
def symptom_checker():

    if request.method == "POST":

        symptoms = request.form.getlist("symptoms")

        # If nothing selected
        if not symptoms:
            return render_template("result.html", results=[])

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM dental_problems WHERE "

        conditions = []
        values = []

        for s in symptoms:
            conditions.append("symptoms LIKE %s")
            values.append("%" + s + "%")

        query += " OR ".join(conditions)

        cursor.execute(query, values)

        results = cursor.fetchall()

        return render_template("result.html", results=results)

    return render_template("symptom_checker.html")



# ADMIN LOGIN
@app.route('/admin', methods=['GET','POST'])
def admin():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # simple login check
        if username == "admin" and password == "admin123":
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')


# ADMIN DASHBOARD
@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


# ADD PROBLEM
@app.route("/admin/add", methods=["GET", "POST"])
def add_problem():

    if request.method == "POST":

        name = request.form["name"]
        symptoms = request.form["symptoms"]
        description = request.form["description"]
        causes = request.form["causes"]
        treatment = request.form["treatment"]
        prevention = request.form["prevention"]
        severity = request.form["severity"]

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO dental_problems
        (problem_name, symptoms, description, causes, treatments, prevention_tips, severity_level)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """

        values = (name, symptoms, description, causes, treatment, prevention, severity)

        cursor.execute(query, values)

        conn.commit()

        return redirect(url_for("view_problems"))

    return render_template("add_problem.html")


# VIEW ALL PROBLEMS
@app.route("/admin/problems")
def view_problems():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM dental_problems")

    problems = cursor.fetchall()

    return render_template("view_problems.html", problems=problems)


# DELETE PROBLEM
@app.route("/admin/delete")
def delete_page():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM dental_problems")
    problems = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("delete.html", problems=problems)

@app.route("/admin/delete/<int:id>")
def delete_problem(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM dental_problems WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("delete_page"))

# EDIT PROBLEM
@app.route("/admin/edit")
def edit_page():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM dental_problems")

    problems = cursor.fetchall()

    return render_template("edit_problem.html", problems=problems)

@app.route("/admin/edit/<int:id>", methods=["GET","POST"])
def edit_problem(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        symptoms = request.form["symptoms"]
        description = request.form["description"]
        causes = request.form["causes"]
        treatment = request.form["treatment"]
        prevention = request.form["prevention"]
        severity = request.form["severity"]

        query = """
        UPDATE dental_problems
        SET problem_name=%s,
        symptoms=%s,
        description=%s,
        causes=%s,
        treatments=%s,
        prevention_tips=%s,
        severity_level=%s
        WHERE id=%s
        """

        values = (name, symptoms, description, causes, treatment, prevention, severity, id)

        cursor.execute(query, values)

        conn.commit()

        return redirect("/admin/problems")

    cursor.execute("SELECT * FROM dental_problems WHERE id=%s", (id,))
    problem = cursor.fetchone()

    return render_template("edit_form.html", problem=problem)



if __name__ == "__main__":
    app.run(debug=True)