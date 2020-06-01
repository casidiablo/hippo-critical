#!/usr/bin/env bash
set -euo pipefail

ORIGINAL_USER=$1
ORIGINAL_GROUP_NAME=$2

if [ "${HOST_USER_ID:-0}" -ne 0 ] && [ "${HOST_GROUP_ID:-0}" -ne 0 ]; then
    # if use already exists, delete it
    if getent passwd "${ORIGINAL_USER}"; then
        userdel -f "$ORIGINAL_USER"
    fi
    
    # when group already exists, reuse it
    if getent group "${HOST_GROUP_ID}" > /dev/null ; then
        group_name=$(getent group "${HOST_GROUP_ID}" | cut -d: -f1)
    # when group does not exist, use the one provisioned in the container
    # before that, delete it and create it anew with new group id
    else
        groupdel "$ORIGINAL_GROUP_NAME"
        groupadd -g "${HOST_GROUP_ID}" "$ORIGINAL_GROUP_NAME"
        group_name=$ORIGINAL_GROUP_NAME
    fi
    
    # re-add user pointing to new group
    useradd -l -u "${HOST_USER_ID}" -g "$group_name" "$ORIGINAL_USER"
    install -d -m 0755 -o "$ORIGINAL_USER" -g "$group_name" "/home/$ORIGINAL_USER"
    
    # TODO receive parameters to override any folder
    chown --changes --silent --no-dereference --recursive \
          "${HOST_USER_ID}":"${HOST_GROUP_ID}" "/home/$ORIGINAL_USER"
fi