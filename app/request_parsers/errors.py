class Error(Exception):
    pass


class MalformedRequestError(Error):
    pass


class MissingFieldError(Error):
    pass


class InvalidWifiSettings(Error):
    code = 'INVALID_WIFI_SETTINGS'


class InvalidVideoSettingError(Error):
    pass


class InvalidVideoSettingStunAddressError(Error):
    code = 'INVALID_STUN_ADDRESS'


class UnsupportedPastedCharacterError(Error):
    pass
