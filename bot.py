import tweepy
import requests
import time
import os

# Configurações do Twitch
TWITCH_CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID', '4ks9f0is84e2peffewa50hdzjrerkh')
TWITCH_CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET', 'metbwpvqzj687bi3r64uar3r65kby0')
STREAMER_NAME = os.environ.get('STREAMER_NAME', 'oMeiaUm')
JOGO_DESEJADO = os.environ.get('JOGO_DESEJADO', 'Minecraft')

# Configurações do Twitter
API_KEY = os.environ.get('TWITTER_API_KEY', 'rKkhI8DTfyuY5PaCrC0Ir647h')
API_SECRET = os.environ.get('TWITTER_API_SECRET', 'Eo9YuLyOMstAwWvgZ6lHNEoMOncxsguAk8tzJ1fkOsu4xo7jBQ')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN', '1712184630604963840-mg4UNaUs6ivqaxdS4KV1nmdM5DGKz4')
ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', '4q8WeFtOWb4YxjUArFlTLrOnga0Vg0XPFg5uR9CHIAXbp')

# Tempo entre verificações (em segundos)
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 60))

# Autenticação no Twitter
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
twitter_api = tweepy.API(auth)

# Função para obter o token de acesso do Twitch
def get_twitch_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]

# Função para verificar o status do streamer
def check_stream_status(token):
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }
    url = f"https://api.twitch.tv/helix/streams?user_login={STREAMER_NAME}"
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        # Token expirado
        raise RuntimeError("Twitch token expired")
    response.raise_for_status()
    data = response.json()["data"]
    if data and data[0]["game_name"].lower() == JOGO_DESEJADO.lower():
        return True
    return False

def main():
    twitch_token = get_twitch_token()
    notified = False
    print(f"Monitorando {STREAMER_NAME} jogando {JOGO_DESEJADO}...")
    while True:
        try:
            is_streaming = check_stream_status(twitch_token)
            if is_streaming and not notified:
                tweet = f"{STREAMER_NAME} está jogando {JOGO_DESEJADO}! Assista agora: https://www.twitch.tv/{STREAMER_NAME}"
                twitter_api.update_status(tweet)
                print("Tweet enviado:", tweet)
                notified = True
            elif not is_streaming:
                if notified:
                    print(f"{STREAMER_NAME} parou de jogar {JOGO_DESEJADO}.")
                notified = False
            else:
                print(f"{STREAMER_NAME} já está sendo monitorado.")
            time.sleep(CHECK_INTERVAL)
        except RuntimeError as re:
            if "Twitch token expired" in str(re):
                print("Token do Twitch expirado. Renovando...")
                twitch_token = get_twitch_token()
            else:
                print("Erro de runtime:", re)
            time.sleep(CHECK_INTERVAL)
        except tweepy.TweepyException as te:
            print("Erro no Twitter:", te)
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print("Erro inesperado:", e)
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
