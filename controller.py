from models import *

import json
from datetime import datetime
from flask import Flask, render_template, request
from sqlalchemy import and_, or_
import random

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    # record = get_all_record()
    prizes = session.query(Prize).all()
    users = session.query(User).filter(User.active == 1).all()
    user_ids = [u.id for u in users]
    return render_template('index.html', prizes=prizes, user_ids=user_ids)


@app.route('/res/<int:lround>/', methods=['POST', 'GET'])
def lottery_result(lround):
    prizes = session.query(Prize).filter(Prize.lottery_round == lround).all()
    prize_ids = [p.id for p in prizes]
    prize_d = {p.id: {'desc': p.desc, 'users': []} for p in prizes}
    keys = prize_d.keys()
    if lround in [6,12]:
        users = session.query(User).filter(User.global_prize_id.in_(prize_ids)).all()
        for user in users:
            if user.global_prize_id in keys:
                prize_d[user.global_prize_id]['users'].append(user.id)
    else:
        users = session.query(User).filter(or_(User.single_prize_id.in_(prize_ids),
                                               User.external_prize_id.in_(prize_ids))).all()
        for user in users:
            if user.single_prize_id in keys:
                prize_d[user.single_prize_id]['users'].append(user.id)
            if user.external_prize_id in keys:
                prize_d[user.external_prize_id]['users'].append(user.id)
    # return list(prize_d.values())
    return render_template('result.html', lottery_res=list(prize_d.values()), lottery_round=lround)


@app.route('/lottery', methods=['POST'])
def lottery():
    data = json.loads(request.get_data())
    prize_id = data.get('prize_id')
    prize_info = session.query(Prize).filter(Prize.id == int(prize_id)).first()
    if prize_info.is_global:
        global_user_id = 0
        if prize_info.lottery_round == 6:
            global_user_id = 88
        elif prize_info.lottery_round == 12:
            global_user_id = 0
        if global_user_id == 0:
            users = session.query(User).filter(User.active == 1, User.global_prize_id == 0).all()
        else:
            users = session.query(User).filter(User.active == 1, User.global_prize_id == 0,
                                               User.id == global_user_id).all()
    else:
        users = session.query(User).filter(User.active == 1, User.single_prize_id == 0).all()
    user_ids = [u.id for u in users]
    if len(user_ids) < prize_info.prize_count:
        fill_users = session.query(User).filter(User.active == 1, User.external_prize_id == 0).all()
        fill_user_ids = [u.id for u in fill_users]
        user_ids += random.sample(fill_user_ids, prize_info.prize_count - len(user_ids))
    lucy_ids = random.sample(user_ids, prize_info.prize_count)
    if prize_info.is_global:
        session.query(User).filter(User.id.in_(lucy_ids)).update({User.global_prize_id: prize_id})
    else:
        update_users = session.query(User).filter(User.id.in_(lucy_ids)).all()
        for uu in update_users:
            if uu.single_prize_id == 0:
                uu.single_prize_id = prize_id
            else:
                uu.external_prize_id = prize_id
    session.commit()
    session.close()
    return json.dumps({"result": lucy_ids})


@app.route('/add', methods=['POST'])
def add_record():
    if request.method != 'POST':
        return json.dumps({"result": 0})
    data = json.loads(request.get_data())
    data['date'] = datetime.strptime(data['date'], "%Y-%m-%d").date()
    if find_value(data['id']):
        return json.dumps({"result": -1})
    add_value(data)
    return json.dumps({"result": 1})


@app.route('/del', methods=['POST'])
def del_record():
    if request.method != 'POST':
        return json.dumps({"result": 0})
    data = json.loads(request.get_data())
    id = data.values()
    del_value(id)
    if (find_value(id)):
        return json.dumps({"result": -1})
    return json.dumps({"result": 1})


def add_value(data):
    id, name, tem, date = data.values()
    session.add(Record(id=id, name=name, temperature=tem, date=date))
    session.commit()
    session.close()


def del_value(id):
    session.query(Record).filter(Record.id == id).delete()
    session.commit()
    session.close()


def find_value(id):
    res = session.query(Record).filter(Record.id == id).all()
    return True if res else False


def get_all_record():
    return session.query(Record).all()