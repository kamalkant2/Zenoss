#not related to Zenoss 
#general shell script to check any dependencies

OS=`gawk -F= '/^NAME/{print $2}' /etc/os-release`
APT_DISTROS=("ubuntu" "debian")
YUM_DISTROS=("fedora" "rhel" "centos")
DISTRO_FLAG=""

for distro in "${APT_DISTROS[@]}"
do
  	match=`echo "$OS" | grep -i -E -o "$distro"`
        if [ -n "$match" ]; then
                DISTRO_FLAG="apt"
                break
        fi
done

if [ -z "$DISTRO_FLAG" ]; then
        for distro in "${YUM_DISTROS[@]}"
        do
          	match=`echo "$OS" | grep -i -E -o "$distro"`
                if [ -n "$match" ]; then
                        DISTRO_FLAG="yum"
                        break
                fi
        done
fi


if [ "$DISTRO_FLAG" == "apt" ]; then
        echo "Using apt-get"
        apt-get install -y git python27
elif [ "$DISTRO_FLAG" == "yum" ]; then
        echo "Using yum"
        yum install -y git python27
else
    	echo "Unknown distro."
fi
