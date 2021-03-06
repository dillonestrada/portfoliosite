from flask import Flask, request, render_template, redirect, url_for, Response, jsonify
from flask_mail import Message, Mail
import json, requests
from flask_cors import CORS
from creds import gmail, secret_key, recaptcha_secret_key

 
mail = Mail()
 
app = Flask(__name__)
CORS(app)
 
app.secret_key = secret_key
 
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = gmail['email']
app.config["MAIL_PASSWORD"] = gmail['password']

mail.init_app(app)

app.debug = True

@app.errorhandler(Exception)
def page_not_found(e):
    code = 500
    message = "Something Went Wrong"
    error = str(e)
    print(error)
    if '404' in error:
        message = "Page Not Found"
        code = 404
    elif '403' in error:
        message = "Forbidden"
        code = 403
    elif '500' in error:
        message = "Internal Server Error"
        code = 500

    return render_template('sections/error.html', message=message, code=str(code)), code

@app.route('/')
def home():
    try:
        success = request.args.get('success')
    except:
        success = False

    return render_template('index.html', success=success)

@app.route('/contact', methods=['POST'])
def contact():
    try:
        music_req = request.args.get('music')
        args = request.get_json()
        name = args['p_name']
        email = args['p_email']
        message = args['p_message']
        recaptcha = args['g-recaptcha-response']

        msg = Message("Email from contact form on music.dillonestrada.com", sender=gmail['email'], recipients=[gmail['music_email']])
    except:
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            recaptcha = request.form.get('g-recaptcha-response')

            msg = Message("Email from contact form on dillonestrada.com", sender=gmail['email'], recipients=[gmail['forward_email']])
        except:
            return "Uh oh..."
    if(recaptcha):
        print('captcha')
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data={'secret': recaptcha_secret_key, 'response': recaptcha})
        r_json = r.json()
        if(r_json['success']):
            msg.html = f"<h1>Name: {name}</h1><h3>Email: {email}</h3><p>{message}</p>"

            mail.send(msg)
            if(music_req):
                return Response(status=200)
            success = True
            return redirect(url_for('.home', success=success))
    
    return redirect(url_for('.home'))

@app.route('/services', methods=['GET'])
def prices():

    name = request.args.get('name')
    
    if(name):
        return render_template('services.html', name=name.capitalize())
    else:
        return render_template('services.html')
    

if __name__ == '__main__':
    app.run(port=8080)