#!/bin/bash

# Exit script on first failure.
set -e

# Exit on unset variable.
set -u

# Enable the dwc2 kernel driver, which we need to emulate USB devices with USB
# OTG.
readonly MODULES_PATH='/etc/modules'
if ! grep --quiet '^dwc2$' "${MODULES_PATH}" ; then
  echo 'dwc2' | tee --append "${MODULES_PATH}"
fi
readonly BOOT_CONFIG_PATH='/boot/firmware/config.txt'
if ! grep --quiet '^dtoverlay=dwc2$' "${BOOT_CONFIG_PATH}" ; then
  echo 'dtoverlay=dwc2' | tee --append "${BOOT_CONFIG_PATH}"
fi
