import pyrebase

firebaseConfig = {
    "apiKey": "*************************",
    "authDomain": "****************************",
    "databaseURL": "***************************************",
    "projectId": "*******************************",
    "storageBucket": "*********************************",
    "messagingSenderId": "*****************",
    "appId": "*********************************",
    "measurementId": "************************"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

