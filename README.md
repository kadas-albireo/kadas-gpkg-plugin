KADAS GPKG Plugin
==================


Publish new version
-------------------

    make package VERSION=master
    scp kadas_gpkg.zip pkg@pkg:www/qgis/vbs/
    ssh pkg@pkg qgis-plugin-repo-scan http://pkg.sourcepole.ch/qgis /home/pkg/www/qgis
