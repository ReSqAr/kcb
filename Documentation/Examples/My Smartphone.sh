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
