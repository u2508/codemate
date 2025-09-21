# backend/llm_adapter.py
# Pluggable adapter that transforms natural language into a structured command spec.
# Returns JSON: {"command": "mkdir", "args": ["testdir"], "confirm": False, "confidence": 0.9}

import json
import re

# Simple rule-based fallback (useful if no LLM is configured)

def nl_to_spec_rule(nl: str):
    nl = nl.strip().lower()
    # create folder called X
    m = re.search(r'(create|make) (a )?(folder|directory) (called )?(?P<name>\w[\w\-\_\.]*)', nl)
    if m:
        return {'command': 'mkdir', 'args': [m.group('name')], 'confirm': False, 'confidence': 0.85}
    m = re.search(r'move (?P<src>\S+) (to|into) (?P<dest>\S+)', nl)
    if m:
        return {'command': 'mv', 'args': [m.group('src'), m.group('dest')], 'confirm': False, 'confidence': 0.8}
    return {'command': 'unknown', 'args': [], 'confirm': False, 'confidence': 0.0}

# If you wire an LLM, make it output strict JSON. Validate schema here.

def validate_spec(spec: dict):
    if 'command' not in spec: return False
    if not isinstance(spec.get('args', []), list): return False
    return True

# public API
def interpret(nl_text: str, llm_client=None):
    if llm_client:
        # TODO: call LLM with a prompt template that returns JSON
        # Example: model.generate(prompt)
        pass
    return nl_to_spec_rule(nl_text)
