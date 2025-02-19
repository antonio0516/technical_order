from enum import Enum

from config import DevConfig, ProdConfig


class ConfigMode(Enum):
    DEV = "dev"
    PROD = "prod"


class Config:
    mode = ConfigMode.PROD

    @staticmethod
    def set_mode(mode: ConfigMode):
        if mode == ConfigMode.DEV:
            Config.mode = ConfigMode.DEV
        elif mode == ConfigMode.PROD:
            Config.mode = ConfigMode.PROD
        else:
            raise Exception("Config mode not found")

    @staticmethod
    def get_config():
        if Config.mode == ConfigMode.DEV:
            return DevConfig
        elif Config.mode == ConfigMode.PROD:
            return ProdConfig
        else:
            raise Exception("Config mode not found")
