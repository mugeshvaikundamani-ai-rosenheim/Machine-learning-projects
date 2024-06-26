from flask import Flask, request
import requests
import secrets
import Database as db
import joblib
from Api_key_encryption import sha256

model = joblib.load('Models/model_exam_score.joblib')

app = Flask(__name__)

@app.errorhandler(404)
def not_found_error(error):
    return {
        'Status':"Error 404: Not Found"
        ,'Type':404
    }

@app.route("/v2/<api_key>", methods=['GET'])
def index(api_key):
    Hashed_api_key = sha256(api_key)
    Api = db.cursor.execute("SELECT COUNT(*) FROM Version2Api WHERE api_key = ?", (Hashed_api_key,)).fetchone()[0]
 
    if Api == 1:
        Allowed = db.cursor.execute(f"SELECT Allowed FROM Version2Api WHERE api_key = '{Hashed_api_key}'").fetchone()[0]
        if Allowed==None:
            Data_1 = request.form.get('Score_1')
            Data_2 = request.form.get('Score_2')
            Data_1 = float(Data_1)
            Data_2 = float(Data_2)
        
            pred = model.predict([[Data_1, Data_2]])

            Api_requests = db.cursor.execute(f"SELECT Api_requests FROM Version2Api WHERE Api_key='{Hashed_api_key}'").fetchone()[0]

            print(Api_requests)
            if Api_requests == None :
                db.cursor.execute(f"UPDATE Version2Api SET Api_requests = 1 , ip_address='{request.environ['REMOTE_ADDR']}' WHERE Api_key = '{Hashed_api_key}' ")
                db.cnxn.commit()
            else :
                Api_requests = int(Api_requests)+1
                db.cursor.execute(f"UPDATE Version2Api SET Api_requests = {Api_requests} , ip_address='{request.environ['REMOTE_ADDR']}'  WHERE Api_key = '{Hashed_api_key}'")
                db.cnxn.commit()
            
        else:
            return {
                "status": "Error",
                'Message':'Api user not allowed',
                'api':api_key
            }

        

        if pred == 0:
            return {'result':'Fail', 'Server':200}
        else:
            return {'result':'Pass', 'Server':200}

    else:
        return "Invalid API key", 401




@app.route("/v2/api", methods=['GET'])
def addnew():
    User_id = request.headers.get('User-ID')
    api_count = db.cursor.execute(f"SELECT api_generateCount FROM Version2Api WHERE user_id='{User_id}'").fetchone()[0]
    User_id = User_id.lower()

    if not User_id:
        return {'user': ''}, 401
    else:
        user = db.cursor.execute('SELECT user_id FROM Version2Api')
        users = [row[0] for row in user.fetchall()]
        
        if User_id in users:
            Api_key = secrets.token_urlsafe(11) + '-' + secrets.token_urlsafe(7)
            Hashed_api = sha256(Api_key)
            db.cursor.execute(f"UPDATE Version2Api SET Api_key='{Hashed_api}', ip_address='{request.environ['REMOTE_ADDR']}' WHERE user_id='{User_id}'")
            db.cnxn.commit()
            update_api_count(api_count, User_id)
            return {'api': Api_key, 'user': User_id}
        else:
            Api_key = secrets.token_urlsafe(11) + '-' + secrets.token_urlsafe(7)
            Hashed_api = sha256(Api_key)
            db.cursor.execute(f"INSERT INTO Version2Api (user_id, Api_key, ip_address) VALUES ('{User_id}', '{Hashed_api}', '{request.environ['REMOTE_ADDR']}')")
            db.cnxn.commit()
            update_api_count(api_count, User_id)
            return {'api': Api_key, 'user': User_id}

def update_api_count(api_count, User_id):
    if api_count is None:
        db.cursor.execute(f"UPDATE Version2Api SET api_generateCount=1 WHERE user_id='{User_id}'")
        db.cnxn.commit()
        return 0
    else:
        api_count = api_count + 1
        db.cursor.execute(f"UPDATE Version2Api SET api_generateCount={api_count} WHERE user_id='{User_id}'")
        db.cnxn.commit()
        return api_count






if __name__ == '__main__':
    app.run(debug=True,port=4232)
