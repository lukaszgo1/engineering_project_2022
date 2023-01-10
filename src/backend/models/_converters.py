import cattrs


DEFAULT_CONV = cattrs.Converter(forbid_extra_keys=True)

from_json_conv = DEFAULT_CONV.copy()
