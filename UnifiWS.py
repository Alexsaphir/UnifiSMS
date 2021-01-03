import shutil
import time
from requests import Session, Response
import requests
import requests.utils
from loguru import logger
import urllib3
import json


class UnifiWS:
    def __init__(self):
        # Désactive vérification https

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # NVR
        self.addressNVR: str = 'https://unifi-cloudkey-gen2-plus'

        # Login
        self.username: str = 'ubnt'
        self.password: str = 'ubntubnt'

        self.session = None

        assert self.isUnifiOS()
        self.login()
        self.bootstrap = self.getBootstrap()

    def _initSession(self):
        self.session: Session = requests.session()
        self.session.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.session.verify = False

    def isUnifiOS(self):
        # https://github.com/NickWaterton/Unifi-websocket-interface/blob/master/unifi_client.py
        r = requests.head(self.addressNVR, verify=False)
        if r.status_code == 200:
            return True
        return False

    def login(self):
        self._initSession()

        payload = {
                'username'  : self.username,
                'password'  : self.password,
                'rememberMe': False
                }

        r: Response = self.session.post(f"{self.addressNVR}/api/auth/login",
                                        data=json.dumps(payload))

        # cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        if r.ok:
            logger.info("Login Succès !")
        else:
            logger.warning("Login Echec !")
            raise

        return r.ok

    def getBackups(self):
        r = self.session.get(f"{self.addressNVR}/proxy/protect/api/backups")
        if not r.ok:
            raise
        r.json()

    def getBootstrap(self):
        r = self.session.get(f"{self.addressNVR}/proxy/protect/api/bootstrap")
        if r.ok:
            logger.info("Bootstrap Succès !")
        else:
            logger.warning("Bootstrap Echec !")
            raise
        logger.info(f"Caméras trouvées : {len(r.json()['cameras'])}")
        return r.json()

    def getEvents(self, start, end):
        parameter = {
                'start': start,
                'end'  : end,
                'types': ['motion', 'ring']
                }
        r = self.session.get(f"{self.addressNVR}/proxy/protect/api/events",
                             params=parameter)

        if not r.ok:
            raise
        return r.json()

    def getSelf(self):
        r = self.session.get(f"{self.addressNVR}/api/users/self")
        if not r.ok:
            raise
        return r.json()

    def getSystem(self):
        r: Response
        if self.session is None:
            r = requests.get(f"{self.addressNVR}/api/system", verify=False)
        else:
            r = self.session.get(f"{self.addressNVR}/api/system")

        if not r.ok:
            raise
        return r.json()

    def processEvent(self, event, h: int = 1080, w: int = 1920):
        id_event = event['id']
        parameter = {
                'h': h,
                'w': w
                }
        # Récupère la miniature
        r = self.session.get(f"{self.addressNVR}/proxy/protect/api/events/{id_event}/thumbnail",
                             params=parameter,
                             stream=True)
        if not r.ok:
            raise
        with open(f"output/thumb_{id_event}.jpeg", 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        # Récupère la heatmap
        r = self.session.get(f"{self.addressNVR}/proxy/protect/api/events/{id_event}/heatmap",
                             stream=True)
        if not r.ok:
            raise
        with open(f"output/heat_{id_event}.png", 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    def exportEvent(self, event):
        parameter = {
                'camera'  : event['camera'],
                'channel' : 0,
                'start'   : event['start'],
                'end'     : event['end'],
                'filename': f"{event['end']}.mp4"
                }
        r = self.session.get(f"{self.addressNVR}/proxy/protect/api/video/export/",
                             params=parameter,
                             stream=True)
        if not r.ok:
            raise

        with open('output/' + parameter['filename'], 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def main():
    monitor = UnifiWS()

    now = int(time.time() * 1000)
    start = now - (3600 * 6) * 1000

    for event in monitor.getEvents(start, now):
        monitor.processEvent(event)
        monitor.exportEvent(event)


if __name__ == '__main__':
    main()
