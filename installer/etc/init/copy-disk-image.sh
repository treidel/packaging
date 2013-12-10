# variables to hold where we're reading from and writing to
IMAGE=/var/tmp/disk.img.gz
DEVICE=/dev/mmcblk1

# flashing light to indicate we're writing the image
if [ -e /sys/class/leds/beaglebone\:green\:usr0/trigger ] ; then
    /bin/echo heartbeat > /sys/class/leds/beaglebone\:green\:usr0/trigger
    /bin/echo heartbeat > /sys/class/leds/beaglebone\:green\:usr1/trigger
    /bin/echo heartbeat > /sys/class/leds/beaglebone\:green\:usr2/trigger
    /bin/echo heartbeat > /sys/class/leds/beaglebone\:green\:usr3/trigger
fi

# indicate to the console we're starting
/usr/bin/logger "Writing image ${IMAGE} to ${DEVICE}"

# do the write operation
/bin/gunzip -c ${IMAGE} | /bin/dd bs=1M of={DEVICE}

# indicate we're done
/usr/bin/logger "Finished writing image"

# solid light to indicate we're done
if [ -e /sys/class/leds/beaglebone\:green\:usr0/trigger ] ; then
    /bin/echo default-on > /sys/class/leds/beaglebone\:green\:usr0/trigger
    /bin/echo default-on > /sys/class/leds/beaglebone\:green\:usr1/trigger
    /bin/echo default-on > /sys/class/leds/beaglebone\:green\:usr2/trigger
    /bin/echo default-on > /sys/class/leds/beaglebone\:green\:usr3/trigger
fi

