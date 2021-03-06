
from app.models import User
from flask_openid import OpenID
import re, requests, time
from app import app
from app import engine
from app import db_session
from flask import url_for, render_template, flash, g, session, \
        redirect
from flask import request
from .forms import xForm
from .forms import signForm
from mandril import drill
import stripe
from stripe import Customer, Charge



con = engine.connect()
app.secret_key = 'super secret key'
STEAM_API_KEY = "1A15D2C82402F944CF5625FC011EF14C"
open_id = OpenID(app)
_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')


@app.route('/')
@app.route('/index')
def index():
    form = xForm()
    g.user = None
    count = 0
    for users in User.query.filter_by(ptype=2):
        if users.paid == 1:
            count += 20 * 0.3
    for users in User.query.filter_by(ptype=1):
        if users.paid == 1:
            count += 5 * 0.3
    output = render_template('index.html',username=g.user,form=form,count=count)
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        if g.user != None:
            ptype = g.user.ptype
            if ptype == '0':
                output = render_template('index.html',username=g.user,form=form,count=count)

            else:
                output = render_template('success.html',username=g.user,form=form)

    return output


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    g.user = None
    form = signForm()
    form2 = xForm()
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

    if form.validate_on_submit():
        print form.email.data
        session['username'] = g.user.nickname
        session['email'] = form.email.data
        session['team'] = form.team.data
        session['website'] = form.website.data
        g.user.email = form.email.data
        g.user.team = form.team.data
        g.user.website = form.website.data

        g.user.member1 = form.member1.data
        g.user.member2 = form.member2.data
        g.user.member3 = form.member3.data
        g.user.member4 = form.member4.data
        db_session.commit()

        return redirect(url_for('terms'))

    if form2.validate_on_submit():
        print form.email.data
        session['username'] = g.user.nickname
        session['email'] = form2.email.data
        g.user.email = form2.email.data


        db_session.commit()

        return redirect(url_for('terms'))

    output = render_template('form.html',username=g.user,form=form)
    return output


@app.route('/select', methods=['GET', 'POST'])
def select():
    g.user = None
    form = xForm()
    form2 = signForm()
    print "%s xxxx"%request.form
    output = render_template('select.html',username=g.user,form=form2)
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        ptype = g.user.ptype
        if ptype != 1 or 2:
            output = render_template('select.html',username=g.user,form=form2)
        else:
            output = render_template('success.html',username=g.user,form=form2)

    if 'player' in request.form:
        g.user.ptype = '1'
        db_session.commit()
        return redirect(url_for("signup"))

    if 'team' in request.form:
        g.user.ptype = '2'
        db_session.commit()
        return redirect(url_for("signup"))
    return output


@app.route("/terms")
def terms():
    output = render_template("terms.html")
    return output


@app.route("/payment")
def payment():
    g.user = None
    form = xForm()
    form2 = signForm()
    team = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        if g.user != None:
            team = g.user.ptype
            print "x is %s"%team
    output = render_template("payment.html",team=team)
    return output


@app.route('/success', methods=['GET', 'POST'])
def success():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


    if g.user.ptype == 1:
        html = "<p>You will be receiving a friend request in steam from a user named xTcR | Tournament [IN]. You will need to accept this friend request to be verified on the date of the tournament.</p><p>The tournament will be on August 15th, 2015 at 1:00pm EST. You and your team will need to be in xTcR's teamspeak (ts3.xtcr.net > INS Tournament Waiting Room) 1 hour before the starting time in order to be verified.</p>"
    else:
        html = "<p>You will be receiving a friend request in steam from a user named xTcR | Tournament [IN]. You will need to accept this friend request to be verified on the date of the tournament.</p><p>The tournament will be on August 15th, 2015 at 1:00pm EST.  You will need to be in teamspeak (ts3.xtcr.net > INS Tournament Waiting Room) 1 and a half hours before the starting time to allow time for teaming up.</p>"
    drill(g.user.email,html)
    print "email %s sent to %s"%(html,g.user.email)
    output = render_template('success.html',username=g.user)

    return output




@app.route('/users', methods=['GET', 'POST'])
def users():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
    team = User.query.order_by(User.nickname)
    print team


    output = render_template('users.html',username=g.user,users=team)

    return output



