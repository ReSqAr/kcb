# kcb

Execute bash scripts on top of KDEConnect's sftp mount

## Installation and configuration

```
pip3 install --user kcb
mkdir .config/kcb
cp https://raw.githubusercontent.com/ReSqAr/kcb/master/Documentation/Examples/My%20Smartphone.sh .config/kcb/PHONENAME.sh
pico .config/kcb/PHONENAME.sh
```

## Example bash scripts

The following is a sample bash script which backups the photo folder, OSMAnd's GPS tracks and the WhatsApp folder to `~/MySmartphone` folder.

```
set -x

TARGET="~/MySmartphone"

echo "file listing"
ls

echo "GPS Tracks"
rsync --human-readable --progress --archive --ignore-existing --itemize-changes --prune-empty-dirs "Android/data/net.osmand.plus/files/tracks/rec/" "$TARGET/GPS Tracks/"

echo "WhatsApp"
rsync --human-readable --progress --archive --ignore-existing --itemize-changes --prune-empty-dirs "WhatsApp/" "$TARGET/WhatsApp/"

echo "Photos"
rsync --human-readable --progress --archive --ignore-existing --itemize-changes --prune-empty-dirs "DCIM/Camera/" "$TARGET/"
```


## Usage

Since we installed the `kcb` executable in `~/.local/bin/`,
we start the application via `~/.local/bin/kcb`.
There are multiple ways around that,
i.e. being able to just type `kcb`;
one could add `~/.local/bin` to the `PATH` variable.

Regarding the command line parameters of `kcb`,
you can run `kcb` without any parameters
in which case all bash scripts of online phones are executed.
Or you can list the names of the devices
whose bash scripts should be executed.


## Example usage
Assume that KDE Connect knows two smartphones named `OnePlus` and `Samsung S8`.

- `.local/bin/kcb OnePlus` executes just `OnePlus.sh` (if it exists)
- `.local/bin/kcb "Samsung S8"` executes just `Samsung S8.sh` (if it exists) 
- `.local/bin/kcb` executes both shell scripts
- `.local/bin/kcb OnePlus "Samsung S8"` executes both shell scripts
