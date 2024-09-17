from firebase_admin import credentials, initialize_app, firestore, get_app
from core.config import settings

cred = credentials.Certificate(settings.FIREBASE_KEY_FILENAME)
initialize_app(cred, name=settings.PROJECT_NAME)

firebase = firestore.client(get_app(settings.PROJECT_NAME))