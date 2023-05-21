import os
#from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for, flash, redirect, send_file, abort, jsonify
from wtforms import HiddenField
import pandas as pd
from datetime import datetime
from flask_login import UserMixin, login_user, login_required, logout_user, LoginManager, current_user
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from flask_sslify import SSLify
#import mysql.connector
#import pymysql.cursors
from modelform import *
import smtplib
from email.message import EmailMessage
from flask_migrate import Migrate
#from modelform import Download
from sqlalchemy import and_, or_,func
import csv
import re
import secrets
from OpenSSL import SSL
context=SSL.Context(SSL.SSLv23_METHOD)
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
load_dotenv()
ALLOWED_EXTENSIONS = set(['xlsx'])
UPLOADS_FOLDER = "/var/www/html/ecsa/static/files"

application = Flask(__name__)
bootstrap = Bootstrap(application)
#x=os.environ['secret_key']

#sslify = SSLify(application)
naomi=os.environ.get('naomi')
application.config['SECRET_KEY'] = str(naomi)
application.config['UPLOADS_FOLDER'] = UPLOADS_FOLDER
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(application)
migrate = Migrate(application, db)
#engine = create_engine('mysql://root:''@localhost/rak')
bcrypt=Bcrypt(application)

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80))
    agent_name=db.Column(db.String(50))
    hrmsID = db.Column(db.String(10))
    bankcode=db.Column(db.String(20))
    bankname = db.Column(db.String(10))
    tlhrmsid=db.Column(db.String(10))
    tlname=db.Column(db.String(50))
    manager = db.Column(db.String(30))
    mngrhrmsid = db.Column(db.String(30))
    coordinator_hrmsid =db.Column(db.String(30))
    location = db.Column(db.String(30))
    userlevel = db.Column(db.String(10))




class Appdata(db.Model):
    #primary columns
    id = db.Column(db.Integer, primary_key=True)
    leadid=db.Column(db.String(30))
    entry_date = db.Column(db.DateTime, nullable=False)

    #agent detection
    agent_id = db.Column(db.String(20), nullable=False) #will be fetched by session user
    agent_name = db.Column(db.String(100)) #will be fetched by session user
    tlhrmsid = db.Column(db.String(100)) #will be fetched by session user
    mngrhrmsid=db.Column(db.String(50))
    crdntr_hrmsid=db.Column(db.String(50))
    agent_location = db.Column(db.String(60)) #will be fetched by session user
    agent_level=db.Column(db.String(10)) #will be fetched by session user

    #Primary customer information
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200))
    gender = db.Column(db.String(10), default="M")
    mobile = db.Column(db.String(20))
    dob = db.Column(db.DateTime)
    salary = db.Column(db.Float)
    nationality = db.Column(db.String(50))
    company = db.Column(db.String(100))
    designation = db.Column(db.String(50))
    ale_status = db.Column(db.String(10))
    office_emirates = db.Column(db.String(100))
    length_of_residence = db.Column(db.String(10))
    length_of_service = db.Column(db.String(10))

    #Secondary customer informatio
    emirates_id = db.Column(db.String(30))
    EID_expiry_date = db.Column(db.DateTime)
    passport_number = db.Column(db.String(10))
    passport_expiry = db.Column(db.DateTime)
    cheque_number = db.Column(db.String(100))
    cheque_bank = db.Column(db.String(100))
    iban = db.Column(db.String(100))
    bankingwith=db.Column(db.String(50))
    visa_expiry_date = db.Column(db.DateTime)
    submissiondate=db.Column(db.DateTime)
    bookingdate=db.Column(db.DateTime)

    # Bank specific group
    bank_name = db.Column(db.String(50))  # Will be fetched by session user
    product_type = db.Column(db.String(100))  # Depends on bank name
    product_name = db.Column(db.String(100))  # Depends on bank name
    bank_reference = db.Column(db.String(100))  # Depends on bank name
    bank_status = db.Column(db.String(100))   # Depends on bank name
    application_type = db.Column(db.String(50))
    supplementary_card = db.Column(db.String(50))
    remarks = db.Column(db.String(500))
    cpv = db.Column(db.String(100))

    # Al Hilal bank specific
    cclimit = db.Column(db.String(90))
    mothername = db.Column(db.String(90))
    uaeaddress = db.Column(db.String(300))
    homecountryaddress = db.Column(db.String(300))
    homecountrynumber = db.Column(db.String(20))
    joiningdate = db.Column(db.DateTime)
    ref1name = db.Column(db.String(100))
    ref2name = db.Column(db.String(100))
    ref1mobile = db.Column(db.String(100))
    ref2mobile = db.Column(db.String(100))
    sent = db.Column(db.DateTime)
    promo = db.Column(db.String(100))

    # CBD bank specific
    last6salaries=db.Column(db.String(10))
    cbdsource=db.Column(db.String(20))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@application.route('/')
def index():
    form=LoginForm()
    return render_template('login3.html', form=form)



@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            g = bcrypt.generate_password_hash(user.password)
            if user.userlevel == "2":
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('success'))
            if user.userlevel=="1":
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('aecb', id=user.hrmsID))
            if user.userlevel in ["2","3","4"]:
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('success'))
            if user.userlevel == "5":
                if bcrypt.check_password_hash(g, form.password.data):
                    login_user(user, remember=True)
                    return redirect(url_for('success'))
        else:
            flash("Invalid user name or password")
            return redirect(url_for('login'))
    return render_template('login3.html', form=form)



@application.route('/success')
@login_required
def success():
    q = request.args.get('q')
    if current_user.userlevel not in ["2","3", "4", "5"]:
        abort(403)
    elif current_user.userlevel =="2":
        if q:
            all_data = Appdata.query.filter(Appdata.customer_email.contains(q)).all()
        else:
            all_data = Appdata.query.filter(and_(Appdata.bank_name==current_user.bankname, Appdata.tlhrmsid==current_user.hrmsID)).all()
    elif current_user.userlevel=="3":
        if q:
            all_data = Appdata.query.filter(Appdata.customer_email.contains(q)).all()
        else:
            all_data = Appdata.query.filter(and_(Appdata.bank_name == current_user.bankname,
                                             Appdata.mngrhrmsid == current_user.hrmsID)).order_by(Appdata.id.desc()).all()
    elif current_user.userlevel=="4":
        if q:
            all_data = Appdata.query.filter(Appdata.customer_email.contains(q)).all()
        else:
            all_data = Appdata.query.filter(and_(Appdata.bank_name == current_user.bankname,
                                             Appdata.crdntr_hrmsid == current_user.hrmsID)).order_by(Appdata.id.desc()).all()
    else:
        if q:
            all_data = Appdata.query.filter(Appdata.customer_email.contains(q)).all()
        else:
            all_data = Appdata.query.order_by(Appdata.id.desc()).all()

    return render_template('success2.html', record=all_data, datetime=datetime)


@application.route('/aecb', methods=['GET', 'POST'])
@login_required
def aecb():
    q = request.args.get('q')
    if q:
        aecb_all = Appdata.query.filter(Appdata.customer_name.contains(q)).order_by(Appdata.id.desc()).all()
    else:
        aecb_all = Appdata.query.filter(Appdata.agent_id == current_user.hrmsID).order_by(Appdata.id.desc()).all()
    return render_template('aecb.html', record=aecb_all, id=id, datetime=datetime, str=str)


