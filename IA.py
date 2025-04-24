import pyttsx3
import speech_recognition as sr
import json
import time
import os
import requests

# URL de ton fichier JSON sur GitHub (version brute)
URL_MEMOIRE = "https://raw.githubusercontent.com/valou2908/ia/main/ia_memoiry.json"
FICHIER_MEMOIRE = "ia_memoiry.json"

# Initialisation du moteur de voix
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# Télécharger la mémoire si elle n'existe pas
def telecharger_memoire_si_absente():
    if not os.path.exists(FICHIER_MEMOIRE):
        print("Mémoire non trouvée localement, téléchargement...")
        try:
            r = requests.get(URL_MEMOIRE)
            if r.status_code == 200:
                with open(FICHIER_MEMOIRE, 'w', encoding='utf-8') as f:
                    f.write(r.text)
                print("Mémoire téléchargée avec succès.")
            else:
                print("Erreur lors du téléchargement de la mémoire.")
        except Exception as e:
            print("Erreur de téléchargement :", e)

# Charger ou créer la mémoire
def charger_memoire():
    telecharger_memoire_si_absente()
    try:
        with open(FICHIER_MEMOIRE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def sauvegarder_memoire(memoire):
    with open(FICHIER_MEMOIRE, 'w', encoding='utf-8') as f:
        json.dump(memoire, f, ensure_ascii=False, indent=4)

def parler(texte, volume=1.0, rate=150):
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    print("IA:", texte)
    engine.say(texte)
    engine.runAndWait()

def ecouter():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Je t'écoute...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            message = r.recognize_google(audio, language='fr-FR')
            print("Vous :", message)
            return message.lower()
        except sr.UnknownValueError:
            print("Je n'ai pas compris.")
            return ""
        except sr.RequestError:
            print("Problème de connexion.")
            return ""
        except sr.WaitTimeoutError:
            print("Je n'ai pas entendu de phrase.")
            return ""

def ia_vocale():
    memoire = charger_memoire()

    while True:
        message = ecouter()

        if "au revoir" in message:
            parler("Au revoir, à bientôt!")
            break

        if message in memoire:
            reponse = memoire[message]
            if isinstance(reponse, list):
                parler(reponse[0])  # ou random.choice(reponse)
            else:
                parler(reponse)
        else:
            parler(f"Je ne connais pas la réponse à '{message}'. Peux-tu me dire ce que je devrais répondre ?")
            reponse = ecouter()
            if reponse:
                memoire[message] = reponse
                sauvegarder_memoire(memoire)
                parler(f"Merci, je vais m'en souvenir. La réponse à '{message}' est : {reponse}")

# Lancer l'IA vocale
ia_vocale()
