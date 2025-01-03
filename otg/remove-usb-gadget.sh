#!/bin/bash

# Tears down USB gadgets, see: docs/usb-gadget-driver.md

# Exit on first error.
set -e

# Echo commands before executing them, by default to stderr.
set -x

# Treat undefined environment variables as errors.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
readonly SCRIPT_DIR
# shellcheck source=lib/usb-gadget.sh
source "${SCRIPT_DIR}/lib/usb-gadget.sh"

cd "${USB_GADGET_PATH}"

if [ ! -d "${USB_DEVICE_DIR}" ]; then
    echo "Gadget does not exist, quitting."
    exit 0
fi

pushd "${USB_DEVICE_DIR}"

# Disable all gadgets
if [ -n "$(cat UDC)" ]; then
  echo "" > UDC
fi

# Walk items in `configs`
for config in ${USB_ALL_CONFIGS_DIR} ; do
    # Exit early if there are no entries
    [ "${config}" == "${USB_ALL_CONFIGS_DIR}" ] && break

    # Remove all functions from config
    for function in ${USB_ALL_FUNCTIONS_DIR} ; do
      file="${config}/$(basename "${function}")"
      [ -e "${file}" ] && rm "${file}"
    done

    # Remove strings in config
    [ -d "${config}/${USB_STRINGS_DIR}" ] && rmdir "${config}/${USB_STRINGS_DIR}"

    rmdir "${config}"
done

# Remove functions
for function in ${USB_ALL_FUNCTIONS_DIR} ; do
    [ -d "${function}" ] && rmdir "${function}"
done

# Remove strings from device
[ -d "${USB_STRINGS_DIR}" ] && rmdir "${USB_STRINGS_DIR}"

popd

rmdir "${USB_DEVICE_DIR}"

rm -f /dev/hidg0
rm -f /dev/hidg1
rm -f /dev/hidg2