@app.route('/users/<usr>', methods=['GET', 'POST'])
def userss(usr):
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
    team = User.query.filter_by(steam_id=usr)
    for user in team:
        guy = user

    output = render_template('user.html',username=g.user,users=guy)

    return output





def get_steam_userinfo(steam_id):
    options = {
        'key': STEAM_API_KEY,
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
          'GetPlayerSummaries/v0001'

    r = requests.get(url, params=options)
    rv = r.json()
    return rv['response']['players']['player'][0] or {}

@app.route('/login')
@open_id.loginhandler
def login():
    if g.user is not None:
        flash("You already have a team!")
        return redirect(open_id.get_next_url())
    return open_id.try_login('http://steamcommunity.com/openid')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin', None)
    return redirect(open_id.get_next_url())

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@open_id.after_login
def create_or_login(response):
    form = xForm()
    match = _steam_id_re.search(response.identity_url)
    g.user = User.get_or_create(match.group(1))
    steamdata = get_steam_userinfo(g.user.steam_id)
    g.user.nickname = steamdata['personaname']
    db_session.commit()

    session['user_id'] = g.user.user_id
    session['admin'] = False
    return redirect(url_for("select"))




stripe_keys = {
        'secret_key': "sk_live_GFHD3hslyrBiTy9I2HCEIP7y",
        'publishable_key': "pk_live_MjOyhptp99TO2UUMypnJwckz"
    }



@app.route("/stripe2", methods=['GET', 'POST'])
def stripe2():
    g.user = None
    form = xForm()
    form2 = signForm()
    team = None
    emailz = None
    output = render_template("fail.html")
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        if g.user != None:
            team = g.user.ptype
            emailz = g.user.email

    stripe_token = request.form['stripeToken']
    email = request.form['stripeEmail']
    if team == 1:
        amnt = 5
        print amnt
    else:
        amnt = 20
        print amnt
    try:
        charge = Charge.create(
                amount=int(amnt * 100),
                currency='usd',
                card=stripe_token,
                description=email)
        g.user.paid = 1
        db_session.commit()

        output = render_template('success.html')
        if team == 2:
            html = "<p>You will be receiving a friend request in steam from a user named xTcR | Tournament [IN]. You will need to accept this friend request to be verified on the date of the tournament.</p><p>The tournament will be on August 15th, 2015 at 1:00pm EST. You and your team will need to be in xTcR's teamspeak (ts3.xtcr.net > INS Tournament Waiting Room) 1 hour before the starting time in order to be verified.</p><p>*If you do not recieve a friend request from xTcR | Tournament [IN] please add the user here: http://steamcommunity.com/id/xtcr-tournament/ . You will not be able to be verified for the tournament if you skip this step.</p>"
        else:
            html = "<p>You will be receiving a friend request in steam from a user named xTcR | Tournament [IN]. You will need to accept this friend request to be verified on the date of the tournament.</p><p>The tournament will be on August 15th, 2015 at 1:00pm EST.  You will need to be in teamspeak (ts3.xtcr.net > INS Tournament Waiting Room) 1 and a half hours before the starting time to allow time for teaming up.</p><p>*If you do not recieve a friend request from xTcR | Tournament [IN] please add the user here: http://steamcommunity.com/id/xtcr-tournament/ . You will not be able to be verified for the tournament if you skip this step.</p>"
        drill(g.user.email,html)
    except stripe.CardError, e:
        return render_template("fail.html")



    # stripe.api_key = stripe_keys['secret_key']
    # print "--- begin stripe ---"
    # if request.form['stripeToken']:
    #     print "--- stripe 1 worked ---"
    #     stripe.api_key = "sk_live_GFHD3hslyrBiTy9I2HCEIP7y"
    #     ttest = request.form['stripeToken']
    #     customer = stripe.Customer.create(
    #         email = str(emailz),
    #         source = str(ttest)
    #     )
    #     if team == 1:
    #         amnt = 5
    #         print amnt
    #     else:
    #         amnt = 20
    #         print amnt
    #     charge = Charge.create(
    #         customer=customer.id,
    #         amount=amnt * 100,
    #         currency='usd',
    #         description='xTcR Donation'
    #     )







    return output


