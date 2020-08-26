import os
import requests
from hash import protect_pass , verify_Password
from apidatas import getratings
from flask import Flask, session , render_template, request, redirect, url_for, jsonify
from flask_session import Session
from flask_api import status
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker



app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#website base page
@app.route("/")
def index():
    if 'username' in session:
        return  redirect(url_for('booksearch'))
    return render_template("homepage.html")

@app.route("/usercheck", methods = ['POST'])
def checkuser():
    username = request.form.get("usrnamecreate")

    checksql = "SELECT * FROM users WHERE username = :username"
    inputs = {"username" : username}

    result = db.execute(checksql,inputs).fetchone()

    if result == None:
        return "True"
    return "False"

# route to allow users to register
#accepts GET and POST methods only
@app.route("/register" , methods=['GET','POST'])
def Register():

    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get("usrnamecreate")
    retrievepassword = request.form.get("passwrdcreate")
    password = protect_pass(str(retrievepassword).encode())

    checksql = "SELECT * FROM users WHERE username = :username AND password = :password"
    inputs = {"username" : username, "password": str(password)}

    if db.execute(checksql,inputs).rowcount != 0: #if we get a row returned then user has an account already
        return render_template("registrationfail.html")
    

    insertsql = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.execute(insertsql,inputs) 
    db.commit()
    return render_template("success.html" , reguser = username)



# route to allow users who are registered to login
#accepts GET and POST methods only
@app.route("/login", methods=['GET','POST'])
def Login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get("usrname")
    retrievepassword = request.form.get("passwrd")

    #first check to see if user exist
    checksql = "SELECT * FROM users WHERE username = :username"
    inputs = {"username" : username }
    
    if db.execute(checksql,inputs).rowcount == 0:
        return render_template("loginfail.html")

    #if user exist we get the password and match it
    getpasswordquery = "SELECT password FROM users WHERE username = :username"
    result = db.execute(getpasswordquery,inputs).fetchone()
    storedpass = -1
    for val in result:
        storedpass = val

    passwordtobyte = protect_pass(str(retrievepassword).encode())
    
    #now we verify that the password the user entered is valid
    if verify_Password(storedpass , str(passwordtobyte)):
        session['username'] = username
        return  redirect(url_for('booksearch'))
    else:
        return render_template("nulllogin.html")



# once loged in this route will display search page for user
#only accessed through POST method

@app.route("/home" , methods = ['GET','POST'])
def booksearch():
    if 'username' in session:
        if request.method == 'GET':
            return render_template("home.html", user = session['username'])
        else:
            usrinput = request.form.get('searchrequest')
            
            sql = "SELECT title, author, isbn FROM books WHERE (isbn LIKE :isbn OR title LIKE :title OR author LIKE :author)"
            input = "%{}%".format(usrinput)

            values = {'isbn' : input, 'title' : input, 'author' : input}

            datareturned = db.execute(sql,values).fetchall()
            username = session['username']
            return render_template("searchresults.html", booksfound = datareturned, userreq=usrinput, username = username )


@app.route("/book/<book_id>", methods = ['GET'])
def bookinformation(book_id):
    if 'username' in session:
        #need to get book title,author, year, ISBN, reviews left by users
        infosql = "SELECT title, isbn, author, published FROM books WHERE (books.isbn = :isbn)"
        inputs = {'isbn' : book_id}

        datareturned = db.execute(infosql,inputs).fetchone()

        reviewsql = "SELECT rating, text, userid FROM reviews WHERE reviews.bookid IN (SELECT isbn FROM books WHERE isbn = :isbn)"
        reviewreturned = db.execute(reviewsql,inputs).fetchall()

        usrhasreview = False
        for row in reviewreturned:
            if session['username'] == row.userid:
                usrhasreview = True
                break

        # get average rating and # of ratings from goodreads
        number_ratings, average_rating  = getratings(book_id)

        return render_template("abook.html", bookinfo = datareturned, usr = session['username'], usrhasreview = usrhasreview, reviewinfo = reviewreturned , ratingsnumber = number_ratings , average = average_rating)

    else:
        return "Need to be logged in to view book details<br><a href = 'login.html'> sign in here </a>"
#functions i need to implement

#review submit function - paramters: book_id, user_id
    #make sure user hasn't already submitted a review for this book
    #make sure to update reviewcount and averagescore for book