# insert data to mysql database via html forms
@application.route('/insert', methods=['GET', 'POST'])
@login_required
def insert():
    form = Appdata1()
    form.cpv.choices=['Verified', 'Not-verified']

    if current_user.userlevel=="1":
        form.bank_status.choices=['InProcess']
    else:
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']

    if (current_user.bankname not in ["ENBD"]) and (current_user.userlevel !="5"):
        abort(403)

    if (current_user.bankname=="ENBD") or (current_user.userlevel=="5"):
        form.product_name.choices=["TITANIUM MASTERCARD","GO 4 IT GOLD VISA CARD","GO 4 IT PLATINUM VISA CARD",
                                   "VISA FLEXI VISA CARD","DNATA PLATINUM MASTERCARD","DNATA WORLD MASTERCARD",
                                   "BUSINESS MASTERCARD","BUSINESS REWARDS SIGNATURE VISA CARD","MANCHESTER UNITED MASTERCARD",
                                   "LULU TITANIUM MASTERCARD","LULU PLATINUM MASTERCARD","U BY EMAAR FAMILY VISA CARD",
                                   "U BY EMAAR SIGNATURE VISA CARD","U BY EMAAR INFINITE VISA CARD","SKYWARDS SIGNATURE VISA CARD",
                                   "SKYWARDS INFINITE VISA CARD","GENERIC INFINITE VISA CARD","MARRIOTT BONVOY WORLD",
                                   "ETHIHAD GUEST VISA INSPIRE","ETHIHAD GUEST VISA ELEVATE","PLATINUM VISA CARD","DUO CREDIT CARD"]
        form.application_type.choices=['PHYSICAL','TAB-StandAlone','Tab-Bundle']


    if form.validate_on_submit():
        appdata = Appdata()

        if (current_user.bankname=="ENBD") or (current_user.userlevel=="5"):
            appdata.leadid = "719" + str(form.mobile.data[-6:]) + "EN23"

        # customer details
        appdata.entry_date=datetime.now()
        appdata.customer_name = form.customer_name.data
        appdata.mobile = form.mobile.data
        appdata.customer_email = form.customer_email.data
        appdata.gender = form.gender.data
        appdata.nationality = form.nationality.data
        appdata.salary = form.salary.data
        appdata.company = form.company.data
        appdata.designation = form.designation.data
        appdata.ale_status = form.ale_status.data
        appdata.office_emirates = form.office_emirates.data
        appdata.length_of_residence = str(form.length_of_residence.data)
        appdata.length_of_service = str(form.length_of_service.data)
        appdata.dob = form.dob.data

        # customer's documents details
        appdata.emirates_id = form.emirates_id.data
        appdata.EID_expiry_date = form.EID_expiry_date.data
        appdata.passport_number = form.passport_number.data
        appdata.passport_expiry = form.passport_expiry.data
        appdata.visa_expiry_date = form.visa_expiry_date.data
        appdata.cheque_number = form.cheque_number.data
        appdata.cheque_bank = form.cheque_bank.data
        appdata.iban = form.iban.data
        appdata.submissiondate=form.submissiondate.data
        appdata.bookingdate=form.bookingdate.data
        appdata.bankingwith=form.bankingwith.data


        # Agent specific details
        appdata.agent_id = current_user.hrmsID
        appdata.agent_name = current_user.agent_name
        appdata.agent_level = current_user.userlevel
        appdata.bank_name = current_user.bankname
        appdata.tlhrmsid = current_user.tlhrmsid
        appdata.mngrhrmsid=current_user.mngrhrmsid
        appdata.crdntr_hrmsid=current_user.coordinator_hrmsid
        appdata.agent_location = current_user.location



        # Bank Specific details
        appdata.product_type = form.product_type.data
        appdata.product_name = form.product_name.data
        appdata.bank_reference = form.bank_reference.data
        appdata.bank_status = form.bank_status.data
        appdata.application_type=form.application_type.data
        appdata.supplementary_card=form.supplementary_card.data
        appdata.remarks=form.remarks.data
        appdata.cpv=form.cpv.data




        # commiting to the database
        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if current_user.userlevel=="1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))

    return render_template('insert.html', form=form)




@application.route('/insert2', methods=['GET', 'POST'])
@login_required
def insert2():
    form = Alhilal()
    usr = User.query.filter_by(hrmsID=current_user.hrmsID).first()

    if usr.userlevel=="1":
        form.bank_status.choices=['InProcess']
    else:
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']
    if (current_user.bankname not in ["ALHILAL"]) and (current_user.userlevel !=5):
        abort(403)

    if form.validate_on_submit():
        appdata = Appdata()
        if (usr.bankname == "ALHILAL") or (current_user.userlevel=="5"):
            appdata.leadid = "779" + str(form.mobile.data[-6:]) + "AH23"

        appdata.customer_name=form.customer_name.data
        appdata.entry_date=datetime.now()
        appdata.mobile=form.mobile.data
        appdata.homecountrynumber=form.homecountrynumber.data
        appdata.salary=form.salary.data
        appdata.bank_reference=form.bank_reference.data
        appdata.cclimit=form.cclimit.data
        appdata.mothername=form.mothername.data
        appdata.company=form.company.data
        appdata.designation=form.designation.data
        appdata.ale_status=form.ale_status.data
        appdata.uaeaddress=form.uaeaddress.data
        appdata.homecountryaddress=form.homecountryaddress.data
        appdata.iban=form.iban.data
        appdata.ref1name=form.ref1name.data
        appdata.ref2name=form.ref2name.data
        appdata.ref1mobile=form.ref1mobile.data
        appdata.ref2mobile=form.ref2mobile.data
        appdata.joiningdate=form.joiningdate.data
        appdata.remarks=form.remarks.data
        appdata.sent=form.sent.data
        appdata.bank_status=form.bank_status.data
        appdata.product_name=form.product_name.data

        # Agent specific details
        appdata.agent_id = usr.hrmsID
        appdata.agent_name = usr.agent_name
        appdata.agent_level = usr.userlevel
        appdata.bank_name = usr.bankname
        appdata.tlhrmsid = usr.tlhrmsid
        appdata.mngrhrmsid = usr.mngrhrmsid
        appdata.crdntr_hrmsid = usr.coordinator_hrmsid
        appdata.agent_location = usr.location

        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if usr.userlevel=="1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))

    return render_template('insert2.html', form=form, user=usr)


