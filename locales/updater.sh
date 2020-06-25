#!/bin/bash

APP="PyArchboot"
POT="locales/${APP}.pot"
FOLDERS="modules/*.py modules/questioner/*.py modules/system_manager/*.py"
LANGUAGES=(en fr)

if [[ ! -f "${APP}.pot" ]]; then
    echo "ERROR: updater needs to be run from ${APP}/locales folder!"
    exit 1
else
    # Get translatable strings and update POT
    cd ..
    xgettext -d ${APP} -o ${POT} ${APP}.py "${FOLDERS}" --keyword=trad

    # Update PO files
    for LANGUAGE in "${LANGUAGES[@]}"; do
        msgmerge -U locales/"${LANGUAGE}"/LC_MESSAGES/${APP}.po ${POT}
    done
fi
