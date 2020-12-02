from flask import Flask, render_template, g, session, request, redirect , url_for
import re
import bcrypt
import configparser
import sqlite3
import json
import random
from functools import wraps
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__)
db_location = 'var/flashdb.db'
socketio = SocketIO(app)

def init(app):
    cfg = configparser.ConfigParser()
    cfg_l = "etc/defaults.cfg" #config location
    try:
        cfg.read(cfg_l)
        app.config['secret_key'] = cfg.get("config", "secret_key")
        app.secret_key = app.config['secret_key']
        
    except:
        print("ah jeez config no worky")
    

init(app)

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = sqlite3.connect(db_location)
        g.db = db
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('etc/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_words(location):
    # get words
    with open(location, 'r') as rf:
        words = json.load(rf)
    random.shuffle(words)
    return words

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('etc/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        status = session.get('loggedin', False)
        if not status:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/database/')
def database():
    db = get_db()
    #db.cursor().execute('insert into pb values (11, 82, 18)')
    

    page = []
    page.append('<html><ul>')

    page.append('<ul>')
    sql = "select * FROM users ORDER BY joined DESC"
    page.append('<h1>users table</h1>')
    for row in db.cursor().execute(sql):
        page.append('<li>'+str(row)+'</li>')
    page.append('</ul>')

    page.append('<ul>')
    sql = "select * FROM decks ORDER BY deckID DESC"
    page.append('<h1>decks table</h1>')
    for row in db.cursor().execute(sql):
        page.append('<li>'+str(row)+'</li>')
    page.append('</ul>')

    page.append('<ul>')
    sql = "select * FROM cards ORDER BY cardID DESC"
    page.append('<h1>cards table</h1>')
    for row in db.cursor().execute(sql):
        page.append('<li>'+str(row)+'</li>')
    page.append('</ul>')

    page.append('<html>')
    return ''.join(page)

@app.route('/', methods=['POST', 'GET'])
def root():
    db = get_db() # get db
    try:
        if request.arg['lang'] == 'kr':
            test = "Korean 1000"
            testWords = get_words('static/js/json/kr1000.json')
    except:
        test = "English 1000"
        testWords = get_words('static/js/json/eng1000.json')

    if request.method=="POST":
        wpm = (int(request.form['correct'])-1)/int(request.form['time'])*60/5
        correct = request.form['correct']
        total = request.form['total']
        time = int(request.form['time'])
        words=request.form['lang']
        if request.form['total'] == 'static/js/json/eng1000.json':
            test = "English 1000"
        else:
            test = "Korean 1000"

        if time == 15:
            db.cursor().execute('update users set wpm15=?, lang15=?', (wpm, test))
        elif time == 30:
            db.cursor().execute('update users set wpm30=?, lang30=?', (wpm, test))
        elif time == 60:
            db.cursor().execute('update users set wpm60=?, lang60=?', (wpm, test))
        db.commit()
        return render_template('sType.html', title="Flash Typer", testWords=words, test=test, openStats=True, wpm=wpm, correct=correct, total=total)
    else:
        return render_template('sType.html', title="Flash Typer", testWords=testWords, test=test)


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method =='POST': # if posts
        db = get_db() # get db
        name = request.form['name']
        password = request.form['pass']
        errMsg = ''
        
        for row in db.cursor().execute("select name, pass from users where name = ?", (name, )): # check user exists
            exists = True
            name, passH= row
            break
        else:
            exists = False

        if 'login' in request.form: # if request to login
            # checks if the user exists and compares passwords
            if exists and bcrypt.checkpw(password.encode('utf-8'), passH): 
                session['loggedin'] = True
                session['name'] = name
                return redirect(url_for('root')) # if credentials are correct redirect to root
            else:
                errMsg += "Incorrect Credentials"
                return redirect(url_for('login')+'?err='+errMsg+'&name='+name) 
        else: # if request to signup
            # form validation
            if not(name): # check name is empty
                errMsg += 'Username field is empty\n' # add error
            elif len(name) > 24 or len(name) <3:
                errMsg += 'Username must be between 3 and 24 characters<br>' # add error
            elif not(re.match('^\w+$', name)): 
                errMsg += 'Invalid username: alphanumerics and underscores only<br>' # add error
            elif exists:
                errMsg += 'Username already taken<br>' # add error

            if not(password):  # check password is blank
                errMsg += 'Password field is empty<br>' # add error
            elif len(password) < 6:
                errMsg += 'Password must be at least 6 characters<br>' # add error

            if password != request.form['passCon']: # check passwords match
                errMsg += 'Passwords do not match<br>' # add error
            
            if errMsg: # if there are errors
                return redirect(url_for('login')+'?err='+errMsg+'&name='+name) 
            else:
                passH = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=15))
                db.cursor().execute('insert into users values (?, ?, CURRENT_DATE, 0, 0, 0, NULL, NULL, NULL)', (name, passH))
                db.commit()
                session['loggedin'] = True
                session['name'] = name
                return redirect(url_for('root'))
    else:
        errMsg = request.args.get('err', '')
        name = request.args.get('name', '')
        return render_template('login.html', title='Flash Typer - Login', err=errMsg, name=name)

