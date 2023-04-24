from flask_wtf import FlaskForm
from wtforms import Form, DateTimeField, SubmitField, StringField, PasswordField, BooleanField, IntegerField, \
    SelectField, ValidationError, DateField, FileField,DecimalField,HiddenField
from wtforms.validators import NumberRange, Email, InputRequired, Length, Regexp, DataRequired, Optional
import pandas as pd
from wtforms_components import TimeField

#from app import current_user, request

from application import current_user, request


df = pd.read_csv("static/nationality.csv")
lst = list(range(1, 226))
lst2 = list(zip(lst, df['Nationality']))
lst3 = list(df['Nationality'])


def length(min=-1, max=-1):
    message = 'Must only have %d digits and must start with 05' % (min)

    def _length(form, field):
        x = field.data
        l = field.data and len(field.data) or 0
        if not x.startswith("05"):
            raise ValidationError("It should start with 05")
        if not x.isdigit():
            raise ValidationError("Mobile number must only have numbers")
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length


def length2(min=-1, max=-1):
    message = 'Must be between %d and %d characters long.' % (min, max)

    def _length(form, field):
        x = field.data
        if not x.isdigit():
            raise ValidationError("Only numbers are allowed")
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length


def length3(min=-1, max=-1):
    message = 'Must be %d characters long.' % (max)

    def _length(form, field):
        x = field.data
        if not x.startswith("784"):
            raise ValidationError("It must start with 784 and must have 15 digits")
        if not x.isdigit():
            raise ValidationError("Only numbers are allowed")
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length


def length4(min=-1, max=-1):
    message = 'Must be %d characters long.' % (max)

    def _length(form, field):
        x = field.data
        if not x.startswith("AE"):
            raise ValidationError("It must start with AE and must have 23 digits")
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class Customer1(FlaskForm):
    agent_id = StringField('AgentID', validators=[InputRequired(), length2(5, 10)])
    customer_name = StringField('CustomerName', validators=[InputRequired(), Length(min=6, max=100)])
    customer_email = StringField('CustomerEmail', validators=[DataRequired(), Email(message="Invalid Email Address")])
    gender = SelectField('Gender', validators=[InputRequired()],
                         choices=[(1, "Please Select Gender"), ("M", "Male"), ("F", "Female")], default=1)
    dob = DateTimeField('DOB', validators=[InputRequired()], format="%Y-%m-%d")
    emirates_id = StringField('EmiratesID', validators=[InputRequired(), length3(15, 15)])
    mobile = StringField('Mobile', validators=[DataRequired(), length(min=10, max=10)])
    passport_number = StringField('Passport', validators=[InputRequired(), Length(min=6, max=8)])
    nationality = SelectField('Nationality', validators=[InputRequired()], choices=lst3, default=1)
    salary = IntegerField('Salary', validators=[InputRequired(), NumberRange(min=5000, max=150000)])
    product = StringField('Product', validators=[InputRequired(), Length(min=5, max=30)])
    company = StringField('Company', validators=[InputRequired(), Length(min=4, max=100)])
    submit = SubmitField('Submit')


class Appdata1(FlaskForm):
    customer_name = StringField('Name', validators=[InputRequired(), Length(min=6, max=100)])
    mobile = StringField('Mobile', validators=[DataRequired(), length(10,10)])

    customer_email = StringField('Email', validators=[DataRequired(), Email(message="Invalid Email Address")])
    gender = SelectField('Gender', validators=[InputRequired()],
                         choices=["MALE","FEMALE"])
    nationality = SelectField('Nationality', validators=[InputRequired()], choices=lst3, default=1)
    salary = DecimalField('Salary', validators=[InputRequired(), NumberRange(min=5000, max=150000)])
    company = StringField('Company', validators=[InputRequired(), Length(min=4, max=100)])
    designation = StringField("Designation", validators=[Optional()])
    ale_status = SelectField("TML/NTML", validators=[Optional()], choices=["TML", "NTML"])
    office_emirates = SelectField("OfficeEmirates", validators=[InputRequired()], choices=["AbuDhabi", "AlAin","Ajman","Dubai","Fujairah","RasAlKhaima","Sharjah", "UmmAlQuwain"])
    length_of_residence = StringField("Landline(HR)", validators=[Optional(),length2(min=1, max=840)])
    length_of_service = StringField("LOS(Months)", validators=[Optional(),length2(min=1, max=840)])
    dob = DateField('DOB', validators=[Optional()])

    emirates_id = StringField('EmiratesID', validators=[Optional(), length3(15, 15)])
    EID_expiry_date = DateField("ExpireOn", validators=[Optional()])
    passport_number = StringField('Passport', validators=[Optional(), Length(min=6, max=20)])
    passport_expiry = DateField("ExpireOn", validators=[Optional()])
    cheque_number = StringField("ChequeNumber", validators=[Optional()])
    cheque_bank = StringField("ChequeBank", validators=[Optional()])
    bankingwith=SelectField("SalaryAccount", validators=[Optional()], choices=["ADCB", "ENBD", "MASHREQ", "RAK", "CBD", "SCB", "HSBC", "DIB",
                                                                                "FAB","CBI","EIB", "OTHER"])
    iban = StringField("IBAN", validators=[Optional()])
    visa_expiry_date = DateField("VisaExpiryDate", validators=[Optional()])

    product_type = SelectField('Product_type', validators=[InputRequired()],choices=[("CreditCard", "CreditCard"), ("Loan", "Loan")], default="CreditCard")
    product_name = SelectField('ProductName', validators=[InputRequired()])
    bank_reference = StringField("BankReference", validators=[Optional()])
    bank_status = SelectField("BankStatus", validators=[Optional()], choices=[], default="Inprocess")
    application_type=SelectField("ApplicationType", validators=[Optional()], choices=[])
    submissiondate = DateField("SubmissionDate", validators=[Optional()])
    bookingdate = DateField("BookingDate", validators=[Optional()])
    supplementary_card=SelectField("SupplCard", validators=[Optional()], choices=['NotRequired', 'Required'],default="NotRequired")
    remarks=StringField("Remarks", validators=[Optional()])
    cpv=SelectField("CPV", validators=[Optional()])
    submit = SubmitField('Submit')
    promo = SelectField("Promo", validators=[Optional()], choices=['AECB', 'NCC', 'STC', 'CHLD', 'EMRT'])


    # Al Hilal Bank specific fields.
