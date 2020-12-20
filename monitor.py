import os
import time
from typing import List
from ruamel.yaml import YAML
from loguru import logger

from user import User


def tail(file):
    # from http://www.dabeaz.com/generators/Generators.pdf
    file.seek(0, os.SEEK_END)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


class Monitor:
    def __init__(self):
        self.__users: List[User] = []

        self.__yaml = YAML()
        self.__yaml.register_class(User)
        self.__yaml.default_flow_style = False

        self.__loadUsers(config='users.yaml')

    def __loadUsers(self, config: str):
        with open('users.yaml', 'r') as content:
            self.__users = self.__yaml.load(content)

    def testUsers(self):
        for user in self.__users:
            user.sendSMS(subject='Test Message !')

    def actionMotionStart(self, info: str):
        date = info.split(sep=" - ")
        msg = f"Mouvement détecté à {date}" \
              f"https://protect.ui.com/"
        for user in self.__users:
            user.sendSMS(info)

    def actionMotionStop(self, info: str):
        pass

    def actionJSON(self):
        pass

    def watch(self):
        logger.info("Start watching /srv/unifi-protect/logs/events.cameras.log")

        logfile = open("/srv/unifi-protect/logs/events.cameras.log", "r")
        loglines = tail(logfile)

        open_level = 0
        event = ''

        for line in loglines:

            line = line.lstrip()
            line = line.rstrip()

            if "verbose: motion.start" in line:
                logger.info("Mouvement Début !")
                self.actionMotionStart(info=line)
                continue

            if "verbose: motion.stop" in line:
                logger.info("Mouvement Fin !")
                self.actionMotionStop(info=line)
                continue

            # if open_level == 0 and len(line) > 0 and line[0] != '{':
            #     logger.debug(line)
            #
            # # Extract JSON event
            # for character in line:
            #     if character == '{':
            #         open_level += 1
            #
            #     if open_level > 0:
            #         event += character
            #
            #     if character == '}':
            #         open_level -= 1
            #         if open_level == 0:
            #             logger.info(f'JSON : {event}')
            #             self.actionJSON()
            #             event = ''
            #
            #     if open_level < 0:
            #         logger.warning(f'Too Many }} : {event}')
            #         open_level = 0
            #         event = ''