@app.route('/MyFlashcards/', methods=['POST', 'GET'])
@requires_login
def decks():
    db = get_db() # get db
    if request.method =='POST': # if posts

        # create new deck
        if 'new_deck' in request.form:
            print("in new deck post")
            # create new database entry
            db.cursor().execute('insert into decks values (NULL, ?, "Untitled Deck", CURRENT_DATE)', (session['name'], ))
            db.commit()

            # redirect to the created deck
            for row in db.cursor().execute("select deckID from decks where owner = ? ORDER BY deckID DESC", (session['name'], )):
                return redirect(url_for('edit_deck')+"?deckID="+str(row[0]))

        # delete deck
        if 'del_deck' in request.form:
            print("deleted deck")
            # delete cards in deck

            # delete deck
            db.cursor().execute('delete from decks where deckID = ?', (request.form['deckID'], ))
            db.commit()

    

    # get all decks
    # db.cursor().execute("select * from decks where owner = ?", (session['name'], ))
    # rows = db.cursor().fetchall()
    
    
    # decks = []
    decks = []
    sql = "select * FROM decks where owner = '%s' order by deckID desc" % session['name']
    for row in db.cursor().execute(sql):
        # decks.append('''<div class="deck"><img src="/static/svg/deckicon.svg" alt="" style="width:100%"><div class="deck-options"></div></div>''')
        deckID, owner, title, lastUpdated = row
        decks.append({'deckID':deckID, 'owner':owner,'title':title,'lastUpdated':lastUpdated}.copy())
    return render_template('decks.html', title="FlashTyper - Decks", decks=decks)

@app.route('/EditDeck/', methods=['POST', 'GET'])
@requires_login
def edit_deck():
    db = get_db()

    try:
        if request.args['deckID']:
            # check deck exists
            for row in db.cursor().execute("select * from decks where deckID = ?", (request.args['deckID'], )):
                deckID, owner, title, lastUpdated = row
                break
            else:
                return redirect(url_for('decks')+"?err=DeckNonExistant")
    except:
        return redirect(url_for('decks')+"?err=DeckIDNotSupplied")

    # db.cursor().execute('insert into cards values (null, 2, "TESTA", "DWADAWDWAD")')
    # db.commit()
    if request.method == 'post':
        print("in card post")
        if 'del_card' in request.form:
            print("del card")
            db.cursor().execute("delete from cards where cardID = ?", (request.form['cardID'], ))
            db.commit()

        elif 'new_card' in request.form:
            print("in new card post")
            db.cursor().execute('insert into cards values (null, ?, ?, ?)', (request.form['deckID'], request.form['sideA'],request.form['sideB'],))
            db.commit()
        
    #get cards
    cards = []
    for row in db.cursor().execute("select * from cards where deckID = ?", (request.args['deckID'], )):
        cardID, deckID, sideA, sideB = row
        cards.append({'cardID':cardID, 'deckID':deckID,'sideA':sideA,'sideB':sideB}.copy())
    return render_template('editDeck.html', title=title, deckID=str(request.args['deckID']), cards=cards)

