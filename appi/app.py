from flask import Flask, redirect, session, request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///miskapajukangas"
db = SQLAlchemy(app)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/loginresult", methods=["POST"])
def loginresult():
    username = request.form["username"]
    password = request.form["password"]
    sql = text("SELECT id, password, role FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if not user:
        # TODO: invalid username
        return redirect("/")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            # TODO: correct username and password
            if user.role == "admin":
                session["role"] = "admin"
            session["username"] = username
            return redirect("/")
        else:
            # TODO: invalid password
            return redirect("/login")


@app.route("/newaccountresult", methods=["POST"])
def newaccountresult():
    newUsername = request.form["username"]
    newPassword = request.form["password"]
    hash_value = generate_password_hash(newPassword)
    sql = text("INSERT INTO users (username, password, role) VALUES (:username, :password, 'basic')")
    db.session.execute(sql, {"username":newUsername, "password":hash_value})
    db.session.commit()
    return redirect("/")


@app.route("/newaccount")
def newaccount():
    return render_template("newaccount.html")


@app.route("/addrestaurant", methods=["POST"])
def addrestaurant():
    newRestaurantName = request.form["restaurantName"]
    sql = text("INSERT INTO restaurants (name) VALUES (:restaurantName)")
    db.session.execute(sql, {"restaurantName": newRestaurantName})
    db.session.commit()
    return redirect("/")


@app.route("/restaurants/<restaurantName>", methods=["GET"])
def restaurant(restaurantName):
    sql = text("SELECT reviews.starReview, reviews.textReview, restaurants.name,"
               " restaurants.description "
               "FROM reviews "
               "RIGHT JOIN restaurants ON reviews.restaurantId = restaurants.id "
               "WHERE restaurants.name = :restaurantName;")
    reviews = db.session.execute(sql, {"restaurantName": restaurantName})
    data = reviews.fetchall()

    if data:
        opening_hours_sql = text("SELECT openDay, openHourStart, openHourEnd "
                                 "FROM opening_hours "
                                 "INNER JOIN restaurants ON opening_hours.restaurantId = restaurants.id "
                                 "WHERE restaurants.name = :restaurantName;")
        hoursResult = db.session.execute(opening_hours_sql, {"restaurantName": restaurantName})
        hoursData = hoursResult.fetchall()
        starreview_sum = 0
        count = 0
        for i in data:
            if i.starreview is not None:
                starreview_sum += int(i.starreview)
                count += 1
        if starreview_sum != 0:
            meanScore = starreview_sum / count
            return render_template("restaurant.html",
                               restaurantName=restaurantName,
                               reviews=data,
                               meanScore="{:.1f}".format(meanScore),
                                openingHours=hoursData)
        else:
            return render_template("restaurant.html",
                                   restaurantName=restaurantName,
                                   openingHours=hoursData,
                                   reviews=data)
    else:
        return render_template("restaurant.html",
                               restaurantName=restaurantName,
                               reviews=reviews)


@app.route("/addreview/<restaurantName>", methods=["POST"])
def addreview(restaurantName):
    starReview = request.form["rating"]
    textReview = request.form["textReview"]
    idQuery = text("SELECT id FROM restaurants WHERE name = :restaurantName")
    restaurant = db.session.execute(idQuery, {"restaurantName": restaurantName})
    result = restaurant.fetchone()

    if result:
        restaurantId = result[0]
        sql = text("INSERT INTO reviews (restaurantId, starReview, textReview) "
                   "VALUES (:restaurantId, :starReview, :textReview)")

        db.session.execute(sql, {"restaurantId": restaurantId,
                                 "starReview": starReview,
                                 "textReview": textReview})
        db.session.commit()
        return redirect(f'/restaurants/{restaurantName}')
    else:
        return redirect(f'/restaurants/{restaurantName}')


@app.route("/adddescription/<restaurantName>", methods=["POST"])
def adddescription(restaurantName):
    description = request.form["description"]
    sql = text("UPDATE restaurants "
               "SET description = :description "
                "WHERE name = :restaurantName; ")
    db.session.execute(sql, {"description": description,
                             "restaurantName": restaurantName})
    db.session.commit()
    return redirect(f'/restaurants/{restaurantName}')


@app.route("/addhours/<restaurantName>", methods=["POST"])
def addhours(restaurantName):
    mondayStart = request.form["timeStart1"]
    tuesdayStart = request.form["timeStart2"]
    wednesdayStart = request.form["timeStart3"]
    thursdayStart = request.form["timeStart4"]
    fridayStart = request.form["timeStart5"]
    saturdayStart = request.form["timeStart6"]
    sundayStart = request.form["timeStart7"]
    mondayEnd = request.form["timeEnd1"]
    tuesdayEnd = request.form["timeEnd2"]
    wednesdayEnd = request.form["timeEnd3"]
    thursdayEnd = request.form["timeEnd4"]
    fridayEnd = request.form["timeEnd5"]
    saturdayEnd = request.form["timeEnd6"]
    sundayEnd = request.form["timeEnd7"]
    print(type(mondayEnd), type(mondayStart))
    idQuery = text("SELECT id FROM restaurants WHERE name = :restaurantName")
    restaurant = db.session.execute(idQuery,
                                    {"restaurantName": restaurantName})
    result = restaurant.fetchone()

    if result:
        restaurantId = result[0]

        sql = text("INSERT INTO opening_hours(restaurantId, openDay, openHourStart, openHourEnd)"
                " VALUES (:restaurantId, 1, :timeStart1, :timeEnd1) ")

        sql2 = text("INSERT INTO opening_hours(restaurantId, openDay, openHourStart, openHourEnd)"
                " VALUES (:restaurantId, 2, :timeStart2, :timeEnd2) ")

        sql3 = text("INSERT INTO opening_hours(restaurantId, openDay, openHourStart, openHourEnd)"
                " VALUES (:restaurantId, 3, :timeStart3, :timeEnd3) ")

        sql4 = text("INSERT INTO opening_hours(restaurantId, openDay, openHourStart, openHourEnd)"
                " VALUES (:restaurantId, 4, :timeStart4, :timeEnd4) ")

        sql5 = text("INSERT INTO opening_hours(restaurantId, openDay, openHourStart, openHourEnd)"
                " VALUES (:restaurantId, 5, :timeStart5, :timeEnd5) ")

        sql6 = text("INSERT INTO opening_hours(restaurantId, openDay, openHourStart, openHourEnd)"
                " VALUES (:restaurantId, 6, :timeStart6, :timeEnd6) ")

        sql7 = text("INSERT INTO opening_hours(restaurantId, openDay, openHourStart, openHourEnd)"
                " VALUES (:restaurantId, 7, :timeStart7, :timeEnd7) ")

        db.session.execute(sql, {
            "restaurantId": restaurantId, "timeStart1": mondayStart, "timeEnd1": mondayEnd
        })
        db.session.execute(sql2, {
            "restaurantId": restaurantId, "timeStart2": tuesdayStart,
            "timeEnd2": tuesdayEnd
        })
        db.session.execute(sql3, {
            "restaurantId": restaurantId, "timeStart3": wednesdayStart,
            "timeEnd3": wednesdayEnd
        })
        db.session.execute(sql4, {
            "restaurantId": restaurantId, "timeStart4": thursdayStart,
            "timeEnd4": thursdayEnd
        })
        db.session.execute(sql5, {
            "restaurantId": restaurantId, "timeStart5": fridayStart,
            "timeEnd5": fridayEnd

        })
        db.session.execute(sql6, {
            "restaurantId": restaurantId, "timeStart6": saturdayStart,
            "timeEnd6": saturdayEnd
        })
        db.session.execute(sql7, {
            "restaurantId": restaurantId, "timeStart7": sundayStart,
            "timeEnd7": sundayEnd
        })

        db.session.commit()
        return redirect(f"/restaurants/{restaurantName}")
    else:
        return redirect(f"/restaurants/{restaurantName}")





@app.route("/logout")
def logout():
    del session["username"]
    try:
        del session["role"]
    except:
        pass
    return redirect("/")


@app.route("/")
def index():
    result = db.session.execute(text("SELECT * FROM restaurants ORDER BY name ASC;"))
    restaurants = result.fetchall()
    return render_template("restaurants.html", count=len(restaurants),
                           restaurants=restaurants)
