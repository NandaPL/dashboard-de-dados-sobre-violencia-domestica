import pyrebase
import pandas as pd


def connect_firebase():

    firebaseConfig = {
        "apiKey": "AIzaSyDDbyEQIN0UfyFaZsnTJegjZZSa1SMw4qo",
        "authDomain": "dashboard-sobre-violencia.firebaseapp.com",
        "projectId": "dashboard-sobre-violencia",
        "databaseURL": "https://dashboard-sobre-violencia-default-rtdb.firebaseio.com/",
        "storageBucket": "dashboard-sobre-violencia.appspot.com",
        "messagingSenderId": "596297318510",
        "appId": "1:596297318510:web:0702e84b644ecfbae0267f",
        "measurementId": "${config.measurementId}",
    }

    firebase = pyrebase.initialize_app(firebaseConfig)

    dados = firebase.database()

    return dados


def insert_data(data, child_principal, child_secundary):
    ref = connect_firebase().child(child_principal).child(child_secundary)

    if child_principal == "Tweets_Crus":
        return ref.set(data)
    elif child_principal == "word_ranking":
        return ref.update(data)


def get_database():
    all_words = connect_firebase().child("word_ranking").get()

    df_wordRanking = pd.DataFrame([word.val() for word in all_words.each()])

    return df_wordRanking
