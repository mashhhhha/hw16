import json

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# making an application with config
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['JSON_AS_ASCII'] = False

# making a database
db = SQLAlchemy(app)


# creating the 'User' model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)
    phone = db.Column(db.String)


# creating the 'Order' model
class Order(db.Model):

    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String(200))
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    customer = db.relationship('User', foreign_keys=[customer_id])
    executor = db.relationship('User', foreign_keys=[executor_id])

    offer = db.relationship('Offer')


# creating the 'Offer' model
class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    order = db.relationship('Order')
    executor = db.relationship('User')


with app.app_context():
    db.create_all()


# utils for application
def load_json(path):

    with open(path, 'r', encoding='UTF-8') as f:
        return json.load(f)


def fill_table(cls, data):
    with app.app_context():
        for element in data:
            new_element = cls(**element)

            db.session.add(new_element)
        db.session.commit()


def get_dicts_from_user(data):
    response_list = []

    for item in data:
        response_list.append({
            'id': item.id,
            'first_name': item.first_name,
            'last_name': item.last_name,
            'age': item.age,
            'email': item.email,
            'role': item.role,
            'phone': item.phone
        })
    return response_list


def get_dict_from_orders(data):
    response_list = []

    for item in data:
        response_list.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'start_date': item.start_date,
            'end_date': item.end_date,
            'address': item.address,
            'price': item.price,
            'customer_id': item.customer_id,
            'executor_id': item.executor_id
        })
    return response_list


def get_dict_from_offers(data):
    response_list = []

    for item in data:
        response_list.append({
            'id': item.id,
            'order_id': item.order_id,
            'executor_id': item.executor_id,
        })
    return response_list


# load data from json files
fill_table(Offer, load_json('offers.json'))
fill_table(Order, load_json('orders.json'))
fill_table(User, load_json('users.json'))


# creating views
@app.route('/')
def index():
    return 'main page'


@app.route('/users/', methods=['GET', 'POST'])
def get_all_users():
    """GET method returned all users
       POST method add new user"""
    if request.method == 'GET':
        users = User.query.all()
        user_list = get_dicts_from_user(users)

        return jsonify(user_list)

    elif request.method == 'POST':
        user_data = request.json
        new_user = User(**user_data)
        db.session.add(new_user)
        print(new_user)
        db.session.commit()

        return f'Welcome ,{new_user.first_name}!'


@app.route('/users/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_certain_user(pk):
    """GET method returns certain user
       PUT method update cartain user's information
       DELETE method delete certain user """
    if request.method == 'GET':
        user = User.query.get(pk)

        user_dict = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'phone': user.phone
            }

        return jsonify(user_dict)

    elif request.method == 'PUT':
        updated_user = request.json
        old_user = User.query.get(pk)

        old_user.first_name = updated_user['first_name']
        old_user.last_name = updated_user['last_name']
        old_user.age = updated_user['age']
        old_user.email = updated_user['email']
        old_user.role = updated_user['role']
        old_user.phone = updated_user['phone']

        db.session.add(old_user)
        db.session.commit()
        return f'Данные пользователя {old_user.first_name} {old_user.last_name} обновлены'

    elif request.method == 'DELETE':
        user = User.query.get(pk)
        db.session.delete(user)
        db.session.commit()
        return f'Выбранный пользователь удален'


@app.route('/orders/', methods=['GET', 'POST'])
def get_all_orders():
    """GET method returns all orders
       POST method add new order"""
    if request.method == 'GET':
        orders = Order.query.all()
        order_list = get_dict_from_orders(orders)

        return jsonify(order_list)
    elif request.method == 'POST':
        order_data = request.json
        new_order = Order(**order_data)
        db.session.add(new_order)
        db.session.commit()
        return f'Новый заказ {new_order.name} добавлен'


@app.route('/orders/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_certain_order(pk):
    """GET method returns certain user
       PUT method update certain user
       DELETE method delete certain user"""
    if request.method == 'GET':
        order = Order.query.get(pk)
        order_dict = {
                'id': order.id,
                'name': order.name,
                'description': order.description,
                'start_date': order.start_date,
                'end_date': order.end_date,
                'address': order.address,
                'price': order.price,
                'customer_id': order.customer_id,
                'executor_id': order.executor_id
            }

        return jsonify(order_dict)

    elif request.method == 'PUT':
        updated_order = request.json
        old_order = Order.query.get(pk)

        old_order.name = updated_order['name']
        old_order.description = updated_order['description']
        old_order.start_date = updated_order['start_date']
        old_order.end_date = updated_order['end_date']
        old_order.address = updated_order['address']
        old_order.price = updated_order['price']
        old_order.customer_id = updated_order['customer_id']
        old_order.executor_id = updated_order['executor_id']

        db.session.add(old_order)
        db.session.commit()

        return f'Данные заказа {old_order.name} обновлены'

    elif request.method == 'DELETE':
        order = Order.query.get(pk)

        db.session.delete(order)
        db.session.commit()

        return 'Заказ успешно удален'


@app.route('/offers/', methods=['GET', 'POST'])
def get_all_offers():
    if request.method == 'GET':
        offers = Offer.query.all()
        offer_list = get_dict_from_offers(offers)

        return jsonify(offer_list)

    elif request.method == 'POST':
        offer_data = request.json
        new_offer = Offer(**offer_data)
        db.session.add(new_offer)
        db.session.commit()

        return f'Новое предложение добавлено!'


@app.route('/offers/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_certain_offer(pk):
    if request.method == 'GET':
        offer = Offer.query.get(pk)

        offer_dict = {
                'id': offer.id,
                'order_id': offer.order_id,
                'executor_id': offer.executor_id,
            }

        return jsonify(offer_dict)

    elif request.method == 'PUT':
        updated_offer = request.json
        old_offer = Offer.query.get(pk)
        old_offer.order_id = updated_offer['order_id']
        old_offer.executor_id = updated_offer['executor_id']
        db.session.add(old_offer)
        db.session.commit()

        return f'Данные предложения {old_offer.id} успешно обновлены'

    elif request.method == 'DELETE':
        offer = Offer.query.get(pk)
        db.session.delete(offer)
        db.session.commit()

        return f'Предложение успешно удалено'


if __name__ == '__main__':
    app.run()