@app.route('/FlashTest/')
@requires_login
def cardTest():
    return render_template('cardTest.html')

@app.route('/profile/<user>', methods=['POST', 'GET'])
@app.route('/profile/', methods=['POST', 'GET'])
@requires_login
def profile(user=None):
    db = get_db()

    if request.method == 'POST':
        print("inpost")
        if not(request.form['pass']): # if request to delete
            print('in del')
            for row in db.cursor().execute("select pass from users where name = ?", (request.form['name'], )): # check user exists
                print('user check')
                passH= row
                exists = True
                if bcrypt.checkpw(request.form['pass'].encode('utf-8'), passH):
                    print("pass matched")
                    for row in db.cursor().execute("select deckID from users where owner = ?", (request.form['name'], )):
                        db.cursor().execute("delete from cards where deckID = ?", (row,))
                        db.commit()
                        db.cursor().execute("delete from decks where deckID = ?", (row,))
                        db.commit()
                        print("card/deck del")
                    db.cursor().execute("delete from users where userID = ?", (request.form['name'],))
                    db.commit()
                    print("user del")
                return redirect(url_for('.root'))
                break
            else:
                return redirect(url_for('profile')+"?err=wrongPass")
    if user == None:
        user = session['name']
    else:
        user = user
    

    for row in db.cursor().execute("select name, joined, wpm30, wpm60, wpm15 from users where name = ?", (user, )): # check user exists
        name, joined, wpm30, wpm60, wpm15 = row
        x = {'name': name, 'joined': joined, 'wpm30': wpm30, 'wpm60':wpm60, 'wpm15':wpm15}
        return render_template('profile.html', active = x, title = name+"'s Profile")
    else:
        return redirect(url_for('root')+'?err=NoUserFound')


@app.route('/logout/')
def logout():
    session['loggedin'] = False
    session['name'] = ''
    return redirect(url_for('.root'))


@socketio.on('username', namespace='/eng')
def receive_username(username, name):
    
    users.append({username : request.sid})
    print(users)
    print('Username added!')
    x+1
    print(x)

def gen_lobby_code():
    random_string = ''
    for _ in range(10):
        # Considering only upper and lowercase letters
        random_integer = random.randint(97, 97 + 26 - 1)
        flip_bit = random.randint(0, 1)
        # Convert to lowercase if the flip bit is on
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
        # Keep appending random characters using chr(x)
        random_string += (chr(random_integer))
    return random_string


lobbyEng = []
@socketio.on('message', namespace='/pub_eng')
def handleMessage(name, wpm):
    isthere = 0
    check = {'id':name,'wpm':wpm}
    for users in lobbyEng:
        if users['id'] == check['id']:
            isthere = 1
    if isthere == 0:
        lobbyEng.append({'id':name,'wpm':wpm})
    print(lobbyEng)
    emit(lobbyEng, broadcast=True)

lobbyId = []
@socketio.on('message', namespace='/pub_id')
def handleMessage(name, wpm):
    isthere = 0
    check = {'id':name,'wpm':wpm}
    for users in lobbyId:
        if users['id'] == check['id']:
            isthere = 1
    if isthere == 0:
        lobbyId.append({'id':name,'wpm':wpm})
        emit('players', name , broadcast=True)
        emit('nPlayer', len(lobbyId) , broadcast=True)
        print(lobbyId)

@app.route('/multiplayer/')
@requires_login
def multi():
    return render_template('mLobby.html')

@app.route('/multiplayer/eng')
@requires_login
def pub_eng():
    return render_template('mType.html', js='js/pubEng.js')

@app.route('/multiplayer/id')
@requires_login
def pub_id():
    return render_template('mType.html', js='js/pubId.js')



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    socketio.run(app)
