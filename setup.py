from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'Console'

executables = [
    Executable('./updater/__main__.py', base=base, target_name = 'lamzpack-update')
]

setup (
    name='lamzpack-updater',
      version = '1.0',
      description = 'Updates the Minecraft LAMZPack modpack',
      options = {'build_exe': build_options},
      executables = executables
)
