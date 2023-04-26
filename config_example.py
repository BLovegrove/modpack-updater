class pack:
    # The name of your pack to display in the scripts welcome message
    name = "Your Modpack Name Here"
    # Url to your modpacks data. Must be a zip containing a config folder and/or a mods folder in its root. Must be direct DL link.
    url = "https://foo.bar/modpack/latest.zip"
    # Url to your modpacks version file. Must be a txt file containing one line with a 3-part semantic version number.
    version = "https://foo.bar/version.txt"


class updater:
    # Wether or not to check for an updated version of the updater itself - this should stay on outside of testing
    check_version = True
    # Url to the updater version file. Must be a txt file containing one line with a 3-part semantic version number.
    version = "https://foo.bar/version.txt"


class upload:
    # Public IP address for the system your pack is hosted on
    host = "xxx.xxx.xxx.xxx"
    # SSH-FTP (SFTP) port (must be forwarded!) on the host system you pack lives on. Usually default unless you changed it.
    port = 22
    # Username and password for the user account you are using SSH to access.
    username = ""
    password = ""
    # Path to the folder you want your modpack version folders to live. This is usually the same as the path in your URL setting above.
    # I would recommend using apache2 to host it on /var/www/<something>. This program does not work with dropbox or anything. Only something accessable via SFTP.
    filepath = ""
