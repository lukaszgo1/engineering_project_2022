import configparser
import os
import typing

if typing.TYPE_CHECKING:
    import mariadb_connector

_DEFAULT_DB_PORT = "3306"
_app_config = configparser.ConfigParser()
_app_config.read(os.path.join(os.path.dirname(__file__), "app_config.conf"))
DB_HOST: str = _app_config["Database"]["host"]
db_user: str = _app_config["Database"]["user"]
db_password: str = _app_config["Database"]["password"]
db_name: str = _app_config["Database"]["name"]
db_port: int = int(_app_config["Database"].get("port", _DEFAULT_DB_PORT))
active_db_con: "mariadb_connector.MariadbConnector"
