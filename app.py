import json

from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from utils import save_extracted_data_in_new_file, stemming, import_data_from_csv, encode_data_with_bow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class UniqueWords(db.Model):
    id = db.Column('unique_words_id', db.Integer, primary_key=True)
    unique_words = db.Column(db.String(300), unique=False, nullable=False)

    def __init__(self, unique_words):
        self.unique_words = unique_words


class Serializer(db.Model):
    id = db.Column('serialize_id', db.Integer, primary_key=True)
    record_id = db.Column(db.String(80), unique=True, nullable=False)
    vector_data = db.Column(db.String(300), unique=False, nullable=True)

    def __init__(self, record_id, vector_data):
        self.record_id = record_id
        self.vector_data = vector_data


db.create_all()
db.session.commit()


@app.route('/')
def index():
    return render_template('index.html', data=Serializer.query.all())


@app.route('/transform')
def transform_data():
    extracted_data = import_data_from_csv()

    save_extracted_data_in_new_file(extracted_data)
    stemmed_data = stemming(extracted_data)

    data, unique_words = encode_data_with_bow(stemmed_data)

    for record, title in data.items():
        encoded_data = Serializer(record, json.dumps(title))
        db.session.add(encoded_data)

    db.session.add(UniqueWords(json.dumps(unique_words)))
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/record/', methods=['POST'])
@app.route('/record/<string:record_id>', methods=['POST', 'GET'])
def record_view(record_id=None):
    if request.method == 'POST':
        record_id = request.form['record_id']
    return render_template('record.html', data=Serializer.query.filter_by(record_id=record_id).first())


if __name__ == '__main__':
    app.run()