class Alhilal(FlaskForm):
    salary = DecimalField('Salary', validators=[InputRequired(), NumberRange(min=5000, max=150000)])
    company = StringField('Company', validators=[InputRequired(), Length(min=4, max=100)])
    designation = StringField("Designation", validators=[Optional()])
    ale_status = SelectField("CompanyStatus", validators=[Optional()], choices=["TML", "NTML"], default="TML")
    customer_name = StringField('CustomerName', validators=[InputRequired(), Length(min=6, max=100)])
    mobile = StringField('Mobile', validators=[DataRequired(),length(10,10)])
    iban = StringField("IBAN", validators=[InputRequired(),length4(23,23)])
    cclimit = StringField("CC-Limit", validators=[InputRequired(), length2(min=1, max=20)])
    mothername = StringField("MotherName", validators=[InputRequired()])
    uaeaddress = StringField("UAEAddress", validators=[InputRequired()])
    homecountryaddress = StringField("HomeCountryAddress", validators=[InputRequired()])
    homecountrynumber = StringField("HomeCountryNumber", validators=[InputRequired(), length2(10,15)])
    joiningdate = DateField("DateOfJoining", validators=[InputRequired()])
    ref1name = StringField("Ref1-Name", validators=[InputRequired()])
    ref2name = StringField("Ref2-Name", validators=[InputRequired()])
    ref1mobile = StringField("Ref1-Mobile", validators=[DataRequired(), length(10,10)])
    ref2mobile = StringField("Ref2-Mobile", validators=[DataRequired(), length(10,10)])
    sent = DateField("Sent", validators=[Optional()])
    remarks = StringField("Remarks", validators=[Optional()])
    bank_reference = StringField("BankReference", validators=[Optional()])
    bank_status = SelectField("BankStatus", validators=[Optional()], choices=[])
    product_name = SelectField("CardName", validators=[InputRequired()],
                               choices=['CashBack', 'Etihad Guest Infinite Card'])
    bookingdate = DateField("BookingDate", validators=[Optional()])

    submit = SubmitField('Submit')

    #def validate_mobile(self, mobile):
        #if (current_user.userlevel=="1") & (request.method=="GET"):
            #mobile.type=HiddenField()
        #else:
            #mobile.validators=[DataRequired(), length(10,10)]



class Download(FlaskForm):
    start = DateField("StartDate", validators=[InputRequired()], format="%Y-%m-%d")
    end = DateField("EndDate", validators=[InputRequired()], format="%Y-%m-%d")
    stime=TimeField("StartTime")
    etime = TimeField("EndTime")
    download = SubmitField("Download")



class Create(FlaskForm):
    username = StringField("UserName", validators=[InputRequired()])
    password = StringField("Password", validators=[InputRequired()])
    hrmsid=StringField("AgntHRMS", validators=[InputRequired()])
    department = SelectField("Department", choices=['ENBD', 'EIB', 'RAK', 'ADCB', 'SCB', 'CBD', 'ALHILAL'])
    name = StringField("AgentName", validators=[InputRequired()])

    location = SelectField("Location", validators=[InputRequired()], choices=['ABU DHABI', 'ALAIN', 'DUBAI', 'RAK', 'FUJAIRAH', 'SHARJAH', 'AJMAN'])
    usergroup = SelectField("UserGroup", validators=[InputRequired()], choices=["1","2","3","4"])
    tlhrmsid = StringField("TLhrms", validators=[InputRequired()])
    mngrhrmsid=StringField("MngrHRMS", validators=[InputRequired()])
    manager = StringField("MngrName", validators=[InputRequired()])
    crdntrhrmsid=StringField("CrdntrID", validators=[InputRequired()])

    CreateUser=SubmitField("CreateUser")

class Upload(FlaskForm):
    upload = FileField("Upload")
    uploadfile = SubmitField("UploadFile")

