#!/bin/bash
LICENSE_KEY="your_maxmind_license_key"
wget "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country&license_key=$LICENSE_KEY&suffix=tar.gz" -O geoip.tar.gz
tar -xvzf geoip.tar.gz --strip-components=1 -C Database/migrations/ '*.mmdb'
rm geoip.tar.gz