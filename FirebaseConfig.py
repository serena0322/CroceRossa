import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("/Users/serenagiuliani/PycharmProjects/CroceRossa/crocerossa-1084b-firebase-adminsdk-fbsvc-ebc6d4e5e4.json")
api_key = "AIzaSyBBkg_KKo9PlSDJjzYGNhXHl5Eh77fEUjA"
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
