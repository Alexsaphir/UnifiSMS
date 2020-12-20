#!/usr/bin/env python3.9
from loguru import logger

from monitor import Monitor


def main():
    logger.add("/root/UnifiSMS/UnifiSMS.log", rotation="10 MB")
    logger.info('Lancement UnifiSMS !')
    moniteur = Monitor()
    moniteur.watch()


if __name__ == '__main__':
    main()
