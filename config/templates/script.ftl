#!/bin/bash

set -e
set +h

. /etc/alps/alps.conf
. /var/lib/alps/functions

<#list requiredDependencies as requiredDependency>
#REQ:${requiredDependency}
</#list>
<#list recommendedDependencies as recommendedDependency>
#REC:${recommendedDependency}
</#list>
<#list optionalDependencies as optionalDependency>
#OPT:${optionalDependency}
</#list>

cd $SOURCE_DIR

<#list downloadUrls as downloadUrl>
wget -nc ${downloadUrl}
</#list>

NAME=<#if packageName??>${packageName}<#else>""</#if>
VERSION=<#if version??>${version}<#else>""</#if>
URL=<#if url??>${url}<#else>""</#if>

if [ ! -z $URL ]
then

TARBALL=$(echo $URL | rev | cut -d/ -f1 | rev)
if [ -z $(echo $TARBALL | grep ".zip$") ]; then
	DIRECTORY=$(tar tf $TARBALL | cut -d/ -f1 | uniq | grep -v "^\.$")
	sudo rm -rf $DIRECTORY
	tar --no-overwrite-dir -xf $TARBALL
else
	DIRECTORY=$(unzip_dirname $TARBALL $NAME)
	unzip_file $TARBALL $NAME
fi

cd $DIRECTORY
fi

<#list commands as command>
${command}
</#list>

if [ ! -z $URL ]; then cd $SOURCE_DIR && cleanup "$NAME" "$DIRECTORY"; fi

register_installed "$NAME" "$VERSION" "$INSTALLED_LIST"
