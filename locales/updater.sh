#!/bin/bash

POT="locales/PyArchboot.pot"
FOLDERS="modules/*.py modules/questioner/*.py modules/system_manager/*.py"
LANGUAGES=(en fr)

if [[ ! -f "PyArchboot.pot" ]]; then
    echo "ERROR: updater needs to be run from PyArchboot/locales folder!"
    exit 1
else
    # Get translatable strings and update POT
    cd ..
    xgettext -d PyArchboot -o locales/PyArchboot.pot PyArchboot.py ${FOLDERS}

    # Update PO files
    for LANGUAGE in "${LANGUAGES[@]}"; do
        msgmerge -U locales/${LANGUAGE}/LC_MESSAGES/PyArchboot.po ${POT}
    done
fi
