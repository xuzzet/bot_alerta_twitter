import tweepy
import requests
import time

# Configurações do Twitch
TWITCH_CLIENT_ID = '4ks9f0is84e2peffewa50hdzjrerkh'
TWITCH_CLIENT_SECRET = 'metbwpvqzj687bi3r64uar3r65kby0'
STREAMER_NAME = 'oMeiaUm'
JOGO_DESEJADO = 'Minecraft'

# Configurações do Twitter
API_KEY = 'rKkhI8DTfyuY5PaCrC0Ir647h'
API_SECRET = 'Eo9YuLyOMstAwWvgZ6lHNEoMOncxsguAk8tzJ1fkOsu4xo7jBQ'
ACCESS_TOKEN = '1712184630604963840-mg4UNaUs6ivqaxdS4KV1nmdM5DGKz4'
ACCESS_TOKEN_SECRET = '4q8WeFtOWb4YxjUArFlTLrOnga0Vg0XPFg5uR9CHIAXbp'

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
    response.raise_for_status()
    data = response.json()["data"]
    if data and data[0]["game_name"].lower() == JOGO_DESEJADO.lower():
        return True
    return False

def main():
    twitch_token = get_twitch_token()
    notified = False
    while True:
        try:
            is_streaming = check_stream_status(twitch_token)
            if is_streaming and not notified:
                tweet = f"{STREAMER_NAME} está jogando {JOGO_DESEJADO}! Assista agora: https://www.twitch.tv/{STREAMER_NAME}"
                twitter_api.update_status(tweet)
                print("Tweet enviado:", tweet)
                notified = True
            elif not is_streaming:
                notified = False
            time.sleep(60)  # Verifica a cada 60 segundos
        except Exception as e:
            print("Erro:", e)
            time.sleep(60)

if __name__ == "__main__":
    main()
