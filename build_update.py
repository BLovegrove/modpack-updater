from cx_Freeze import setup, Executable
import config as cfg

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {"packages": [], "excludes": []}

base = "Console"

executables = [
    Executable("./updater/__main__.py", base=base, target_name="modpack-update")
]

setup(
    name="modpack-updater",
    version="1.0",
    description=f"Updates the {cfg.pack.name} modpack",
    options={"build_exe": build_options},
    executables=executables,
)