@application.route('/insertadcb', methods=['GET', 'POST'])
@login_required
def insertadcb():
    form1 = Appdata1()
    usr = User.query.filter_by(hrmsID=current_user.hrmsID).first()
    form1.cpv.choices=['Verified', 'Not-verified']
    if usr.userlevel == "1":
        form1.bank_status.choices = ['InProcess']
    else:
        form1.bank_status.choices = ['InProcess','Booked','Declined','Approved','Not-workable','Pending-with-sales', 'WIP']

    if (current_user.bankname not in ["ADCB"]) and (current_user.userlevel !="5"):
        abort(403)

    if (usr.bankname == "ADCB") or (current_user.userlevel=="5"):
        form1.product_name.choices = ["43-ETIHAD VISA ETIHAD PLATINUM CARD", "365-CASHBACK ISLAMIC CARD",
                                     "201-VISA ISLAMIC COVERED GOLD","200-VISA ISLAMIC COVERED PLATINUM",
                                      "356-VISA 365 CASHBACK CARD","357-VISA VISA ISLAMIC COVERED",
                                     "132-MASTERCARD WORLD TRAVELLER CREDIT CARD", "119-MASTERCARD SIMPLYLIFE CASHBACK CARD",
                                     "9-MASTERCARD TOUCH POINTS PLATINUM CARD", "8-MASTERCARD TOUCH POINTS TITANIUM CARD",
                                      "14-VISA TOUCH POINTS GOLD CARD","16-VISA TOUCH POINTS PLATINUM CARD",
                                     "32-MASTERCARD LULU PLATINUM CARD", "30-MASTERCARD LULU TITANIUM CARD",
                                      "ADCB INFINITE CARD", "ADCB SIGNATURE CARD ", "CASHBACK CARD", "BETAQTI CARD"]
        form1.application_type.choices = ['ADCB', 'ISLAMIC', 'SIMPLYLIFE']


    form1.gender.validators=[Optional()]
    form1.office_emirates.validators=[Optional()]

    if form1.validate_on_submit():
        appdata = Appdata()

        if (usr.bankname == "ADCB") or (current_user.userlevel=="5"):
            appdata.leadid = "769" + str(form1.mobile.data[-6:]) + "AD23"

        # customer details
        appdata.customer_name = form1.customer_name.data
        appdata.entry_date=datetime.now()
        appdata.mobile = form1.mobile.data
        appdata.customer_email = form1.customer_email.data
        appdata.nationality = form1.nationality.data
        appdata.salary = form1.salary.data
        appdata.company = form1.company.data
        appdata.ale_status = form1.ale_status.data

        # customer's documents details
        appdata.emirates_id = form1.emirates_id.data
        appdata.passport_number = form1.passport_number.data
        appdata.submissiondate = form1.submissiondate.data
        appdata.bookingdate = form1.bookingdate.data


        # Agent specific details
        appdata.agent_id = usr.hrmsID
        appdata.agent_name = usr.agent_name
        appdata.agent_level = usr.userlevel
        appdata.bank_name = usr.bankname
        appdata.tlhrmsid = usr.tlhrmsid
        appdata.mngrhrmsid = usr.mngrhrmsid
        appdata.crdntr_hrmsid = usr.coordinator_hrmsid
        appdata.agent_location = usr.location

        # Bank Specific details
        appdata.product_name = form1.product_name.data
        appdata.bank_reference = form1.bank_reference.data
        appdata.bank_status = form1.bank_status.data
        appdata.application_type = form1.application_type.data
        appdata.remarks = form1.remarks.data
        appdata.cpv = form1.cpv.data
        appdata.promo = form1.promo.data

        # commiting to the database
        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if usr.userlevel == "1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))

    return render_template('insertadcb.html', form=form1, user=usr)



@application.route('/insertscb', methods=['GET', 'POST'])
@login_required
def insertscb():
    form1 = Appdata1()
    usr = User.query.filter_by(hrmsID=current_user.hrmsID).first()
    form1.cpv.choices = ['Verified', 'Not-verified']

    if usr.userlevel == "1":
        form1.bank_status.choices = ['InProcess']
    else:
        form1.bank_status.choices = ['InProcess','Booked','Declined','Dsa-pending','Docs-required']



    if (usr.bankname == "SCB") or (current_user.userlevel=="5"):
        form1.product_name.choices = ["CASHBACK CREDIT CARD", "MANHATTAN REWARD+ CREDIT CARD",
                                      "SAADIQ", "INFINITE"]
        form1.application_type.choices = ['DIGITAL','IPAD']

    if (current_user.bankname not in ["SCB"]) and (current_user.userlevel !="5"):
        abort(403)

    form1.office_emirates.validators=[Optional()]

    if form1.validate_on_submit():
        appdata = Appdata()

        if (usr.bankname == "SCB") or (current_user.userlevel=="5"):
            appdata.leadid = "779" + str(form1.mobile.data[-6:]) + "SC23"

        # customer details
        appdata.customer_name = form1.customer_name.data
        appdata.entry_date=datetime.now()
        appdata.mobile = form1.mobile.data
        appdata.customer_email = form1.customer_email.data
        appdata.gender=form1.gender.data
        appdata.nationality = form1.nationality.data
        appdata.salary = form1.salary.data
        appdata.company = form1.company.data
        appdata.ale_status = form1.ale_status.data
        appdata.designation=form1.designation.data
        appdata.bankingwith=form1.bankingwith.data




        # customer's documents details
        appdata.emirates_id = form1.emirates_id.data
        appdata.submissiondate = form1.submissiondate.data
        appdata.bookingdate = form1.bookingdate.data


        # Agent specific details
        appdata.agent_id = usr.hrmsID
        appdata.agent_name = usr.agent_name
        appdata.agent_level = usr.userlevel
        appdata.bank_name = usr.bankname
        appdata.tlhrmsid = usr.tlhrmsid
        appdata.mngrhrmsid = usr.mngrhrmsid
        appdata.crdntr_hrmsid = usr.coordinator_hrmsid
        appdata.agent_location = usr.location

        # Bank Specific details
        appdata.product_type=form1.product_type.data
        appdata.product_name = form1.product_name.data
        appdata.bank_reference = form1.bank_reference.data
        appdata.bank_status = form1.bank_status.data
        appdata.application_type = form1.application_type.data
        appdata.remarks = form1.remarks.data
        appdata.cpv = form1.cpv.data


        # commiting to the database
        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if usr.userlevel == "1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))

    return render_template('insertscb.html', form=form1, user=usr)




@application.route('/insertcbd', methods=['GET', 'POST'])
@login_required
def insertcbd():
    form1 = Appdata1()
    form1.cpv.choices = ['Verified', 'Not-verified']

    if current_user.userlevel == "1":
        form1.bank_status.choices = ['InProcess','Booked','Declined']
    else:
        form1.bank_status.choices = ['InProcess','Booked','Declined','Dsa-pending','Docs-required']



    if (current_user.bankname == "CBD") or (current_user.userlevel=="5"):
        form1.product_name.choices = ["CBD ONE", "CBD SMILES VISA PLATINUM", "CBD SMILES VISA SIGNATURE", "CBD YES CREDIT CARD",
                                      "SUPER SAVER", "TITANIUM MASTER CARD", "WORLD MASTER CARD"]
        form1.application_type.choices = ['DFC','DCC']

    if (current_user.bankname not in ["CBD"]) and (current_user.userlevel !="5"):
        abort(403)

    form1.office_emirates.validators=[Optional()]
    form1.gender.validators=[Optional()]

    if form1.validate_on_submit():
        appdata = Appdata()

        if (current_user.bankname == "CBD") or (current_user.userlevel=="5"):
            appdata.leadid = "789" + str(form1.mobile.data[-6:]) + "CB23"


        print("If validation is happening print it")
        # customer details
        appdata.customer_name = form1.customer_name.data
        appdata.entry_date=datetime.now()
        appdata.mobile = form1.mobile.data
        appdata.customer_email = form1.customer_email.data
        appdata.nationality = form1.nationality.data
        appdata.salary = form1.salary.data
        appdata.company = form1.company.data
        appdata.ale_status = form1.ale_status.data
        appdata.designation=form1.designation.data
        appdata.bankingwith=form1.bankingwith.data




        # customer's documents details
        appdata.emirates_id = form1.emirates_id.data
        appdata.submissiondate = form1.submissiondate.data
        appdata.bookingdate = form1.bookingdate.data


        # Agent specific details
        appdata.agent_id = current_user.hrmsID
        appdata.agent_name = current_user.agent_name
        appdata.bank_name = current_user.bankname
        appdata.tlhrmsid = current_user.tlhrmsid
        appdata.mngrhrmsid = current_user.mngrhrmsid
        appdata.crdntr_hrmsid = current_user.coordinator_hrmsid
        appdata.agent_location=current_user.location

        # Bank Specific details
        appdata.product_type=form1.product_type.data
        appdata.product_name = form1.product_name.data
        appdata.bank_reference = form1.bank_reference.data
        appdata.bank_status = form1.bank_status.data
        appdata.application_type = form1.application_type.data
        appdata.remarks = form1.remarks.data
        appdata.cpv = form1.cpv.data
        appdata.last6salaries=form1.last6salaries.data
        appdata.cbdsource=form1.cbdsource.data


        # commiting to the database
        db.session.add(appdata)
        db.session.commit()
        flash("Record Inserted Successfully")
        if current_user.userlevel == "1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))

    return render_template('insertcbd.html', form=form1)



