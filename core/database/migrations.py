import importlib.util
import os
import sys

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


def run_migrations():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    service_dir = os.path.dirname(os.path.dirname(current_dir))
    alembic_ini = os.path.join(service_dir, "alembic.ini")

    if not os.path.exists(alembic_ini):
        print(f"No alembic.ini found at {alembic_ini}")
        return False

    config = Config(alembic_ini)

    try:
        script = ScriptDirectory.from_config(config)

        def get_revision(rev):
            return script.get_revision(rev)

        head = script.get_current_head()
        if not head:
            print("No migrations found")
            return True

        print(f"Running migrations to {head}...")

        env_path = os.path.join(service_dir, "alembic", "env.py")
        if os.path.exists(env_path):
            spec = importlib.util.spec_from_file_location("alembic_env", env_path)
            env_module = importlib.util.module_from_spec(spec)
            sys.modules["alembic_env"] = env_module
            spec.loader.exec_module(env_module)

        command.upgrade(config, "head")

        print("Migrations completed successfully")
        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
