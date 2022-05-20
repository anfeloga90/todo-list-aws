#!/bin/bash

set -x
du -hs * | sort -h
echo ${ENVIRONMENT} 
echo sam deploy template.yaml --config-env ${ENVIRONMENT} --no-confirm-changeset --force-upload --no-fail-on-empty-changeset --no-progressbar
sam deploy template.yaml --config-env staging --no-confirm-changeset --force-upload --no-fail-on-empty-changeset --no-progressbar
