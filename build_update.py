from cx_Freeze import setup, Executable
import config as cfg

# Dependencies are automatically detected, but it might need
# fine tuning.

build_options = {
    "packages": [],
    "excludes": [],
    "build_exe": "/home/brandon/.var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances/core/minecraft/tools/",
}
# build_options = {"packages": [], "excludes": [], }

setup(
    name="modpack-uploader",
    version="1.0",
    description=f"Uploads new version of {cfg.pack.name} modpack",
    options={"build_exe": build_options},
    executables=[
        Executable(
            "./updater/__main__.py", base="Console", target_name="modpack-update"
        )
    ],
)
