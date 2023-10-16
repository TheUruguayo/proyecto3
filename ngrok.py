from pyngrok import ngrok
import requests
from emailer import Emailer

class ngrokTunnel():
    def __init__(self, port):
        self.emailer = Emailer()
        self.custom_domain = "mollusk-right-kitten.ngrok-free.app"
        self.listener = None
        self.api_key = "2WMZ8RtihzdvGZznv66wM43b6Ed_2jYF8zsNHxaNbqM8Zp7CP"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Ngrok-Version": "2",
            "Content-Type": "application/json",
        }
        self.auth_token = "2WEDyeDPDmemNfvej88UIDuQBhh_Pnyv8vyYd1Kznjff2wX4"
        x = self.cleanse_tunnels()
        if x:
            self.start_tunnel(port)

    def start_tunnel(self, port):
        ngrok.set_auth_token(self.auth_token)
        self.listener = ngrok.connect(port, hostname=self.custom_domain, bind_tls=True)
        self.emailer.sendmail(self.listener.public_url)

    def get_domain(self):
        return self.listener.public_url

    def list_tunnels(self):
        try:
            x = requests.get("https://api.ngrok.com/tunnel_sessions", headers=self.headers)
            return x.json()['tunnel_sessions'][0]['id']
        except Exception as e:
            print(e)

    def cleanse_tunnels(self):
        id = self.list_tunnels()
        if id != None:
            x = requests.post(f"https://api.ngrok.com/tunnel_sessions/{id}/stop", headers=self.headers, json={})
            return x.status_code == 204
        return True