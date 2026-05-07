import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True, kw_only=True)
class APIConfig:
    host: str
    port: int

    debug: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class SecretsConfig:
    secret: str
    expires_in: int


@dataclass(slots=True, frozen=True, kw_only=True)
class DatabaseConfig:
    url: str


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    api: APIConfig
    database: DatabaseConfig
    secrets: SecretsConfig


def load_config() -> Config:
    config_path = Path("config.toml")  # объект Path
    with config_path.open("rb") as file:
        config = tomllib.load(file)
        return Config(
            api=APIConfig(
                host=config["api"]["host"],
                port=config["api"]["port"],
                debug=os.getenv("DEBUG", "false") in ("true", "false"),
            ),
            database=DatabaseConfig(url=config["database"]["url"]),
            secrets=SecretsConfig(
                secret=config["api"]["secret"],
                expires_in=config["api"]["expires_in"],
            ),
        )
