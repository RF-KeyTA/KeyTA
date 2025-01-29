from dataclasses import dataclass, asdict
import json


@dataclass
class SelectValue:
    arg_name: str|None
    kw_call_index: int|None
    pk: int|None
    user_input: str|None

    def jsonify(self):
        # sort the keys in order to always generate the same string
        # the select widget chooses the selected value from the choices by comparing strings
        return json.dumps(asdict(self), sort_keys=True)

    @classmethod
    def from_json(cls, json_str):
        return SelectValue(**json.loads(json_str))
