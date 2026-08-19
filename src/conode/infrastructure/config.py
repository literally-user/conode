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
    expires_in: int
    public_key: str
    private_key: str
    audience: str
    issuer: str


@dataclass(slots=True, frozen=True, kw_only=True)
class DatabaseConfig:
    username: str
    password: str
    database: str
    host: str
    port: int


@dataclass(slots=True, frozen=True, kw_only=True)
class OTELConfig:
    endpoint: str
    enabled: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    api: APIConfig
    database: DatabaseConfig
    secrets: SecretsConfig
    otel: OTELConfig


def load_config(path: str = "config.toml") -> Config:
    config_path = Path(path)
    with config_path.open("rb") as file:
        config = tomllib.load(file)

        private_key_file_path = Path(config["secrets"]["private_key_file_path"])
        public_key_file_path = Path(config["secrets"]["public_key_file_path"])

        with (
            private_key_file_path.open("r") as private_key_file,
            public_key_file_path.open("r") as public_key_file,
        ):
            private_key = private_key_file.read()
            public_key = public_key_file.read()

        return Config(
            api=APIConfig(
                host=config["api"]["host"],
                port=config["api"]["port"],
                debug=os.getenv("DEBUG", "false") in ("true", "false"),
            ),
            database=DatabaseConfig(
                username=config["database"]["username"],
                password=config["database"]["password"],
                database=config["database"]["database"],
                host=config["database"]["host"],
                port=config["database"]["port"],
            ),
            secrets=SecretsConfig(
                expires_in=config["secrets"]["expires_in"],
                public_key=public_key,
                private_key=private_key,
                audience=config["secrets"]["audience"],
                issuer=config["secrets"]["issuer"],
            ),
            otel=OTELConfig(
                enabled=config["telemetry"]["enabled"],
                endpoint=config["telemetry"]["endpoint"],
            ),
        )
