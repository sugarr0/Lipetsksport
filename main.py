from flask import Flask, redirect, make_response, render_template, request, abort, jsonify
import requests
from data.Cities import City
from data.aboutSport import AboutSport
from data.sport import Sport
from data.athlete import Athletes
from data.users import User
from data.events import Events
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.db_session import global_init, create_session
from forms.loginForm import LoginForm
from forms.athletesForm import AthleteForm
from forms.user import RegisterForm
from forms.sport import SportForm
from forms.addEventForm import EventForm
from requests import get, post
from data import users_resources, resources
from flask_restful import reqparse, abort, Api, Resource
from waitress import serve

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['LOGIN_URL'] = '/login'
login_manager = LoginManager()
s = 0
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    global_init('db/my.db')
    api.add_resource(users_resources.UsersListResource, '/api/users')
    api.add_resource(users_resources.UsersResource, '/api/users/<int:users_id>')
    # app.run()
    serve(app, host='0.0.0.0', port=5000)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    db_sess = create_session()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        res = post("http://127.0.0.1:5000/api/users", json={'email': form.email.data,
                                                            'password': form.password.data,
                                                            'name': form.name.data,
                                                            'surname': form.surname.data,
                                                            'city': resources.get_city_id(request.form['city']),
                                                            }).json()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, cities=db_sess.query(City).all())


@app.route('/sport/<int:ind>', methods=['GET', 'POST'])
@login_required
def sport(ind):
    db_sess = create_session()
    current_user.sport = ind
    db_sess.commit()
    return redirect("/carta")


@app.route('/carta', methods=['GET', 'POST'])
@login_required
def carta():
    db_sess = create_session()
    point = db_sess.query(AboutSport).filter(
        AboutSport.city_id == current_user.city, AboutSport.sport_id == current_user.sport).first()

    toponym_longitude, toponym_lattitude = resources.get_geocod(resources.get_city(current_user.city)).split(" ")

    delta = "0.05"
    pt = ''
    i = 1
    inf = ['' for _ in range(len(point.address.split(';')[:-1]))]
    if point.cont.split(';')[:-1]:
        inf = point.cont.split(';')[:-1]
    info = []
    if point.address is not None:
        for p in point.address.split(';')[:-1]:
            info.append((str(i), f'{p}, {inf[i - 1]}'))
            po = ','.join(resources.get_geocod(p).split(" "))
            pt += f'{po},pm2bll{i}~'
            i += 1
        pt = pt[:-1]

    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join([delta, delta]),
        "l": "map",
        "pt": pt
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    map_file = f"static/img/map{current_user.id}.jpg"
    with open(map_file, "wb") as file:
        file.write(response.content)
    return render_template('carta.html', title=resources.get_sport(current_user.sport),
                           img=f"static/img/map{current_user.id}.jpg",
                           info=info)


