from flask import Flask, render_template, g, request, session, redirect, url_for, jsonify, make_response, Blueprint
from flask_restplus import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os, re
from os import path

app = Flask(__name__)
blueprint_topbaby = Blueprint('api_topbaby', __name__, url_prefix='/api_topbaby')
blueprint_topbabynames = Blueprint('api_topbabynames', __name__, url_prefix='/api_topbabynames')
blueprint_opaltrain = Blueprint('api_opaltrain', __name__, url_prefix='/api_opaltrain')
blueprint_opaltraincardtype = Blueprint('api_opaltraincardtype', __name__, url_prefix='/api_opaltraincardtype')
blueprint_contingentworkforce = Blueprint('api_contingentworkforce', __name__, url_prefix='/api_contingentworkforce')
blueprint_acnc = Blueprint('api_acnc', __name__, url_prefix='/api_acnc')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    messages = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Messages('{self.name}', '{self.email}', '{self.messages}')"

@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/acnc_data_profile', methods=['GET', 'POST'])
def acnc_data_profile():
    return render_template('acnc_data_profile.html')

########################################################################################################################
# NSW birth rate API
########################################################################################################################
api = Api(blueprint_topbaby, doc='/documentation', version='1.0', title='Data Service for NSW birth rate information by suburb',
          description='This is a Flask-RESTPlus data service that allows a client to consume APIs related to NSW birth rate information by suburb.',
          )
app.register_blueprint(blueprint_topbaby)

