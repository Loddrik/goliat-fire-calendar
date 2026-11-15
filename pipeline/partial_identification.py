"""Exact bounds for registered labels in declared, hypothetical toy universes.

No observations, files, physical FRP bounds, or probabilistic assumptions enter
this API. Cartesian completion is a declared constraint, not independence.
"""
from fractions import Fraction
from math import isfinite

PAIRS = ('00', '01', '10', '11')
INCREMENTS = {'00': (0, 0, 0), '01': (0, 1, 0),
              '10': (0, 1, 1), '11': (1, 1, 1)}
DEFAULT_LIMITS = {'units': 200, 'states_per_layer': 100000,
                  'backpointers': 200000, 'transitions': 2000000}
QUALIFIER = 'sharp_only_within_declared_cartesian_hypothetical_model'


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _keys(value, required, optional=()):
    _require(isinstance(value, dict), 'expected_object')
    _require(set(required) <= value.keys() and
             value.keys() <= set(required) | set(optional), 'invalid_fields')


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _observation(obs):
    _keys(obs, ('recorded_values', 'qa_flags', 'policy_inclusion', 'frp_status'))
    values = obs['recorded_values']
    _require(isinstance(values, (list, tuple)) and bool(values) and
             all(type(v) is int and v in (0, 1) for v in values) and
             len(set(values)) == len(values), 'invalid_recorded_values')
    _require(isinstance(obs['qa_flags'], list) and
             all(_text(v) for v in obs['qa_flags']), 'invalid_qa_flags')
    policy = obs['policy_inclusion']
    _keys(policy, ('status',), ('policy_id',))
    _require(policy['status'] in ('include', 'exclude', 'undecided'), 'invalid_policy')
    _require(policy['status'] == 'undecided' or _text(policy.get('policy_id')),
             'policy_id_required')
    if 'policy_id' in policy:
        _require(_text(policy['policy_id']), 'invalid_policy_id')
    frp = obs['frp_status']
    _keys(frp, ('status',), ('value', 'flags'))
    _require(frp['status'] in ('not_assessed', 'reported', 'unavailable'), 'invalid_frp')
    if frp['status'] == 'reported':
        value = frp.get('value')
        _require(type(value) in (int, float) and (type(value) is int or isfinite(value)) and value >= 0,
                 'invalid_reported_frp')
    else:
        _require('value' not in frp, 'unexpected_frp_value')
    if 'flags' in frp:
        _require(isinstance(frp['flags'], list) and all(_text(v) for v in frp['flags']),
                 'invalid_frp_flags')
    return set(values)


def _validate(request):
    _keys(request, ('schema_version', 'target', 'positive_rule_id', 'scope',
                    'units', 'coupling'))
    _require(type(request['schema_version']) is int and request['schema_version'] == 1,
             'unsupported_schema')
    _require(request['target'] == 'registered_positive', 'unsupported_target')
    _require(_text(request['positive_rule_id']), 'positive_rule_required')
    _require(request['coupling'] == 'cartesian_across_units', 'unsupported_coupling')
    _require(isinstance(request['units'], list), 'invalid_units')
    scope = request['scope']
    _require(isinstance(scope, dict), 'invalid_scope')
    if scope.get('status') == 'unidentified':
        _keys(scope, ('status', 'reason'), ('evidence_pending',))
        _require(_text(scope['reason']), 'scope_reason_required')
        _require(not request['units'], 'unidentified_scope_cannot_admit_units')
        return None
    _keys(scope, ('status', 'universe_id', 'disjoint', 'unit_weight'))
    _require(scope['status'] == 'fixed_hypothetical' and _text(scope['universe_id']),
             'invalid_scope')
    _require(scope['disjoint'] is True and type(scope['unit_weight']) is int and
             scope['unit_weight'] == 1, 'unsupported_units')
    units, ids = [], set()
    for unit in request['units']:
        _keys(unit, ('unit_id', 'A', 'V', 'allowed_pairs'))
        uid = unit['unit_id']
        _require(_text(uid) and uid not in ids, 'invalid_or_duplicate_unit_id')
        ids.add(uid)
        av, vv = _observation(unit['A']), _observation(unit['V'])
        pairs = unit['allowed_pairs']
        _require(isinstance(pairs, (list, tuple)) and bool(pairs) and
                 all(isinstance(p, str) and p in PAIRS for p in pairs) and
                 len(set(pairs)) == len(pairs), 'invalid_allowed_pairs')
        _require({int(p[0]) for p in pairs} == av and
                 {int(p[1]) for p in pairs} == vv, 'contradictory_projections')
        units.append((uid, tuple(sorted(pairs))))
    return sorted(units)