@app.route('/sport_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def sport_delete(id):
    db_sess = create_session()
    sp = db_sess.query(AboutSport).filter(AboutSport.sport_id == id,
                                          AboutSport.city_id == current_user.city
                                          ).first()
    if sp:
        db_sess.delete(sp)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/updatesport/<int:ind>', methods=['GET', 'POST'])
@login_required
def updatesport(ind):
    db_sess = create_session()
    n = 0
    sp = db_sess.query(AboutSport).filter(AboutSport.sport_id == ind,
                                          AboutSport.city_id == current_user.city
                                          ).first()
    sprt = db_sess.query(Sport).filter(Sport.id == ind).first()
    if sp and sp.address is not None:
        n = len(sp.address.split(';'))
    elif sp.address is not None:
        n = 1
    if request.method == 'POST':
        p = ''
        inf = ''
        for i in range(n):
            if request.form[f'plase{i}'] == '':
                continue
            else:
                p += str(request.form[f'plase{i}']) + ';'
            if request.form[f'info{i}'] == '':
                inf += ' ;'
            else:
                inf += str(request.form[f'info{i}']) + ';'
        sp.address = p
        sp.cont = inf
        sprt.im1 = str(request.form['url'])
        db_sess.commit()
        return redirect("/")
    if sprt:
        url = sprt.im1
        if sp:
            plases = [(0, '', '')]
            if sp.address is not None:
                for s in range(len(sp.address.split(';')[:-1])):
                    if sp.cont is not None and len(sp.cont.split(';')[:-1]) > s:
                        plases.append((s + 1, sp.address.split(';')[:-1][s], sp.cont.split(';')[:-1][s]))
                    else:
                        plases.append((s + 1, sp.address.split(';')[:-1][s], ''))

            return render_template('updateSport.html', title='Изменить спорт', url=url, arr=plases)


@app.route('/addsport', methods=['GET', 'POST'])
@login_required
def addsport():
    form = SportForm()
    if form.validate_on_submit():
        db_sess = create_session()
        nwsport = db_sess.query(Sport).filter(Sport.sport == form.sport.data.capitalize()).first()
        if nwsport is None:
            newsport = Sport(sport=form.sport.data.capitalize())
            db_sess.add(newsport)
            db_sess.commit()
            nwsport = db_sess.query(Sport).filter(Sport.sport == form.sport.data).first()
            aboutNewSport = AboutSport(sport_id=nwsport.id, city_id=current_user.city)
            db_sess.add(aboutNewSport)
            db_sess.commit()
            return redirect("/")
        else:
            aboutNewSport = AboutSport(sport_id=nwsport.id, city_id=current_user.city)
            db_sess.add(aboutNewSport)
            db_sess.commit()
            return redirect("/")
    return render_template('addsport.html', title='Добавить спорт', form=form)


@app.route('/events', methods=['GET', 'POST'])
def events():
    db_sess = create_session()
    sp = db_sess.query(Sport).all()
    arr = ['Все']
    arr.extend([s.sport for s in sp])
    ev = reversed(db_sess.query(Events).all())
    if request.method == 'POST':
        if request.form['sp'] == 'Все':
            return redirect("/events")
        spr = db_sess.query(Sport).filter(Sport.sport == request.form['sp']).first()
        ev = db_sess.query(Events).filter(Events.sport == spr.id).all()
        return render_template('events.html', title='Мероприятия', events=ev, sports=arr)
    if ev:
        return render_template('events.html', title='Мероприятия', events=ev, sports=arr)
    else:
        return render_template('events.html', title='Мероприятия', events=[], sports=arr)


@app.route('/event_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def event_delete(id):
    db_sess = create_session()
    ev = db_sess.query(Events).filter(Events.id == id).first()
    if ev:
        db_sess.delete(ev)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/events')


@app.route('/athlete_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def athlete_delete(id):
    db_sess = create_session()
    ev = db_sess.query(Athletes).filter(Athletes.id == id).first()
    if ev:
        db_sess.delete(ev)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/athletes')


@app.route('/athlete_add', methods=['GET', 'POST'])
@login_required
def athlete_add():
    form = AthleteForm()
    if form.validate_on_submit():
        db_sess = create_session()
        nwsport = db_sess.query(Sport).filter(Sport.sport == form.sport.data.capitalize()).first()
        if nwsport is None:
            newsport = Sport(sport=form.sport.data.capitalize())
            db_sess.add(newsport)
            db_sess.commit()
        nwsport = db_sess.query(Sport).filter(Sport.sport == form.sport.data.capitalize()).first()
        athlete = Athletes(name=form.name.data,
                           achievement=form.achievement.data,
                           sport_id=nwsport.id,
                           img=form.img.data)
        db_sess.add(athlete)
        db_sess.commit()
        return redirect('/athlete')
    return render_template('addathlete.html', title='Добавить спортсмена',
                           form=form)


@app.route('/event_add', methods=['GET', 'POST'])
@login_required
def event_add():
    form = EventForm()
    if form.validate_on_submit():
        db_sess = create_session()
        if db_sess.query(Events).filter(Events.name == form.name.data).first():
            return render_template('addevent.html', title='Добавить мероприятие',
                                   form=form,
                                   message="Такое мероприятие уже есть")
        nwsport = db_sess.query(Sport).filter(Sport.sport == form.sport.data.capitalize()).first()
        if nwsport is None:
            newsport = Sport(sport=form.sport.data.capitalize())
            db_sess.add(newsport)
            db_sess.commit()
        nwsport = db_sess.query(Sport).filter(Sport.sport == form.sport.data.capitalize()).first()
        ev = Events(name=form.name.data,
                    about=form.about.data,
                    sport=nwsport.id,
                    when=form.when.data,
                    img=form.img.data)
        db_sess.add(ev)
        db_sess.commit()
        return redirect('/events')
    return render_template('addevent.html', title='Добавить мероприятие',
                           form=form)


@app.route('/athletes', methods=['GET', 'POST'])
def athlets():
    db_sess = create_session()
    sports = db_sess.query(Sport).all()
    athlets_dict = {}
    i = 1
    for t in sports:
        athletes = db_sess.query(Athletes).filter(Athletes.sport_id == t.id).all()
        if athletes:
            athlets_dict[(i, t.sport)] = [at for at in athletes]
            i += 1

    return render_template('athletes.html', title='', athletes_keys=[a for a in athlets_dict.keys()],
                           athletes=athlets_dict)


@app.route('/', methods=['POST', 'GET'])
def index():
    if current_user.is_authenticated:
        db_sess = create_session()
        user_city = db_sess.query(City).filter(City.id == current_user.city).first()
        cities = db_sess.query(City).all()
        cities = [user_city.city, *[c.city for c in cities if c.id != user_city.id]]
        sports_in_city = db_sess.query(AboutSport).filter(
            AboutSport.city_id == current_user.city).all()
        sports_id = [s.sport_id for s in sports_in_city]
        sports = db_sess.query(Sport).filter(Sport.id.in_(sports_id)).all()
        if request.method == 'POST':
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.city = resources.get_city_id(request.form['city'])
            db_sess.commit()
            return redirect("/")
        return render_template('index.html', title='Главная', cities=cities, sports=sports)
    else:
        return render_template('index.html', title='Главная')


if __name__ == '__main__':
    main()
