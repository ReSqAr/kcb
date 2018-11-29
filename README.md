# kcb

Python helper to execute bash scripts inside KDEConnect's sshfs mount.
The main motivation behind this helper is to backup my
smartphone's photos and Whatsapp folders with a single command
and without resorting to a file manager.
The approach however allows a whole range of possible use cases.


## Installation and configuration

```
pip3 install --user kcb
mkdir ~/.config/kcb
wget https://raw.githubusercontent.com/ReSqAr/kcb/master/Documentation/Examples/My%20Smartphone.sh -O ~/.config/kcb/"PHONENAME.sh"
chown u+x ~/.config/kcb/PHONENAME.sh
pico ~/.config/kcb/PHONENAME.sh
```
One has to repeat the last three lines such that in the end
the local `~/.config/kcb/` folder contains bash scripts for all phones.
Here `PHONENAME` is a placeholder for the KDEConnect phone name
and phones without a corresponding bash script are ignored.
These scripts can assume that they are run in the phone's sftp mount point,
i.e. the folders `DCIM`, `Downloads`, `Android`, etc are actually directly visible.
One should note that the connection can drop,
hence the bash script must be sufficiently resilient to avoid tears. 


### Example bash scripts

The following is a sample bash script which backups the photo folder, OSMAnd's GPS tracks and the WhatsApp folder to the local `~/MySmartphone` folder.

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
one could add `~/.local/bin` to the `$PATH` variable for example
or - however use that at your own peril - by running the `pip3` command as `root`.

Regarding the command line parameters of `kcb`,
you can run `kcb` without any parameters
in which case all bash scripts of all phones which are online are executed.
Or you can list the names of the devices
whose bash scripts should be executed.


### Example usage

Assume that KDE Connect knows two smartphones named `OnePlus` and `Samsung S8`.

- `kcb OnePlus` executes just `OnePlus.sh` (if it exists)
- `kcb "Samsung S8"` executes just `Samsung S8.sh` (if it exists) 
- `kcb` executes both shell scripts (if they exist)
- `kcb OnePlus "Samsung S8"` executes both shell scripts (if they exist)

## License

Released under the [GPL 3](https://opensource.org/licenses/GPL-3.0).

## Contact

For bug reports please use the GitHub bug tracker.
I would love to hear from you about your thoughts/use cases/etc,
just drop me a line via `yasin.zaehringer-kcb@yhjz.de`.