def _rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def bound_registered_classifications(request, *, limits=None):
    """Return JSON-compatible exact bounds, or an explicit non-result status.

    Optional limits can only lower the frozen computational caps. Invalid input
    returns invalid_input. Resource exhaustion never returns partial metrics.
    """
    try:
        units = _validate(request)
        caps = dict(DEFAULT_LIMITS)
        if limits is not None:
            _require(isinstance(limits, dict) and limits.keys() <= caps.keys(),
                     'invalid_limits')
            for name, value in limits.items():
                _require(type(value) is int and 0 <= value <= caps[name], 'invalid_limit')
                caps[name] = value
    except (ValueError, TypeError, KeyError) as exc:
        return {'status': 'invalid_input', 'reason': str(exc), 'metrics': None,
                'decision': {'status': 'unknown', 'reason': 'invalid_input'}}
    if units is None:
        return {'status': 'not_identified', 'reason': request['scope']['reason'],
                'metrics': None,
                'decision': {'status': 'unknown', 'reason': 'unidentified_scope'}}

    def exhausted(reason):
        return {'status': 'resource_limit', 'reason': reason, 'metrics': None,
                'decision': {'status': 'unknown', 'reason': 'resource_limit'}}

    if len(units) > caps['units']:
        return exhausted('units')
    # Each layer maps reachable states to a predecessor and pair. Iteration is
    # lexical witness order, so the first predecessor retained is the smallest.
    layers, current = [], [(0, 0, 0)]
    backpointers = transitions = 0
    if caps['states_per_layer'] < 1:
        return exhausted('states_per_layer')
    for _, pairs in units:
        layer = {}
        for state in current:
            for pair in pairs:
                transitions += 1
                if transitions > caps['transitions']:
                    return exhausted('transitions')
                step = INCREMENTS[pair]
                following = tuple(state[k] + step[k] for k in range(3))
                if following not in layer:
                    if len(layer) >= caps['states_per_layer']:
                        return exhausted('states_per_layer')
                    if backpointers >= caps['backpointers']:
                        return exhausted('backpointers')
                    layer[following] = (state, pair)
                    backpointers += 1
        layers.append(layer)
        current = list(layer)  # insertion order is lexical witness order
    states = sorted(current)
    witness_cache = {}

    def witness(state):
        original = state
        if state not in witness_cache:
            path = []
            for layer in reversed(layers):
                state, pair = layer[state]
                path.append(pair)
            witness_cache[original] = {
                uid: pair for (uid, _), pair in zip(units, reversed(path))}
        return witness_cache[original]

    # Final insertion order already follows lexical minimum witnesses. Recover
    # paths only for metric extremes, not for every reachable state.
    lexical = current

    def bounds(values, ratio=False):
        defined = []
        for state in lexical:
            value = values(state)
            if value is not None:
                defined.append((state, value))
        if not defined:
            return {'lower': None, 'upper': None, 'defined_possible': False,
                    'undefined_possible': True, 'lower_witness': None, 'upper_witness': None}
        low = min(value for _, value in defined)
        high = max(value for _, value in defined)
        lo_state = next(s for s, value in defined if value == low)
        hi_state = next(s for s, value in defined if value == high)
        return {'lower': _rational(low) if ratio else low,
                'upper': _rational(high) if ratio else high,
                'defined_possible': True, 'undefined_possible': len(defined) < len(states),
                'lower_witness': witness(lo_state), 'upper_witness': witness(hi_state)}

    metrics = {
        'A_only': bounds(lambda s: s[2] - s[0]),
        'V_only': bounds(lambda s: s[1] - s[2]),
        'disagreement_count': bounds(lambda s: s[1] - s[0]),
        'jaccard': bounds(lambda s: Fraction(s[0], s[1]) if s[1] else None, True),
        'A_only_fraction_of_A': bounds(
            lambda s: Fraction(s[2] - s[0], s[2]) if s[2] else None, True),
        'V_only_fraction_of_V': bounds(
            lambda s: Fraction(s[1] - s[2], s[1] + s[0] - s[2])
            if s[1] + s[0] - s[2] else None, True),
    }
    actions = sorted({'review_human' if s[1] else 'no_review_from_this_rule' for s in states})
    return {'status': 'identified_set', 'qualifier': QUALIFIER,
            'positive_rule_id': request['positive_rule_id'],
            'universe_id': request['scope']['universe_id'], 'unit_count': len(units),
            'coupling': request['coupling'],
            'constraints': [{'unit_id': uid, 'allowed_pairs': list(pairs)} for uid, pairs in units],
            'reachable_states': [list(s) for s in states], 'metrics': metrics,
            'decision': {'status': 'invariant' if len(actions) == 1 else 'varies',
                         'possible_actions': actions},
            'computation': {'transitions': transitions, 'backpointers': backpointers,
                            'limits': caps}}