@app.route("/review/<user_id>/<book_id>" , methods = ['POST'])
def reviewSubmit(book_id,user_id):
    if 'username' in session:
        if session['username'] == user_id: #make sure we have the right user submittinf a review
            sqlcheckforreview = "SELECT * FROM reviews WHERE bookid = :bookid AND userid = :userid"
            inputs = { "bookid" : book_id, "userid" : user_id}

            result = db.execute(sqlcheckforreview, inputs).fetchone()
            if result != None:  #if they already submitted a review for this book, let them know
                return render_template("reviewsubmit.html", success = False, username = session['username']) #need to fill in paramters once file created
            else:
                rating = int(request.form['reviewrating'])
                text = request.form['textsubmitted']

                insertquery = "INSERT INTO reviews (bookid, userid, text, rating) VALUES (:bookid,:userid, :text, :rating)"
                inputs = { "bookid" : book_id, "userid" : user_id, "text" : text, "rating" : rating}
            
                db.execute(insertquery,inputs)  #if we were able to insert review succesfully
                db.commit()
                #now we update review count and average review for the book
                updatequery = "UPDATE books SET reviewcount = (SELECT COUNT(*) rating FROM reviews WHERE bookid = :bookid), averagescore = (SELECT AVG(rating) FROM reviews WHERE bookid = :bookid) WHERE isbn = :bookid"
                inputs = { "bookid" : book_id}
                db.execute(updatequery,inputs)
                db.commit()
                return render_template("reviewsubmit.html", success = True ,book = book_id, username = session['username']) #need to fill in paramters once file created
        else:
            content = "Unauthorized access"
            return content, status.HTTP_401_UNAUTHORIZED
        


#review edit function paramters: book_id, user_id -- do last
@app.route("/reviewEdit/<user_id>/<book_id>" , methods = ['GET'])
def reviewEdit(user_id,book_id):
    if 'username' in session:

        ratingsql = "SELECT rating, text FROM reviews WHERE (bookid = :bookid AND userid = :userid)"
        inputs = { "bookid" : book_id, "userid" : user_id}

        ratingText = db.execute(ratingsql,inputs).fetchone()
        #rating = str(rating)

        return render_template("reviewedit.html", rating= ratingText, bookinfo=book_id, usr =user_id)
    else:
        content = {'must be logged in': 'in order to edit review'}
        return content, status.HTTP_405_METHOD_NOT_ALLOWED


@app.route("/reviewUpdate/<user_id>/<book_id>" , methods = ['POST'])
def reviewUpdate(user_id, book_id):
    if 'username' in session:
        rating = int(request.form.get('updatereviewrating'))
        text = request.form.get('updatetextsubmitted')

        reviewupdatequery = "UPDATE reviews SET text = :text, rating = :rating WHERE (bookid = :bookid AND userid = :userid)"
        inputs = { "bookid" : book_id, "userid" : user_id, "text" : text, "rating" : rating}

        db.execute(reviewupdatequery, inputs)
        db.commit()

        updatequery = "UPDATE books SET reviewcount = (SELECT COUNT(*) rating FROM reviews WHERE bookid = :bookid), averagescore = (SELECT AVG(rating) FROM reviews WHERE bookid = :bookid) WHERE isbn = :bookid"
        inputs = { "bookid" : book_id}

        db.execute(updatequery,inputs)
        db.commit()
        return render_template("updateresult.html", usernmae = session['username'])


#logout function
#  pop session username
# return to / 
@app.route("/logout" , methods = ['GET'])
def logout():
    if 'username' in session:
        # remove the username from the session if it is there
        session.pop('username', None)
        return redirect(url_for('index'))
    else:
        content = {'must be logged in': 'in order to logout'}
        return content, status.HTTP_405_METHOD_NOT_ALLOWED
        


# once loged in this route will display search page for user
#only accessed through get method
@app.route("/myreviews" , methods = ['GET'])
def usereviews():
    if 'username' in session:   
        
        sql = "SELECT isbn, title, author ,text, rating FROM reviews, books WHERE (reviews.userid= :username AND books.isbn = reviews.bookid)"
        input = session['username']

        values = {'username' : input}

        datareturned = db.execute(sql,values).fetchall()

        return render_template("myreviews.html", reviewlist = datareturned, usr = input)
    #flask will handle else case, which would only rise route was accessed
    #through anyother method other than 'GET'

@app.route("/reviewDelete/<user_id>/<book_id>", methods=['GET'])
def reviewDelete(user_id,book_id):
    if 'username' in session:
        deleteQeuery = "DELETE FROM reviews WHERE (userid = :userid AND bookid = :bookid)"
        inputs = { "bookid" : book_id, "userid" : user_id}

        db.execute(deleteQeuery,inputs)

        updatequery = "UPDATE books SET reviewcount = (SELECT COUNT(*) rating FROM reviews WHERE bookid = :bookid), averagescore = (SELECT AVG(rating) FROM reviews WHERE bookid = :bookid) WHERE isbn = :bookid"
        inputs = { "bookid" : book_id}

        db.execute(updatequery,inputs)
        db.commit()

        return render_template("reviewDelete.html", book= book_id, username = user_id)
    else:
        content = {'must be logged in': 'in order to delete your review'}
        return content, status.HTTP_405_METHOD_NOT_ALLOWED