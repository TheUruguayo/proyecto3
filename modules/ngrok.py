import os

from pyngrok import ngrok
import requests
from modules.emailer import Emailer
from dotenv import load_dotenv, find_dotenv


class ngrokTunnel():
    def __init__(self, port):
        load_dotenv(find_dotenv())
        self.emailer = Emailer()
        self.custom_domain = os.getenv("NGROK-CUSTOM_DOMAIN")
        self.listener = None
        self.api_key = os.getenv("NGROK-API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Ngrok-Version": "2",
            "Content-Type": "application/json",
        }
        self.auth_token = os.getenv("NGROK-AUTH_TOKEN")
        self.tunnels_url = os.getenv("NGROK-TUNNELS_URL")
        x = self.cleanse_tunnels()
        if x:
            self.start_tunnel(port)

    def start_tunnel(self, port):
        ngrok.set_auth_token(self.auth_token)
        self.listener = ngrok.connect(port, hostname=self.custom_domain, bind_tls=True)
        self.emailer.sendmail(self.listener.public_url, subject="start_ngrok")

    def get_domain(self):
        return self.listener.public_url

    def list_tunnels(self):
        try:
            x = requests.get(f"{self.tunnels_url}", headers=self.headers)
            return x.json()['tunnel_sessions'][0]['id']
        except Exception as e:
            print(e)

    def cleanse_tunnels(self):
        id = self.list_tunnels()
        if id != None:
            x = requests.post(f"{self.tunnels_url}/{id}/stop", headers=self.headers, json={})
            return x.status_code == 204
        return True