@application.route('/updatecbd/<int:id>', methods=['GET', 'POST'])
@login_required
def updatecbd(id):
    data = Appdata.query.get_or_404(id)
    form = Appdata1()
    lst = list(data.__dict__.items())
    dct = dict(lst)
    form.mobile.validators=[Optional()]
    usr = User.query.filter_by(hrmsID=current_user.hrmsID).first()
    form.nationality.choices[0] = data.nationality
    form.ale_status.choices[0]=data.ale_status
    form.gender.validators=[Optional()]
    form.office_emirates.validators=[Optional()]
    form.mobile.validators=[Optional()]

    if current_user.userlevel=="4":
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.cpv.choices=['Verified','Not-verified']
        form.cpv.choices[0]=data.cpv
        form.bank_status.choices[0]=data.bank_status

    if current_user.userlevel=="1":
        form.bank_status.choices=[data.bank_status]
        form.cpv.choices=[data.cpv]
    if (current_user.bankname not in ["CBD"]) and (current_user.userlevel !="5"):
        abort(403)


    if (current_user.userlevel=="4") or (current_user.userlevel=="5"):
        form.product_name.choices = ["CBD ONE", "CBD SMILES VISA PLATINUM", "CBD SMILES VISA SIGNATURE", "CBD YES CREDIT CARD",
                                      "SUPER SAVER", "TITANIUM MASTER CARD", "WORLD MASTER CARD"]
        form.application_type.choices = ['DFC','DCC']
        form.product_name.choices[0]=data.product_name
        form.application_type.choices[0]=data.application_type
    else:
        form.product_name.choices=[data.product_name]
        form.application_type.choices=[data.application_type]


    # dct.pop("entry_date")
    lst_dsrd = ['customer_name', 'customer_email', 'nationality', 'salary', 'company','designation',
                  'ale_status', 'emirates_id', 'passport_number', 'bankingwith', 'product_type', 'product_name', 'bank_reference', 'bank_status',
                'application_type', 'submissiondate','bookingdate', 'supplementary_card','last6salaries','cbdsource','remarks', 'cpv']
    dct_ordered = {k: dct[k] for k in lst_dsrd}
    if form.validate_on_submit():
        data.customer_name = form.customer_name.data
        data.customer_email = form.customer_email.data
        data.nationality = form.nationality.data
        data.salary = form.salary.data
        data.company = form.company.data
        data.designation = form.designation.data
        data.ale_status = form.ale_status.data

        data.emirates_id = form.emirates_id.data
        data.passport_number = form.passport_number.data
        data.bankingwith = form.bankingwith.data

        data.product_type = form.product_type.data
        data.product_name = form.product_name.data
        data.bank_reference = form.bank_reference.data
        data.bank_status = form.bank_status.data

        data.application_type=form.application_type.data
        data.submissiondate=form.submissiondate.data
        data.bookingdate=form.bookingdate.data
        data.supplementary_card=form.supplementary_card.data
        data.last6salaries=form.last6salaries.data
        data.remarks=form.remarks.data
        data.cpv=form.cpv.data


        # for i in lst_dsrd:
        # data.i=form.i.data
        db.session.commit()
        flash("Record Updated Successfully")
        if usr.userlevel=="1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))
    elif request.method == 'GET':
        form_dct = form.data
        #print(form.data)
        dct_ordered_form = {m: form_dct[m] for m in lst_dsrd}
        dct_form = dict(list(zip(dct_ordered_form, dct_ordered.values())))
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('insertcbd.html', form=form, id=id, user=usr)

# update customer record
@application.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    data = Appdata.query.get_or_404(id)
    form = Appdata1()
    lst = list(data.__dict__.items())
    dct = dict(lst)
    form.mobile.validators=[Optional()]
    usr = User.query.filter_by(hrmsID=current_user.hrmsID).first()
    form.nationality.choices[0] = data.nationality
    form.ale_status.choices[0]=data.ale_status

    if current_user.userlevel=="4":
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.cpv.choices=['Verified','Not-verified']
        form.cpv.choices[0]=data.cpv
        form.bank_status.choices[0]=data.bank_status

    if current_user.userlevel=="1":
        form.bank_status.choices=[data.bank_status]
        form.cpv.choices=[data.cpv]
    if (current_user.bankname not in ["ENBD"]) and (current_user.userlevel !="5"):
        abort(403)


    if (current_user.userlevel=="4") or (current_user.userlevel=="5"):
        form.product_name.choices = ["TITANIUM MASTERCARD", "GO 4 IT GOLD VISA CARD", "GO 4 IT PLATINUM VISA CARD",
                                     "VISA FLEXI VISA CARD", "DNATA PLATINUM MASTERCARD", "DNATA WORLD MASTERCARD",
                                     "BUSINESS MASTERCARD", "BUSINESS REWARDS SIGNATURE VISA CARD",
                                     "MANCHESTER UNITED MASTERCARD",
                                     "LULU TITANIUM MASTERCARD", "LULU PLATINUM MASTERCARD",
                                     "U BY EMAAR FAMILY VISA CARD",
                                     "U BY EMAAR SIGNATURE VISA CARD", "U BY EMAAR INFINITE VISA CARD",
                                     "SKYWARDS SIGNATURE VISA CARD",
                                     "SKYWARDS INFINITE VISA CARD", "GENERIC INFINITE VISA CARD",
                                     "MARRIOTT BONVOY WORLD",
                                     "ETHIHAD GUEST VISA INSPIRE", "ETHIHAD GUEST VISA ELEVATE", "PLATINUM VISA CARD"]
        form.application_type.choices = ['PHYSICAL', 'TAB-StandAlone', 'Tab-Bundle']
        form.product_name.choices[0]=data.product_name
        form.application_type.choices[0]=data.application_type
    else:
        form.product_name.choices=[data.product_name]
        form.application_type.choices=[data.application_type]


    # dct.pop("entry_date")
    lst_dsrd = ['customer_name', 'mobile', 'customer_email', 'gender', 'nationality', 'salary', 'company','designation',
                  'ale_status', 'office_emirates', 'length_of_residence', 'length_of_service',
                'dob', 'emirates_id', 'EID_expiry_date','passport_number', 'passport_expiry','cheque_number', 'cheque_bank','iban',
                'visa_expiry_date', 'product_type', 'product_name', 'bank_reference', 'bank_status','bankingwith','submissiondate','bookingdate',
                'application_type', 'supplementary_card', 'remarks', 'cpv']
    dct_ordered = {k: dct[k] for k in lst_dsrd}
    if form.validate_on_submit():
        data.customer_name = form.customer_name.data
        data.customer_email = form.customer_email.data
        data.gender = form.gender.data
        data.nationality = form.nationality.data
        data.salary = form.salary.data
        data.company = form.company.data
        data.designation = form.designation.data
        data.ale_status = form.ale_status.data
        data.office_emirates = form.office_emirates.data
        data.length_of_residence = str(form.length_of_residence.data)
        data.length_of_service = str(form.length_of_service.data)
        data.dob = form.dob.data




        data.emirates_id = form.emirates_id.data
        data.EID_expiry_date = form.EID_expiry_date.data
        data.passport_number = form.passport_number.data
        data.passport_expiry = form.passport_expiry.data
        data.cheque_number = form.cheque_number.data
        data.cheque_bank = form.cheque_bank.data
        data.bankingwith = form.bankingwith.data
        data.iban = form.iban.data

        data.visa_expiry_date = form.visa_expiry_date.data
        data.product_type = form.product_type.data
        data.product_name = form.product_name.data
        data.bank_reference = form.bank_reference.data
        data.bank_status = form.bank_status.data

        data.application_type=form.application_type.data
        data.submissiondate=form.submissiondate.data
        data.bookingdate=form.bookingdate.data
        data.supplementary_card=form.supplementary_card.data
        data.remarks=form.remarks.data
        data.cpv=form.cpv.data


        # for i in lst_dsrd:
        # data.i=form.i.data
        db.session.commit()
        flash("Record Updated Successfully")
        if usr.userlevel=="1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))
    elif request.method == 'GET':
        form_dct = form.data
        #print(form.data)
        dct_ordered_form = {m: form_dct[m] for m in lst_dsrd}
        dct_form = dict(list(zip(dct_ordered_form, dct_ordered.values())))
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('update.html', form=form, id=id, user=usr)


