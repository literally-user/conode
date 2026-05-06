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
class CertsConfig:
    public_key: str
    private_key: str

    expires_in: int


@dataclass(slots=True, frozen=True, kw_only=True)
class DatabaseConfig:
    url: str


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    api: APIConfig
    database: DatabaseConfig
    certs: CertsConfig


def load_config() -> Config:
    config_path = Path("config.toml")

    with config_path.open("rb") as config_file:
        config = tomllib.load(config_file)

        certs_path = Path(config["certs"]["path"])
        with (
            Path(certs_path / "local.crt").open("r") as public_key_file,
            Path(certs_path / "local.key").open("r") as private_key_file,
        ):
            return Config(
                api=APIConfig(
                    host=config["api"]["host"],
                    port=config["api"]["port"],
                    debug=os.getenv("DEBUG", "false") in ("true", "false"),
                ),
                database=DatabaseConfig(url=config["database"]["url"]),
                certs=CertsConfig(
                    public_key=public_key_file.read(),
                    private_key=private_key_file.read(),
                    expires_in=config["certs"]["expires_in"],
                ),
            )
