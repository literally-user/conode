import argparse
from pathlib import Path

from alembic import command
from alembic.config import Config

import conode.infrastructure.persistence
from conode.bootstrap.api import run_http
from conode.infrastructure.persistence import start_mapper


def get_migrations_path() -> Path:
    persistence_root = Path(conode.infrastructure.persistence.__file__).resolve().parent
    return persistence_root / "migrations"


def get_alembic_config() -> Config:
    config = Config()
    config.set_main_option("script_location", str(get_migrations_path()))
    return config


def run_migrations(*_args: str) -> None:
    command.upgrade(get_alembic_config(), "head")


def autogenerate_migrations(*args: str) -> None:
    command.revision(get_alembic_config(), message=args[0], autogenerate=True)


def configure_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="conode",
        description="Easy-to-use API for building graphs with state contexts.",
    )

    subparsers = parser.add_subparsers(dest="module", required=True)

    api_parser = subparsers.add_parser("api", help="API service")
    api_sub = api_parser.add_subparsers(dest="option", required=True)

    api_run = api_sub.add_parser("run", help="Run API")
    api_run.set_defaults(func=run_http)

    mig_parser = subparsers.add_parser("migrations", help="Database migrations")
    mig_sub = mig_parser.add_subparsers(dest="option", required=True)

    mig_upgrade = mig_sub.add_parser("upgrade", help="Apply migrations")
    mig_upgrade.set_defaults(func=run_migrations)

    mig_generate = mig_sub.add_parser("generate", help="Generate migration")
    mig_generate.add_argument("message", type=str)
    mig_generate.set_defaults(func=lambda args: autogenerate_migrations(args.message))

    return parser


def main() -> None:
    parser = configure_argument_parser()
    args = parser.parse_args()

    if args.module == "api":
        run_migrations()

    start_mapper()

    args.func(args)
