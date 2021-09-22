from flask import Flask
from flask_restplus import Resource, Api, fields
from flask_restplus import reqparse
from flaskext.mysql import MySQL
from werkzeug import validate_arguments
app = Flask(__name__)
api = Api(app)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'covidDatabase'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
#establish connection to SQL Database
conn = mysql.connect()
cursor = conn.cursor()

register_user = api.model("register_user",{
    "name":fields.String(),
    "phoneNumber":fields.String(),
    "pinCode":fields.String()
})

take_assessment = api.model("take_assessment",{
    "userId":fields.Integer(),
    "symptoms":fields.List(fields.String),
    "travelHistory":fields.String(),
    "contactWithCovidPatient":fields.String()
})

update = api.model("update",{
    "userId":fields.Integer(),
    "adminId":fields.Integer(),
    "result":fields.String()
})

@api.route("/registerUser")
class RegisterUser(Resource):
    @api.expect(register_user, validate_arguments =True)
    def post(self,):
        try:
            payload = api.payload
            create_db = "create database if not exists covidDatabase"
            cursor.execute(create_db)
            create_user = "create table if not exists User(userId int AUTO_INCREMENT, name varchar(20), phoneNumber varchar(10), pinCode varchar(6), risk varchar(3),primary key(userId))"
            cursor.execute(create_user)
            insert_user = "insert into User(name, phoneNumber, pinCode) values(%s,%s,%s)"
            data = (payload["name"], payload["phoneNumber"], payload["pinCode"])
            cursor.execute(insert_user,data)
            conn.commit()
            return_id ="select userId from User where name = %s and phoneNumber = %s"
            cursor.execute(return_id,payload['name'], payload['phoneNumber'])
            id = cursor.fetchall()
            print(id)
            return {"userId":id[0][0]}, 200
            
        except Exception as e:
            print(e)
            return e, 500


'''selfAssessment:
Sample request - {"userId":"1","symptoms":["fever","cold","cough"],"travelHistory":"True","contactWithCovidPatient":"True"}
Sample response - {"riskPercentage": 95}'''
@api.route("/selfAssessment")
class SelfAssessment(Resource):
    @api.expect(take_assessment)
    def post(self,):
        try:
            '''No symptoms, No travel history, No contact with covid positive patient - Risk = 5%
Any one symptom, travel history or contact with covid positive patient is "True" - Risk = 50%
Any two symptoms, travel history or contact with covid positive patient is "True" - Risk = 75%
Greater than 2 symptoms, travel history or contact with covid positive patient is "True" - Risk = 95%
'''
            payload = api.payload
            create_db = "create database if not exists covidDatabase"
            cursor.execute(create_db)
            create_user = "create table if not exists User(userId int AUTO_INCREMENT, name varchar(20), phoneNumber varchar(10), pinCode varchar(6), risk varchar(3),primary key(userId))"
            cursor.execute(create_user)
            if len(payload["symptoms"])==0 and payload["travelHistory"]=="True" and payload["contactWithCovidPatient"]=="True":
                Risk = "5%"
            elif len(payload["symptoms"])==1 and (payload["travelHistory"]=="True" or payload["contactWithCovidPatient"]=="True"):
                Risk = "50%"
            elif len(payload["symptoms"])==2 and (payload["travelHistory"]=="True" or payload["contactWithCovidPatient"]=="True"):
                Risk = "75%"
            elif len(payload["symptoms"])>2 and (payload["travelHistory"]=="True" or payload["contactWithCovidPatient"]=="True"):
                Risk = "95%"
            insert_user = "update User set risk = %s where userId =%s"
            data = (Risk, payload["userId"])
            cursor.execute(insert_user,data)
            conn.commit()
            return {"riskPercentage": Risk}

        except:
            print("")


@api.route("/registerAdmin")
class RegisterUser(Resource):
    @api.expect(register_user)
    def post(self,):
        try:
            payload = api.payload
            create_db = "create database if not exists covidDatabase"
            cursor.execute(create_db)
            create_user = "create table if not exists Admin(adminId int AUTO_INCREMENT, name varchar(20), phoneNumber varchar(10), pinCode varchar(6),primary key(adminId))"
            cursor.execute(create_user)
            insert_user = "insert into Admin(name, phoneNumber, pinCode) values(%s,%s,%s)"
            data = (payload["name"], payload["phoneNumber"], payload["pinCode"])
            cursor.execute(insert_user,data)
            conn.commit()
            return_id ="select adminId from Admin where name = %s and phoneNumber = %s"
            cursor.execute(return_id,payload['name'], payload['phoneNumber'])
            id = cursor.fetchall()
            print(id)
            return {"adminId":id[0][0]}
            
        except:
            print("You cannot enter user with same names")


'''updateCovidResult:
Sample request - {"userId":"1","adminId":"2","result":"positive"}
Sample response - {"updated":true}
'''
@api.route("/updateCovidResult")
class updateCovidResult(Resource):
    @api.expect(update)
    def post(self,):
        try:
            payload = api.payload
            create_db = "create database if not exists covidDatabase"
            cursor.execute(create_db)
            create_user = "create table if not exists covidResult(userId int, adminId int, result varchar(10), foreign key(userId) references User(userId), foreign key(adminId) references Admin(adminId));"
            cursor.execute(create_user)
            insert_user = "insert into covidResult(userId, adminId, result) values(%s,%s,%s)"
            data = (payload["userId"], payload["adminId"], payload["result"])
            cursor.execute(insert_user,data)
            conn.commit()
            return {"updated":"true"}
            
        except:
            print("You cannot enter user with same names")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)