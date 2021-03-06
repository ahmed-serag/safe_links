from flask import (
    Flask, 
    make_response,
    render_template, 
    request, 
    redirect, 
    url_for,
    session as login_session
)
import hmac
from user import user
from links import links
import hashlib
import requests
from streamango import Streamango

app = Flask(__name__)

URL = "http://server.full-stream.nu"
DATABASE = 'safe_links'
USERNAME = 'root'
PASSWORD = '@Hmed20102010'
PORT = 3306

user_ins = user(username=USERNAME, password=PASSWORD, database=DATABASE, port=PORT)
links_ins = links(username=USERNAME, password=PASSWORD, database=DATABASE, port=PORT)
secret = b"Cool Links!!"

def haaash(w):
    h = hashlib.md5(w)
    x = h.hexdigest().encode('utf-8')
    h = hashlib.md5(x)
    return h.hexdigest()

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val.encode('utf-8')).hexdigest().encode('utf-8'))
####
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val
    else:
        return None
####
@app.route('/')
def home():
    if 'id' in login_session and request.cookies.get('username') and check_secure_val(request.cookies.get('username')):
        id = login_session['id']
        user = user_ins.getUser(id)
        if user:
            # add link based on the request
            links = links_ins.getLinks()
            return render_template('home.html',links=links)
        
    return render_template('login.html')
####
@app.route('/add-link', methods=['POST'])
def add_link():
    if 'id' in login_session and request.cookies.get('username') and check_secure_val(request.cookies.get('username')):
        user_id = login_session['id']
        user = user_ins.getUser(user_id)[0]
        if user:
           if request.form['platform'] == 'streamango':
            print(request.form['link'])
            print(request.form['link'].split('\n')[0])
            for link in request.form['link'].split('\n'):

                new_link = streamango_add_remote_download(
                    url=link,
                    username = user[4],
                    key = user[5]
                )
                print(new_link)
                # add link based on the request
                filename=  new_link['id']
                public_link= URL+"/video-"+new_link['id']
                packup_link= new_link['url'].replace('/f/','/embed/'),
                current_link=new_link['remoteurl']

                links_ins.addLink(
                    platform=request.form['platform'], 
                    filename=filename, 
                    current_link=current_link, 
                    packup_link=packup_link, 
                    public_link=public_link, 
                    user=user_id
                )
    return redirect('/')

@app.route('/video-<string:link>', methods=['GET'])
def getLink(link):   
    l = links_ins.getLinks(filename=link)[0]
    user = user_ins.getUser(l[6])[0]
    response = requests.get(l[4])
    print(response.status_code)
    print("&&&&&&&&&&****************")
    if(response.status_code == 404):
        new_link = streamango_add_remote_download(
            url=l[5],
            username = user[4],
            key = user[5]
        )
        print(new_link)
        # add link based on the request
        packup_link= new_link['url'].replace('/f/','/embed/'),
        current_link=l[5]
        links_ins.updateLink(id=l[0], current_link=current_link, packup_link=packup_link, user=user[0])
        return redirect(current_link)
    else:

        return redirect(l[4])
####

@app.route('/adduser', methods=['POST','GET'])
def adduser():
    print(request.method)
    if request.method == "POST" and 'id' in login_session and request.cookies.get('username') and check_secure_val(request.cookies.get('username')):
        user_ins.addUser(
            password=haaash(str(request.form['password']).encode('utf-8')), 
            username=request.form['username'],
            type=request.form['type'], 
            api_login=request.form['api_login'], 
            api_key=request.form['api_key']
        )
    users = user_ins.getUser()
    return render_template('add_user.html', users=users)


@app.route('/login', methods=['POST'])
def login():
    if 'username' in request.form and 'password' in request.form:
        user = user_ins.login(
            password=haaash(str(request.form['password']).encode('utf-8')), 
            username=request.form['username']
        )
        if user:
            login_session['id'] = user[0]
            login_session['username'] = user[1]
            login_session['type'] = user[3]
            resp = make_response(redirect('/'))
            resp.set_cookie('username', make_secure_val(user[1]))
            return resp    
    return redirect('/')
####

@app.route('/logout', methods=['GET'])
def logout():   
    login_session.clear()
    respond = make_response(redirect('/'))
    respond.set_cookie('username', '', expires=0)
    return respond
####

def streamango_add_remote_download(url, username, key):
    sm = Streamango(username, key)
    resp = sm.remote_upload(url)
    file_id = resp.get('id')
    resp = sm.remote_upload_status(remote_upload_id=file_id)
    return resp[file_id]


if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jJHVDmN]LWX/,?RT'
    app.debug = True
    app.run(host='0.0.0.0', threaded = True)
