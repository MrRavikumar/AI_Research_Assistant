from flask import Flask, render_template, redirect,request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore,auth

app = Flask(__name__)
cred = credentials.Certificate("airesearch.json")
firebase_admin.initialize_app(cred)

store = firestore.client()

@app.route('/',methods = ['GET','POST'])
def home():

    return render_template("index.html")

@app.route('/signup',methods = ['GET','POST'])
def signup():
    userid=""
    message=""
    details = {}
    skills = []

    if request.method == 'POST':
        username=request.form["username"]
        useremail=request.form["email"]
        userpassword=request.form["password"]
        userconfirmp=request.form["confirmpassword"]
        
        
        try:
            print("inside")
            user=auth.create_user(
            email=useremail,
            email_verified=False,
            password=userpassword)
            message="Succesfully created user"
            userid = user.uid
        
            dit = {}
            dit['username'] = username
            dit["email"] = useremail
            dit['password'] = userpassword
            
            
            if userpassword == userconfirmp:
                store.collection('UserCollection').add(dit)
                return redirect('/login')
            else:
                message = "Password Does not Match!"
                

            
            
        except:
            message="User already exists"

        print(message)
        return jsonify("message:",message)
    
    return render_template("Signup.html")

@app.route('/login',methods = ['GET','POST'])
def login():
    dit = {}
    message = ""
    print(f"method is {request.method}")
    if request.method == 'POST':
        useremail=request.form["email"]
        userpassword=request.form["password"]
        message=""
        uid=""
        try:
            user=auth.get_user_by_email(useremail)
            message="Woohooo, succesfully logged in"

            return redirect('/searchpaper')
        except:
            message="User authentication failed"
            return jsonify("message:",message)
        

    return render_template('Login.html')

@app.route('/searchpaper',methods = ['GET','POST'])
def searchpaper():
    return render_template("searchPaper.html")

if __name__ == '__main__':
    app.run(host = "127.0.0.1", port = "3000",debug=True)