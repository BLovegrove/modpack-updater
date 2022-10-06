from cx_Freeze import setup, Executable
import toml

cfg = toml.load("config.toml")

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'Console'

executables = [
    Executable('./uploader/__main__.py', base=base, target_name = 'modpack-upload')
]

setup (
    name='modpack-uploader',
      version = '1.0',
      description = f'Uploads new version of {cfg["pack"]["name"]} modpack',
      options = {'build_exe': build_options},
      executables = executables
)
