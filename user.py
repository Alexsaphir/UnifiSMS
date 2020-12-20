import datetime

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from freesms import FreeClient, FreeResponse
from loguru import logger


def getWeekDay() -> str:
    day = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    return day[datetime.datetime.today().weekday()]


class User:
    yaml_tag = u'!User'

    def __init__(self, name: str, user: str, passwd: str, planning: dict):
        self.__name = name
        self.__user = user
        self.__passwd = passwd

        self.__ClientSMS: FreeClient = FreeClient(user=self.__user, passwd=self.__passwd)

        self.__planning = planning

    def sendSMS(self, subject: str) -> FreeResponse:
        day = getWeekDay()
        hour = datetime.datetime.today().hour

        if hour in self.__planning[day]:
            logger.info(f"Message Canceled : Planning")
            return 425

        response: FreeResponse = self.__ClientSMS.send_sms(subject)
        logger.info(f"Sending SMS to {self.__name} : {response.status_code}")
        return response

    @classmethod
    def to_yaml(cls, representer, data):
        return representer.represent_mapping(cls.yaml_tag,
                                             {
                                                     'name'    : data.__name,
                                                     'user'    : data.__user,
                                                     'passwd'  : data.__passwd,
                                                     'planning': data.__planning
                                                     })

    @classmethod
    def from_yaml(cls, constructor, node):
        data = CommentedMap()
        constructor.construct_mapping(node, data, deep=True)
        return cls(**data)

    def __str__(self):
        return f"User(name -> {self.__name}, user -> {self.__user}, hour_denied -> {self.__planning})"