#Database helper
ROOT = path.dirname(path.realpath(__file__))
def connect_db_topbaby():
    sql = sqlite3.connect(path.join(ROOT, "NSW_BIRTH_RATE.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_topbaby():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_topbaby()
    return g.sqlite_db

@api.route('/topbaby/all')
class TopBabyAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all suburbs.')
    def get(self):
        db = get_db_topbaby()
        details_cur = db.execute('select YEAR, LOCALITY, SUBURB, STATE, POSTCODE, COUNT from NSW_BIRTH_RATE')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['YEAR'] = detail['YEAR']
            detail_dict['LOCALITY'] = detail['LOCALITY']
            detail_dict['SUBURB'] = detail['SUBURB']
            detail_dict['STATE'] = detail['STATE']
            detail_dict['POSTCODE'] = detail['POSTCODE']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/topbaby/<string:SUBURB>', methods=['GET'])
class TopBabySuburb(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for one suburb.')
    def get(self, SUBURB):
        db = get_db_topbaby()
        details_cur = db.execute(
            'select YEAR, LOCALITY, SUBURB, STATE, POSTCODE, COUNT from NSW_BIRTH_RATE where SUBURB = ? COLLATE NOCASE', [SUBURB])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['YEAR'] = detail['YEAR']
            detail_dict['LOCALITY'] = detail['LOCALITY']
            detail_dict['SUBURB'] = detail['SUBURB']
            detail_dict['STATE'] = detail['STATE']
            detail_dict['POSTCODE'] = detail['POSTCODE']
            detail_dict['COUNT'] = detail['COUNT']\

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# NSW Top baby names from 2010 to 2018 API
########################################################################################################################
api = Api(blueprint_topbabynames, doc='/documentation', version='1.0', title='Data Service for top 100 Popular Baby Names from 2010 to 2018 in NSW',
          description='This is a Flask-Restplus data service that allows a client to consume APIs related to top 100 popular baby names from 2010 and 2018 in NSW.',
          )

app.register_blueprint(blueprint_topbabynames)

#Database helper
ROOT = path.dirname(path.realpath(__file__))
def connect_db_topbabynames():
    sql = sqlite3.connect(path.join(ROOT, "PopularBabyName.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_topbabynames():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_topbabynames()
    return g.sqlite_db

@api.route('/topbabynames/all')
class TopBabyNamesAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all.')
    def get(self):
        db = get_db_topbabynames()
        details_cur = db.execute('select NAME, GENDER, YEAR, NUMBER from PopularBN')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['NAME'] = detail['NAME']
            detail_dict['GENDER'] = detail['GENDER']
            detail_dict['YEAR'] = detail['YEAR']
            detail_dict['NUMBER'] = detail['NUMBER']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/topbabynames/all/<string:YEAR>/<string:GENDER>', methods=['GET'])
class TopBabyNamesYearGender(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for specific year and sex.')
    @api.doc(params={'GENDER': 'fill in boys/girls, case-insensitive','YEAR':'e.g. 2018'})
    def get(self, YEAR, GENDER):
        db = get_db_topbabynames()
        details_cur = db.execute(
            'select NAME, GENDER, YEAR, NUMBER from PopularBN where YEAR = ? COLLATE NOCASE and GENDER = ? COLLATE NOCASE', [YEAR, GENDER])
        details = details_cur.fetchall()
        return_values = []
        for detail in details:
            detail_dict = {}
            detail_dict['NAME'] = detail['NAME']
            detail_dict['GENDER'] = detail['GENDER']
            detail_dict['YEAR'] = detail['YEAR']
            detail_dict['NUMBER'] = detail['NUMBER']\

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# NSW Train Opal Trips (July 2016 to April 2019) API
########################################################################################################################
api = Api(blueprint_opaltrain, version='1.0', doc='/documentation', title='Data Service for NSW train line monthly Opal trips covering July 2016 to April 2019.',
          description='This is a Flask-RESTPlus data service that allows a client to consume APIs related to NSW train line monthly Opal trips from July 2016 to April 2019.',
          )

app.register_blueprint(blueprint_opaltrain)

# Database helper
def connect_db_opaltrain():
    sql = sqlite3.connect(path.join(ROOT, "NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_opaltrain():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_opaltrain()
    return g.sqlite_db

@api.route('/opaltrain/all')
class NSWOpalAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all train lines.')
    def get(self):
        db = get_db_opaltrain()
        details_cur = db.execute('select TRAIN_LINE, PERIOD, COUNT from NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/opaltrain/all/period/<string:PERIOD>', methods=['GET'])
class NSWOpalPeriod(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database selected period.')
    def get(self, PERIOD):
        db = get_db_opaltrain()
        details_cur = db.execute(
            'select TRAIN_LINE, PERIOD, COUNT from NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019 where PERIOD = ? COLLATE NOCASE',
            [PERIOD])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/opaltrain/all/trainline/<string:TRAIN_LINE>', methods=['GET'])
class NSWOpalTrainLine(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for selected train line.')
    def get(self, TRAIN_LINE):
        db = get_db_opaltrain()
        details_cur = db.execute(
            'select TRAIN_LINE, PERIOD, COUNT from NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019 where TRAIN_LINE like ? COLLATE NOCASE',
            ["%" + TRAIN_LINE + "%"])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/opaltrain/all/TRAIN_LINE/PERIOD/<string:TRAIN_LINE>/<string:PERIOD>', methods=['GET'])
class NSWOpalTrainLinePeriod(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for selected train line and period.')
    def get(self, TRAIN_LINE, PERIOD):
        db = get_db_opaltrain()
        details_cur = db.execute(
            'select TRAIN_LINE, PERIOD, COUNT from NSW_TRAIN_OPAL_TRIPS_JULY_2016_APRIL_2019 where (TRAIN_LINE like ? COLLATE NOCASE and PERIOD = ? COLLATE NOCASE)',
            ["%" + TRAIN_LINE + "%", PERIOD])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# NSW Train Opal Card Type Monthly Figures (July 2016 to April 2019) API
########################################################################################################################
api = Api(blueprint_opaltraincardtype, version='1.0', doc='/documentation', title='Data Service for NSW opal card type monthly figures. July 2016 to April 2019.',
          description='This is a Flask-Restplus data service that allows a client to consume APIs related to NSW opal card type monthly figures. July 2016 to April 2019.',
          )

app.register_blueprint(blueprint_opaltraincardtype)

# Database helper
def connect_db_opaltraincardtype():
    sql = sqlite3.connect(path.join(ROOT, "NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_opaltraincardtype():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_opaltraincardtype()
    return g.sqlite_db

@api.route('/opaltraincardtype/all')
class NSWOpalAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all train lines.')
    def get(self):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, CARD_TYPE, PERIOD, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/opaltraincardtype/all/TRAIN_LINE/<string:TRAIN_LINE>', methods=['GET'])
class NSWOpalTrainLine(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for selected train line.')
    def get(self, TRAIN_LINE):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, CARD_TYPE, PERIOD, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019 where TRAIN_LINE like ? COLLATE NOCASE',
            ["%" + TRAIN_LINE + "%"])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/opaltraincardtype/all/CARD_TYPE/<string:CARD_TYPE>', methods=['GET'])
class NSWOpalCardType(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database selected CARD_TYPE.')
    def get(self, CARD_TYPE):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, CARD_TYPE, PERIOD, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019 where CARD_TYPE = ? COLLATE NOCASE',
            [CARD_TYPE])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/opaltraincardtype/all/PERIOD/<string:PERIOD>', methods=['GET'])
class NSWOpalPeriod(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database selected PERIOD.')
    def get(self, PERIOD):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, CARD_TYPE, PERIOD, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019 where PERIOD = ? COLLATE NOCASE',
            [PERIOD])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)


@api.route('/opaltraincardtype/all/TRAIN_LINE/PERIOD_or_CARD/<string:TRAIN_LINE>/<string:PERIOD_or_CARD>', methods=['GET'])
class NSWOpalTrainLinePeriodCardType(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database selected TRAIN LINE and PERIOD or CARD.')
    def get(self, TRAIN_LINE, PERIOD_or_CARD):
        db = get_db_opaltraincardtype()
        details_cur = db.execute(
            'select TRAIN_LINE, PERIOD, CARD_TYPE, COUNT from NSW_OPAL_CARD_TYPE_JULY_2016_APRIL_2019 where (TRAIN_LINE like ? COLLATE NOCASE) AND (PERIOD = ? COLLATE NOCASE OR CARD_TYPE = ? COLLATE NOCASE)',
            ["%" + TRAIN_LINE + "%", PERIOD_or_CARD, PERIOD_or_CARD])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['TRAIN_LINE'] = detail['TRAIN_LINE']
            detail_dict['CARD_TYPE'] = detail['CARD_TYPE']
            detail_dict['PERIOD'] = detail['PERIOD']
            detail_dict['COUNT'] = detail['COUNT']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# NSW Total Worked Hours per Contingent Workforce
########################################################################################################################
api = Api(blueprint_contingentworkforce, doc='/documentation', version='1.0', title='Data Service for NSW Total Hours Worked per Contingent Workforce 2019',
          description='This is a Flask-Restplus data service that allows a client to consume APIs related to Contingent Workforce YTD total hours worked per supplier in NSW.',
          )

app.register_blueprint(blueprint_contingentworkforce)

#Database helper
ROOT = path.dirname(path.realpath(__file__))
def connect_db_contingentworkforce():
    sql = sqlite3.connect(path.join(ROOT, "YTDWorkedHours.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_contingentworkforce():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_contingentworkforce()
    return g.sqlite_db

@api.route('/contingentworkforce/all')
class YTDWorkedHours(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database showing Supplier, Industry, TotalHours).')
    def get(self):
        db = get_db_contingentworkforce()
        details_cur = db.execute('select Supplier, Industry, TotalHours from YTDWorkedHours')
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['Supplier'] = detail['Supplier']
            detail_dict['Industry'] = detail['Industry']
            detail_dict['TotalHours'] = detail['TotalHours']

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/contingentworkforce/all/<string:Industry>', methods=['GET'])
class YTDWorkedHoursIndustry(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for specific industry.')
    @api.doc(params={"Industry":'Choose from the list Education|Eligible Customers|External to GovernmentSector|Family and Community Services|Finance|Services and Innovation|Health|Industry|Justice|Planning and Environment|Premier and Cabinet|Transport|Treasury|Grand Total'})
    def get(self, Industry):
        db = get_db_contingentworkforce()
        details_cur = db.execute(
            'select Supplier, Industry, TotalHours from YTDWorkedHours where Industry = ? COLLATE NOCASE', [Industry])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['Supplier'] = detail['Supplier']
            detail_dict['Industry'] = detail['Industry']
            detail_dict['TotalHours'] = detail['TotalHours']\

            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

########################################################################################################################
# ACNC Data
########################################################################################################################
api = Api(blueprint_acnc, doc='/documentation', version='1.0', title='Data Service for ACNC data from FY 2014 through 2017',
          description='This is a Flask-Restplus data service that allows a client to consume APIs related to charity information, compiled by the ACNC across mutliple years.',
          )

app.register_blueprint(blueprint_acnc)

#Database helper
ROOT = path.dirname(path.realpath(__file__))

def connect_db_acnc():
    sql = sqlite3.connect(path.join(ROOT, "acnc.sqlite"))
    sql.row_factory = sqlite3.Row
    return sql

def get_db_acnc():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db_acnc()
    return g.sqlite_db

@api.route('/all')
class CharityAll(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for all charities and all years.')
    def get(self):
        db = get_db_acnc()
        stmt_all = """
        select
            source
            , abn
            , charity_name
            , main_activity
            , how_purposes_were_pursued
            , postcode
        from
            charities
        limit 10
        """

        details_cur = db.execute(stmt_all)
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['source'] = detail['source']
            detail_dict['abn'] = detail['abn']
            detail_dict['charity_name'] = detail['charity_name']
            detail_dict['main_activity'] = detail['main_activity']
            detail_dict['how_purposes_were_pursued'] = detail['how_purposes_were_pursued']
            detail_dict['postcode'] = detail['postcode']
            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

@api.route('/all/<string:abn>', methods=['GET'])
class CharityABN(Resource):
    @api.response(200, 'SUCCESSFUL: Contents successfully loaded')
    @api.response(204, 'NO CONTENT: No content in database')
    @api.doc(description='Retrieving all records from the database for a given charity ABN.')
    def get(self, abn):
        db = get_db_acnc()
        stmt_one = """
        select
            source
            , abn
            , charity_name
            , main_activity
            , how_purposes_were_pursued
            , postcode
            , staff___full_time
            , donations_and_bequests
        from
            charities
        where
            abn = ? collate nocase
        """

        details_cur = db.execute(stmt_one,[abn])
        details = details_cur.fetchall()

        return_values = []

        for detail in details:
            detail_dict = {}
            detail_dict['source'] = detail['source']
            detail_dict['abn'] = detail['abn']
            detail_dict['charity_name'] = detail['charity_name']
            detail_dict['main_activity'] = detail['main_activity']
            detail_dict['how_purposes_were_pursued'] = detail['how_purposes_were_pursued']
            detail_dict['postcode'] = detail['postcode']
            detail_dict['staff___full_time'] = detail['staff___full_time']
            detail_dict['donations_and_bequests'] = detail['donations_and_bequests']
            return_values.append(detail_dict)

        return make_response(jsonify(return_values), 200)

if __name__ == '__main__':
    app.run(debug=True)