@application.route('/updateadcb/<int:id>', methods=['GET', 'POST'])
@login_required
def updateadcb(id):
    data = Appdata.query.get_or_404(id)
    form = Appdata1()
    lst = list(data.__dict__.items())
    dct = dict(lst)
    form.mobile.validators = [Optional()]
    usr = User.query.filter_by(hrmsID=current_user.hrmsID).first()
    form.nationality.choices[0] = data.nationality
    form.ale_status.choices[0]=data.ale_status

    if current_user.userlevel == "1":
        form.bank_status.choices = [data.bank_status]
        form.cpv.choices=[data.cpv]
    else:
        form.bank_status.choices = ['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.bank_status.choices[0]=data.bank_status
        form.cpv.choices=['Verified','Not-verified']
        form.cpv.choices[0]=data.cpv


    if (current_user.bankname not in ["ADCB"]) and (current_user.userlevel !="5"):
        abort(403)

    if (current_user.userlevel == "4") or (current_user.userlevel=="5"):
        form.product_name.choices = ["ADCB INFINITE CARD", "ADCB SIGNATURE CARD ", "CASHBACK CARD", "BETAQTI CARD",
                                      "ADCB ETIHAD GUEST INFINITE CARD", "ADCB ETIHAD GUEST SIGNATURE CARD",
                                      "ADCB ETIHAD GUEST PLATINUM CARD",
                                      "TRAVELLER CREDIT CARD", "TOUCH POINTS INFINITE CARD",
                                      "TOUCH POINTS PLATINUM CARD", "TOUCH POINTS TITANIUM/GOLD CARD",
                                      "LULU PLATINUM CARD", "LULU TITANIUM CARD"]
        form.application_type.choices = ['CONVENTIONAL', 'ISLAMIC']
        form.application_type.choices[0]=data.application_type
        form.product_name.choices[0]=data.product_name
    else:
        form.product_name.choices=[data.product_name]
        form.application_type.choices=[data.application_type]

    # dct.pop("entry_date")
    lst_dsrd = ['customer_name', 'mobile', 'customer_email', 'nationality', 'salary', 'company',
                'ale_status', 'emirates_id', 'passport_number', 'product_type', 'product_name', 'bank_reference',
                'bank_status','application_type', 'submissiondate', 'bookingdate', 'promo', 'remarks', 'cpv']
    dct_ordered = {k: dct[k] for k in lst_dsrd}

    form.mobile.validators=[Optional()]
    form.gender.validators=[Optional()]
    form.office_emirates.validators=[Optional()]


    if form.validate_on_submit():
        data.customer_name = form.customer_name.data
        data.customer_email = form.customer_email.data
        data.nationality = form.nationality.data
        data.salary = form.salary.data
        data.company = form.company.data
        data.ale_status = form.ale_status.data
        data.emirates_id = form.emirates_id.data
        data.passport_number = form.passport_number.data
        data.product_type = form.product_type.data
        data.product_name = form.product_name.data
        data.bank_reference = form.bank_reference.data
        data.bank_status = form.bank_status.data

        data.application_type = form.application_type.data
        data.submissiondate = form.submissiondate.data
        data.bookingdate = form.bookingdate.data
        data.remarks = form.remarks.data
        data.cpv = form.cpv.data
        data.promo=form.promo.data
        #print("Are you coming here")
        # for i in lst_dsrd:
        # data.i=form.i.data
        db.session.commit()
        flash("Record Updated Successfully")
        if usr.userlevel == "1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))
    elif request.method == 'GET':
        form_dct = form.data
        # print(form.data)
        dct_ordered_form = {m: form_dct[m] for m in lst_dsrd}
        dct_form = dict(list(zip(dct_ordered_form, dct_ordered.values())))
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('updateadcb.html', form=form, id=id, user=usr)


@application.route('/updatehilal/<int:id>', methods=['GET', 'POST'])
@login_required
def updatehilal(id):
    data2 = Appdata.query.get_or_404(id)
    form = Alhilal()
    lst = list(data2.__dict__.items())
    dct = dict(lst)
    form.ale_status.choices[0]=data2.ale_status

    # This is the way to override original form validation of any field.
    form.mobile.validators=[Optional()]
    if current_user.userlevel=="1":
        form.bank_status.choices=[data2.bank_status]

    else:
        form.bank_status.choices=['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.bank_status.choices[0]=data2.bank_status


    if (current_user.bankname not in ["ALHILAL"]) and (current_user.userlevel !="5"):
        abort(403)

    lst_dsrd = ['customer_name', 'mobile',  'salary', 'company','designation','ale_status', 'iban', 'product_name','bank_reference',
                'bank_status', 'remarks', 'cclimit', 'mothername', 'uaeaddress', 'homecountryaddress', 'homecountrynumber',
                'joiningdate', 'ref1name', 'ref2name','ref1mobile', 'ref2mobile','sent', 'bookingdate']
    dct_ordered = {k: dct[k] for k in lst_dsrd}
    if form.validate_on_submit():
        #print("Print if its reaching here")
        data2.customer_name=form.customer_name.data
        data2.homecountrynumber=form.homecountrynumber.data
        data2.salary=form.salary.data
        data2.bank_reference=form.bank_reference.data
        data2.cclimit=form.cclimit.data
        data2.mothername=form.mothername.data
        data2.company=form.company.data
        data2.designation=form.designation.data
        data2.ale_status=form.ale_status.data
        data2.uaeaddress=form.uaeaddress.data
        data2.homecountryaddress=form.homecountryaddress.data
        data2.iban=form.iban.data
        data2.ref1name=form.ref1name.data
        data2.ref2name=form.ref2name.data
        data2.ref1mobile=form.ref1mobile.data
        data2.ref2mobile=form.ref2mobile.data
        data2.joiningdate=form.joiningdate.data
        data2.remarks=form.remarks.data
        data2.bank_status=form.bank_status.data
        data2.product_name=form.product_name.data
        data2.sent=form.sent.data
        data2.bookingdate = form.bookingdate.data

        db.session.commit()

        flash("Record Updated Successfully")
        if current_user.userlevel == "1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))
    elif request.method == 'GET':
        form_dct = form.data
        # print(form.data)
        dct_ordered_form = {m: form_dct[m] for m in lst_dsrd}
        dct_form = dict(list(zip(dct_ordered_form, dct_ordered.values())))
        #print(dct_form)
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('update2.html', form=form, id=id, user=current_user)



@application.route('/updatescb/<int:id>', methods=['GET', 'POST'])
@login_required
def updatescb(id):
    data = Appdata.query.get_or_404(id)
    form = Appdata1()
    lst = list(data.__dict__.items())
    dct = dict(lst)
    form.mobile.validators = [Optional()]
    form.nationality.choices[0] = data.nationality
    form.ale_status.choices[0]=data.ale_status

    if current_user.userlevel == "1":
        form.bank_status.choices = [data.bank_status]
        form.cpv.choices=[data.cpv]
    else:
        form.bank_status.choices = ['InProcess','Booked','Declined','Dsa-pending','Docs-required']
        form.bank_status.choices[0]=data.bank_status
        form.cpv.choices=['Verified', 'Not-verified']
        form.cpv.choices[0]=data.cpv

    if (current_user.bankname not in ["SCB"]) and (current_user.userlevel !="5"):
        abort(403)

    if (current_user.userlevel =="4") or (current_user.userlevel =="5"):
        form.product_name.choices = ["CASHBACK CREDIT CARD", "MANHATTAN REWARD+ CREDIT CARD",
                                      "SAADIQ", "INFINITE"]

        form.application_type.choices = ['DIGITAL','IPAD']
        form.product_name.choices[0]=data.product_name
        form.application_type.choices[0]=data.application_type
    else:
        form.application_type.choices=[data.application_type]
        form.product_name.choices=[data.product_name]

    # dct.pop("entry_date")
    lst_dsrd = ['customer_name', 'mobile', 'customer_email', 'gender', 'nationality', 'salary', 'company','designation',
                'ale_status', 'emirates_id', 'bankingwith', 'product_type', 'product_name', 'bank_reference',
                'bank_status','application_type', 'submissiondate','supplementary_card', 'bookingdate',
                'remarks']
    dct_ordered = {k: dct[k] for k in lst_dsrd}

    form.mobile.validators=[Optional()]
    form.gender.validators=[Optional()]
    form.office_emirates.validators=[Optional()]


    if form.validate_on_submit():
        data.customer_name = form.customer_name.data
        data.customer_email = form.customer_email.data
        data.gender = form.gender.data
        data.nationality = form.nationality.data
        data.salary = form.salary.data
        data.company = form.company.data
        data.designation=form.designation.data
        data.ale_status = form.ale_status.data
        data.emirates_id = form.emirates_id.data
        data.bankingwith=form.bankingwith.data
        data.product_type = form.product_type.data
        data.product_name = form.product_name.data
        data.bank_reference = form.bank_reference.data
        data.bank_status = form.bank_status.data

        data.application_type = form.application_type.data
        data.submissiondate = form.submissiondate.data
        data.supplementary_card=form.supplementary_card.data
        data.bookingdate = form.bookingdate.data
        data.remarks = form.remarks.data
        #print("Are you coming here")
        # for i in lst_dsrd:
        # data.i=form.i.data
        db.session.commit()
        flash("Record Updated Successfully")
        if current_user.userlevel == "1":
            return redirect(url_for('aecb'))
        else:
            return redirect(url_for('success'))
    elif request.method == 'GET':
        form_dct = form.data
        # print(form.data)
        dct_ordered_form = {m: form_dct[m] for m in lst_dsrd}
        dct_form = dict(list(zip(dct_ordered_form, dct_ordered.values())))
        for i in dct_form.keys():
            if isinstance(dct_form[i], datetime):
                form[i].data = dct_form[i]
            elif isinstance(dct_form[i], float):
                form[i].data = int(dct_form[i])
            else:
                form[i].data = dct_form[i]
    return render_template('updatescb.html', form=form, id=id)

@application.route('/download', methods=['GET', 'POST'])
@login_required
def download():
    global data
    if current_user.userlevel not in ["4","5"]:
        abort(403)
    form = Download(request.form)
    if form.validate_on_submit():
        sd1 = form.start.data
        ed1 = form.end.data
        st = form.stime.data
        et = form.etime.data
        sd2 = datetime.combine(sd1,st)
        ed2 = datetime.combine(ed1,et)

        #print(sd2,ed2)
        #print(str(sd2), str(ed2))

        if ed2 < sd2:
            raise ValidationError("End date must not be less than Start date")

        if current_user.userlevel =="4":
            data = Appdata.query.filter(and_(Appdata.crdntr_hrmsid==current_user.hrmsID,
                                         func.datetime(Appdata.entry_date)>=str(sd2), func.datetime(Appdata.entry_date)<=str(ed2))).all()
        if current_user.userlevel =="5":
            data = Appdata.query.filter(and_(func.date(Appdata.entry_date) >= str(sd2),
                                             func.date(Appdata.entry_date) <= str(ed2))).all()
        lst_enbd = ['leadid','entry_date','agent_hrmsid','agent_code','mngrhrmsid', 'agent_name', 'customer_name','customer_email',
                    'gender', 'mobile',  'dob', 'salary','nationality', 'company', 'designation', 'ale_status',
                    'office_emirate', 'HRLandline', 'los', 'emirates_id','emiratesid_expiry','passport',
                    'cheque_number', 'cheque_bank', 'iban', 'bank_name', 'product_type',  'product_name',
                     'bank_reference', 'bank_status', 'application_type', 'submission_date','remarks', 'cpv', 'booking_date']

        lst_hilal = ['leadid','entry_date','agent_id','tlhrmsid','mngrhrmsid', 'agent_name', 'customer_name', 'mobile', 'salary',
                   'company','designation','ale_status', 'iban', 'cclimit', 'mothername', 'uaeaddress', 'homecountryaddress',
                     'homecountrynumber','joiningdate', 'ref1name', 'ref2name','ref1mobile', 'ref2mobile',
                     'product_name','bank_reference','bank_status','sent','bookingdate', 'remarks']

        lst_adcb = ['leadid', 'entry_date', 'agent_code', 'customer_name', 'passport', 'salary',
                    'mobile', 'emirates_id', 'company', 'promo', 'nationality', 'ale_status', 'product_name',
                    'application_type', 'agent_name', 'tlname', 'mngrname', 'customer_email', 'bank_reference',
                    'bank_status', 'remarks', 'cpv', 'bookingdate']

        lst_scb = ['leadid', 'entry_date', 'agent_id', 'mngrhrmsid', 'agent_name', 'bank_reference','application_type',
                   'customer_name', 'mobile','company','salary','designation','nationality','ale_status','customer_email',
                    'gender', 'emirates_id', 'salary_account', 'product_type', 'product_name',
                     'bank_status',  'submission_date', 'remarks', 'booking_date']

        lst_cbd = ['leadid', 'entry_date', 'agent_code', 'application_type','customer_name','mobile','product_name',
                   'bank_status', 'remarks', 'nationality', 'company', 'designation', 'salary','customer_email',
                   'salary_account','last6salaries', 'ale_status', 'supplementary_card', 'agent_name', 'bank_reference',
                   'emirates_id', 'cpv', 'booking_date']

        if current_user.bankname=='CBD':
            with open(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter=csv.writer(csvfile,delimiter=",")
                csvwriter.writerow(lst_cbd)
                for p in data:
                    bank_code = User.query.filter_by(hrmsID=p.agent_id).first()
                    if bank_code:
                        bankcode=bank_code.bankcode
                    else:
                        bankcode="NA"
                    csvwriter.writerow([p.leadid, datetime.date(p.entry_date), bankcode, p.application_type,str(p.customer_name).upper(),
                                        p.mobile,p.product_name,p.bank_status,p.remarks,p.nationality,str(p.company).upper(),
                                        str(p.designation).upper(),p.salary,str(p.customer_email).upper(),p.bankingwith,p.last6salaries,
                                        p.ale_status,p.supplementary_card,str(p.agent_name).upper(),p.bank_reference,
                                        p.emirates_id, p.cpv, p.bookingdate])
            return send_file(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", mimetype='text/csv', as_attachment=True)

        if current_user.bankname=='ENBD':
            with open(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter=csv.writer(csvfile,delimiter=",")
                csvwriter.writerow(lst_enbd)
                for p in data:
                    bank_code = User.query.filter_by(hrmsID=p.agent_id).first()
                    if bank_code:
                        bankcode = bank_code.bankcode
                    else:
                        bankcode="NA"
                    csvwriter.writerow([p.leadid, datetime.date(p.entry_date),p.agent_id, bankcode,p.mngrhrmsid,str(p.agent_name).upper(),str(p.customer_name).upper(),
                                        str(p.customer_email).upper(),p.gender, p.mobile,p.dob, p.salary, p.nationality, str(p.company).upper(), str(p.designation).upper(),
                                        p.ale_status, p.office_emirates, p.length_of_residence,
                                        p.length_of_service, str(p.emirates_id), p.EID_expiry_date, p.passport_number,
                                        p.cheque_number, p.cheque_bank, p.iban,p.bankingwith, p.product_type, p.product_name,
                                        str(p.bank_reference),p.bank_status, p.application_type,p.submissiondate,p.remarks,p.cpv, p.bookingdate])
            return send_file(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", mimetype='text/csv', as_attachment=True)

        elif current_user.bankname=="ALHILAL":
            with open(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=",")
                csvwriter.writerow(lst_hilal)
                for p in data:
                    csvwriter.writerow(
                        [p.leadid, datetime.date(p.entry_date),p.agent_id, p.tlhrmsid,p.mngrhrmsid,p.agent_name,p.customer_name,
                         p.mobile,p.salary, p.company, p.designation, p.ale_status, p.iban, p.cclimit,p.mothername,p.uaeaddress,
                         p.homecountryaddress,p.homecountrynumber,p.joiningdate,p.ref1name,p.ref2name,p.ref1mobile,p.ref2mobile,
                         p.product_name,p.bank_reference,p.bank_status,p.sent,p.bookingdate,p.remarks])
            return send_file(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", mimetype='text/csv',
                             as_attachment=True)

        elif current_user.bankname=="ADCB":
            with open(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=",")
                csvwriter.writerow(lst_adcb)
                for p in data:
                    eid=p.emirates_id
                    if eid:
                        eid2 = str.join("-",re.findall('(\w{3})(\w{4})(\w{7})(\w{1})', eid)[0])
                    else:
                        eid2=eid

                    bank_code = User.query.filter_by(hrmsID=p.agent_id).first()
                    if bank_code:
                        bankcode = bank_code.bankcode
                        tlname=bank_code.tlname
                        manager=bank_code.manager
                    else:
                        bankcode="NA"
                        tlname="NA"
                        manager="NA"
                    csvwriter.writerow(
                      [p.leadid, datetime.date(p.entry_date), bankcode, str(p.customer_name).upper(),str(p.passport_number).upper(),
                       p.salary, p.mobile, eid2, str(p.company).upper(),str(p.promo).upper(),p.nationality,str(p.ale_status).upper(),
                       str(p.product_name).upper(),str(p.application_type).upper(),str(p.agent_name).upper(),
                       tlname,manager, str(p.customer_email).upper(),str(p.bank_reference).upper(),
                    str(p.bank_status).upper(), str(p.remarks).upper(), p.cpv, p.bookingdate])
            return send_file(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", mimetype='text/csv',
                             as_attachment=True)

        elif current_user.bankname=="SCB":
            with open(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", 'w',encoding='UTF8', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=",")
                csvwriter.writerow(lst_scb)
                for p in data:
                    csvwriter.writerow(
                        [p.leadid, datetime.date(p.entry_date),p.agent_id, p.mngrhrmsid,p.agent_name,p.bank_reference,p.application_type,p.customer_name,p.mobile,p.company,p.salary,p.designation,
                         p.nationality,p.ale_status,p.customer_email, p.gender,
                         p.emirates_id,p.bankingwith,p.product_type, p.product_name,p.bank_status,
                         p.submissiondate,p.remarks, p.bookingdate])
            return send_file(f"/var/www/html/ecsa/static/all_record_{current_user.hrmsID}.csv", mimetype='text/csv',
                             as_attachment=True)

        else:
            lst_admin=list(data[0].__dict__.keys())
            with open("/var/www/html/ecsa/static/all_record_admin.csv",'w',encoding='UTF8',newline='') as csvfile:
                csvwriter=csv.writer(csvfile,delimiter=',')
                csvwriter.writerow(lst_admin[1:])
                for p in data:
                    dct = p.__dict__
                    dct.pop('_sa_instance_state')
                    lst_dct=dct.values()
                    csvwriter.writerow(lst_dct)
            return send_file("/var/www/html/ecsa/static/all_record_admin.csv", mimetype='text/csv', as_attachment=True)

    return render_template('download.html', form=form)


# Create Login

@application.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.userlevel != "5":
        abort(403)
    form = Create()
    if form.validate_on_submit():
        usr = User()
        usr.username = form.username.data
        usr.password = form.password.data
        usr.hrmsID=form.hrmsid.data
        usr.userlevel = form.usergroup.data
        usr.location = form.location.data
        usr.agent_name = form.name.data
        usr.bankname = form.department.data
        usr.mngrhrmsid=form.mngrhrmsid.data
        usr.manager=form.manager.data
        usr.tlhrmsid=form.tlhrmsid.data
        usr.coordinator_hrmsid=form.crdntrhrmsid.data


        usr2 = User.query.filter(or_(User.username == usr.username, User.hrmsID == usr.hrmsID)).first()
        if usr2:
            flash("User already exist with this hrmsID or username")
            return render_template('create.html', form=form)
        else:
            db.session.add(usr)
            db.session.commit()
            flash("User created successfully")
            return redirect(url_for('users'))
    return render_template('create.html', form=form)


@application.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.userlevel != "5":
        abort(403)
    record = User.query.filter(User.userlevel != "5").all()
    return render_template('users.html', record=record)


@application.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    if current_user.userlevel != "5":
        abort(403)
    x = Appdata.query.filter_by(id=id).first()
    db.session.delete(x)
    db.session.commit()
    flash("Record deleted successfully")
    return redirect(url_for('success'))


@application.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    if current_user.userlevel != "5":
        abort(403)
    x = User.query.filter_by(id=id).first()
    db.session.delete(x)
    db.session.commit()
    flash("User deleted successfully")
    return redirect(url_for('users'))

@application.route('/updateuser/<int:id>', methods=['GET', 'POST'])
@login_required
def updateuser(id):
    if current_user.userlevel !="5":
        abort(403)

    data2 = User.query.get_or_404(id)
    form = Create()
    if form.validate_on_submit():
        data2.username = form.username.data
        data2.password = form.password.data
        data2.hrmsID = form.hrmsid.data
        data2.bankname=form.department.data
        data2.manager=form.manager.data
        data2.location=form.location.data
        data2.userlevel=form.usergroup.data
        data2.agent_name=form.name.data
        data2.mngrhrmsid=form.mngrhrmsid.data
        data2.tlhrmsid=form.tlhrmsid.data
        data2.coordinator_hrmsid=form.crdntrhrmsid.data

        db.session.commit()
        flash("User updated successfully")
        return redirect(url_for('users'))

    elif request.method == "GET":
        form.username.data=data2.username
        form.password.data=data2.password
        form.hrmsid.data=data2.hrmsID
        form.department.data=data2.bankname
        form.manager.data=data2.manager
        form.location.data=data2.location
        form.usergroup.data=data2.userlevel
        form.name.data=data2.agent_name
        form.mngrhrmsid.data=data2.mngrhrmsid
        form.crdntrhrmsid.data=data2.coordinator_hrmsid
        form.tlhrmsid.data=data2.tlhrmsid

    return render_template('updateuser.html', form=form, id=id)

@application.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
        if current_user.userlevel not in ["4","5"]:
            abort(403)
        form = Upload()
        lst_not_updated=[]
        lst_updated=[]
        if form.validate_on_submit():
            file = form.upload.data
            if file and allowed_file(file.filename):
                file.filename = "data_bankstatus" + str(current_user.hrmsID) + str(datetime.date(datetime.utcnow())) + ".xlsx"
                filename = secure_filename(file.filename)
                file.save(os.path.join(application.config['UPLOADS_FOLDER'], filename))
                df=pd.read_excel(f'/var/www/html/ecsa/static/files/{filename}')
                lst_df = list(df.columns)
                lst_df= [x.strip() for x in lst_df]
                lst_df = [x.lower() for x in lst_df]
                df.columns = lst_df
                ar = df.iloc[:,0].values
                ar2 = df.iloc[:,1].values
                df.iloc[:,2] = pd.to_datetime(df.iloc[:,2])
                ar3 = df.iloc[:,2].values

                if (df.isnull().sum().sum())>0:
                    flash("You uploaded a file which has null values. System will not process it.")
                    return redirect(url_for('upload'))
                else:
                    for i in range(len(ar)):
                        if str(ar2[i]).strip().capitalize() not in ['InProcess','Booked','Declined','Approved',"Not-workable","Pending-with-sales","Wip"]:
                            flash(f"second column must have any one of [InProcess,Booked,Declined,Approved,Not-workable, Pending-with-sales, Wip], {i}th cell in second column has invalid value \'{ar2[i]}\'")
                            return redirect(url_for('upload'))
                        else:
                            row = Appdata.query.filter_by(leadid=str(ar[i])).order_by(Appdata.id.desc()).first()
                            if row:
                                lst_updated.append(str(ar[i]))
                                row.bank_status=str(ar2[i]).strip().capitalize()
                                row.bookingdate=ar3[i]
                                db.session.commit()
                            else:
                                lst_not_updated.append(str(ar[i]))
                    flash(f"{len(lst_updated)} records are updated and {len(lst_not_updated)} records are not matched, not matched leadids are {lst_not_updated}")
                    return redirect(url_for('upload'))
            else:
                flash("Not uploaded, please upload only xlsx file")
                return redirect(url_for('upload'))
        return render_template('upload.html', form=form)



@application.route('/upload_cpv', methods=['GET', 'POST'])
@login_required
def upload_cpv():
        if current_user.userlevel not in ["4","5"]:
            abort(403)
        form = Upload()
        lst_not_updated=[]
        lst_updated=[]
        if form.validate_on_submit():
            file = form.upload.data
            if file and allowed_file(file.filename):
                file.filename = "data_cpv" + str(current_user.hrmsID) + str(datetime.date(datetime.utcnow())) + ".xlsx"
                filename = secure_filename(file.filename)
                file.save(os.path.join(application.config['UPLOADS_FOLDER'], filename))
                df=pd.read_excel(f'/var/www/html/ecsa/static/files/{filename}')
                lst_df = list(df.columns)
                lst_df= [x.strip() for x in lst_df]
                lst_df = [x.lower() for x in lst_df]
                df.columns = lst_df
                ar = df.iloc[:,0].values
                ar2 = df.iloc[:,1].values

                if (df.isnull().sum().sum())>0:
                    flash("You uploaded a file which has null values. System will not process it.")
                    return redirect(url_for('upload_cpv'))
                else:
                    for i in range(len(ar2)):
                        #ar2[i]=str(ar2[i]).strip().capitalize().replace(" ", "_")
                        #ar2[i]="".join(y.capitalize() for y in ar2[i].split("_"))
                        if str(ar2[i]).strip().capitalize() not in ['Verified','Not-verified']:
                            flash(f"Second column must have any one of [Verified, Not-verified] value, {i}th cell in second column has invalid value \'{ar2[i]}\'")
                            return redirect(url_for('upload_cpv'))
                        else:
                            row = Appdata.query.filter_by(leadid=str(ar[i])).order_by(Appdata.id.desc()).first()
                            if row:
                                lst_updated.append(str(ar[i]))
                                row.cpv=str(ar2[i]).strip().capitalize()
                                db.session.commit()
                            else:
                                lst_not_updated.append(str(ar[i]))
                    flash(f"{len(lst_updated)} records are updated and {len(lst_not_updated)} records are not matched, not matched leadids are {lst_not_updated}")
                    return redirect(url_for('upload_cpv'))
            else:
                flash("Not uploaded, please upload only xlsx file")
                return redirect(url_for('upload_cpv'))
        return render_template('upload_cpv.html', form=form)


@application.route('/upload_bankref', methods=['GET', 'POST'])
@login_required
def upload_bankref():
        if current_user.userlevel not in ["4","5"]:
            abort(403)
        form = Upload()
        lst_not_updated=[]
        lst_updated=[]
        if form.validate_on_submit():
            file = form.upload.data
            if file and allowed_file(file.filename):
                file.filename = "data_bankref" + str(current_user.hrmsID) + str(datetime.date(datetime.utcnow())) + ".xlsx"
                filename = secure_filename(file.filename)
                file.save(os.path.join(application.config['UPLOADS_FOLDER'], filename))
                df=pd.read_excel(f'/var/www/html/ecsa/static/files/{filename}')
                lst_df = list(df.columns)
                lst_df= [x.strip() for x in lst_df]
                lst_df = [x.lower() for x in lst_df]
                df.columns = lst_df
                ar = df.iloc[:,0].values
                ar2 = df.iloc[:,1].values

                if (df.isnull().sum().sum())>0:
                    flash("You uploaded a file which has null values. System will not process it.")
                    return redirect(url_for('upload_bankref'))
                else:
                    for i in range(len(ar2)):
                        #ar2[i]=str(ar2[i]).strip().capitalize().replace(" ", "_")
                        #ar2[i]="".join(y.capitalize() for y in ar2[i].split("_"))
                        row = Appdata.query.filter_by(leadid=str(ar[i])).order_by(Appdata.id.desc()).first()
                        if row:
                            lst_updated.append(str(ar[i]))
                            row.bank_reference=str(ar2[i]).strip().capitalize()
                            db.session.commit()
                        else:
                            lst_not_updated.append(str(ar[i]))
                    flash(f"{len(lst_updated)} records are updated and {len(lst_not_updated)} records are not matched, not matched leadids are {lst_not_updated}")
                    return redirect(url_for('upload_bankref'))
            else:
                flash("Not uploaded, please upload only xlsx file")
                return redirect(url_for('upload_bankref'))
        return render_template('upload_bankref.html', form=form)

@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    application.run(debug=True)