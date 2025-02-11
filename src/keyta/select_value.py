import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class SelectValue:
    arg_name: Optional[str]
    kw_call_index: Optional[int]
    pk: Optional[int]
    user_input: Optional[str]

    def jsonify(self):
        # sort the keys in order to always generate the same string
        # the select widget chooses the selected value from the choices by comparing strings
        return json.dumps(asdict(self), sort_keys=True)

    @classmethod
    def from_json(cls, json_str):
        return SelectValue(**json.loads(json_str))
