import os
import pathlib

# База тестов задаётся до импорта приложения и удаляется перед прогоном:
# обработчики меняют данные, поэтому файл прошлого прогона дал бы другой
# результат на тех же тестах.
DATABASE_PATH = pathlib.Path("test.sqlite")
DATABASE_PATH.unlink(missing_ok=True)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{DATABASE_PATH}"
