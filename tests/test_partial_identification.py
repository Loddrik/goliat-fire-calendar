"""Synthetic exhaustive-completion oracle; never opens observation data."""
import copy
import itertools
import random
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pipeline'))
from partial_identification import bound_registered_classifications, PAIRS

SUBSETS = [tuple(p for i, p in enumerate(PAIRS) if mask & (1 << i))
           for mask in range(1, 16)]
NAMES = ('A_only', 'V_only', 'disagreement_count', 'jaccard',
         'A_only_fraction_of_A', 'V_only_fraction_of_V')


def observation(values):
    return {'recorded_values': sorted(values), 'qa_flags': [],
            'policy_inclusion': {'status': 'undecided'},
            'frp_status': {'status': 'not_assessed'}}


def request_for(subsets):
    return {'schema_version': 1, 'target': 'registered_positive',
            'positive_rule_id': 'toy-positive-rule-v1',
            'scope': {'status': 'fixed_hypothetical', 'universe_id': 'toy-disjoint-v1',
                      'disjoint': True, 'unit_weight': 1},
            'coupling': 'cartesian_across_units',
            'units': [{'unit_id': f'u{i:02}',
                       'A': observation({int(p[0]) for p in pairs}),
                       'V': observation({int(p[1]) for p in pairs}),
                       'allowed_pairs': list(pairs)} for i, pairs in enumerate(subsets)]}


def direct_values(path):
    # Independent oracle counts labels directly, without DP transition constants
    # or deriving direction from (intersection, union, A-positive).
    counts = {pair: path.count(pair) for pair in PAIRS}
    aonly, vonly, both = counts['10'], counts['01'], counts['11']
    union = sum(pair != '00' for pair in path)
    apos = sum(pair[0] == '1' for pair in path)
    vpos = sum(pair[1] == '1' for pair in path)
    values = (aonly, vonly, aonly + vonly,
              Fraction(both, union) if union else None,
              Fraction(aonly, apos) if apos else None,
              Fraction(vonly, vpos) if vpos else None)
    return (both, union, apos), values


def oracle(subsets):
    states, actions = set(), set()
    extrema = [{'low': None, 'high': None, 'lw': None, 'hw': None, 'undefined': False}
               for _ in NAMES]
    for path in itertools.product(*subsets):
        state, values = direct_values(path)
        states.add(state)
        actions.add('review_human' if any(p != '00' for p in path)
                    else 'no_review_from_this_rule')
        for item, value in zip(extrema, values):
            if value is None:
                item['undefined'] = True
                continue
            if item['low'] is None or value < item['low'] or (value == item['low'] and path < item['lw']):
                item['low'], item['lw'] = value, path
            if item['high'] is None or value > item['high'] or (value == item['high'] and path < item['hw']):
                item['high'], item['hw'] = value, path
    return sorted(states), sorted(actions), extrema


def number(value):
    if isinstance(value, dict):
        return Fraction(value['numerator'], value['denominator'])
    return value


class PartialIdentificationTests(unittest.TestCase):
    def compare_oracle(self, subsets):
        result = bound_registered_classifications(request_for(subsets))
        self.assertEqual(result['status'], 'identified_set')
        states, actions, extrema = oracle(subsets)
        self.assertEqual(result['reachable_states'], [list(s) for s in states])
        self.assertEqual(result['decision']['possible_actions'], actions)
        self.assertEqual(result['decision']['status'], 'invariant' if len(actions) == 1 else 'varies')
        for name, expected in zip(NAMES, extrema):
            metric = result['metrics'][name]
            self.assertEqual(number(metric['lower']), expected['low'], (subsets, name))
            self.assertEqual(number(metric['upper']), expected['high'], (subsets, name))
            self.assertEqual(metric['undefined_possible'], expected['undefined'])
            self.assertEqual(metric['defined_possible'], expected['low'] is not None)
            for key, path in [('lower_witness', expected['lw']), ('upper_witness', expected['hw'])]:
                self.assertEqual(metric[key], None if path is None else
                                 {f'u{i:02}': p for i, p in enumerate(path)})
        return result

    def test_full_input_space_through_three_units(self):
        self.covered_small = 0
        for n in range(4):
            for subsets in itertools.product(SUBSETS, repeat=n):
                self.compare_oracle(subsets)
                self.covered_small += 1
        self.assertEqual(self.covered_small, 3616)

    def test_full_completion_oracle_four_through_seven(self):
        rng = random.Random(20261115)
        cases = 0
        for n in range(4, 8):
            inputs = [(subset,) * n for subset in SUBSETS]
            # Ordered pairs include both phases for each alternating cycle.
            inputs += [tuple((a, b)[i % 2] for i in range(n))
                       for a in SUBSETS for b in SUBSETS if a != b]
            inputs += [tuple(rng.choice(SUBSETS) for _ in range(n)) for _ in range(200)]
            for subsets in inputs:
                self.compare_oracle(subsets)
                cases += 1
        self.assertEqual(cases, 1700)

    def test_unknown_is_not_zero_and_unknown_scope_has_no_bounds(self):
        result = self.compare_oracle([('00', '01')])
        self.assertEqual(result['decision']['status'], 'varies')
        self.assertEqual(result['metrics']['V_only']['upper'], 1)
        self.assertTrue(result['metrics']['jaccard']['undefined_possible'])
        req = request_for([])
        req['scope'] = {'status': 'unidentified', 'reason': 'common_support_unbounded'}
        missing = bound_registered_classifications(req)
        self.assertEqual(missing['status'], 'not_identified')
        self.assertIsNone(missing['metrics'])
        self.assertEqual(missing['decision']['status'], 'unknown')
        req['units'] = request_for([('00',)])['units']
        self.assertEqual(bound_registered_classifications(req)['status'], 'invalid_input')

    def test_qa_policy_frp_never_erase_final_positive(self):
        req = request_for([('01',)])
        before = bound_registered_classifications(req)
        obs = req['units'][0]['V']
        obs['qa_flags'] = ['M13_bit6_non_nominal']
        obs['policy_inclusion'] = {'status': 'exclude', 'policy_id': 'toy-screen-v1'}
        obs['frp_status'] = {'status': 'reported', 'value': 0, 'flags': ['M13_bit6']}
        self.assertEqual(bound_registered_classifications(req), before)
        self.assertEqual(before['metrics']['V_only']['lower'], 1)
        self.assertEqual(before['decision']['possible_actions'], ['review_human'])
        for status in ('not_assessed', 'unavailable'):
            obs['frp_status'] = {'status': status}
            self.assertEqual(bound_registered_classifications(req), before)

    def test_permutation_swap_expansion(self):
        rng = random.Random(20261115)
        for _ in range(80):
            subsets = [rng.choice(SUBSETS) for _ in range(5)]
            req = request_for(subsets)
            original = bound_registered_classifications(req)
            req['units'].reverse()
            for unit in req['units']:
                unit['allowed_pairs'].reverse()
                unit['A']['recorded_values'].reverse()
            self.assertEqual(bound_registered_classifications(req), original)
            swapped = self.compare_oracle([tuple(sorted(p[::-1] for p in subset)) for subset in subsets])
            for left, right in [('jaccard', 'jaccard'), ('A_only', 'V_only'),
                                ('A_only_fraction_of_A', 'V_only_fraction_of_V')]:
                for field in ('lower', 'upper', 'defined_possible', 'undefined_possible'):
                    self.assertEqual(original['metrics'][left][field], swapped['metrics'][right][field])
            expanded = list(subsets)
            expanded[0] = PAIRS
            larger = self.compare_oracle(expanded)
            self.assertTrue({tuple(s) for s in original['reachable_states']} <=
                            {tuple(s) for s in larger['reachable_states']})
            self.assertTrue(set(original['decision']['possible_actions']) <=
                            set(larger['decision']['possible_actions']))
            for name in NAMES:
                small, big = original['metrics'][name], larger['metrics'][name]
                if small['defined_possible']:
                    self.assertLessEqual(number(big['lower']), number(small['lower']))
                    self.assertGreaterEqual(number(big['upper']), number(small['upper']))
                if small['undefined_possible']:
                    self.assertTrue(big['undefined_possible'])

    def test_contract_rejections(self):
        good = request_for([PAIRS])
        def rejected(mutator):
            req = copy.deepcopy(good)
            mutator(req)
            self.assertEqual(bound_registered_classifications(req)['status'], 'invalid_input', req)
        rejected(lambda r: r.update(schema_version=True))
        rejected(lambda r: r.update(target='physical_fire'))
        rejected(lambda r: r.update(coupling='global_constraint'))
        rejected(lambda r: r['scope'].update(unit_weight=2))
        rejected(lambda r: r['scope'].update(disjoint=False))
        rejected(lambda r: r['units'].append(copy.deepcopy(r['units'][0])))
        rejected(lambda r: r['units'][0].update(allowed_pairs=[]))
        rejected(lambda r: r['units'][0].update(allowed_pairs=['22']))
        rejected(lambda r: r['units'][0].update(allowed_pairs=['00']))
        rejected(lambda r: r['units'][0]['A'].update(recorded_values=[True, 0]))
        rejected(lambda r: r['units'][0]['V'].update(frp_status={'status': 'reported', 'value': float('nan')}))
        rejected(lambda r: r.update(unexpected='field'))
        self.assertEqual(bound_registered_classifications(None)['status'], 'invalid_input')

    def test_resource_caps_are_explicit_nonresults(self):
        req = request_for([PAIRS, PAIRS])
        for name, cap in [('units', 1), ('states_per_layer', 1),
                          ('backpointers', 1), ('transitions', 1)]:
            result = bound_registered_classifications(req, limits={name: cap})
            self.assertEqual(result['status'], 'resource_limit')
            self.assertEqual(result['reason'], name)
            self.assertIsNone(result['metrics'])
            self.assertNotIn('reachable_states', result)
            self.assertEqual(result['decision']['status'], 'unknown')
        self.assertEqual(bound_registered_classifications(req, limits={'units': 201})['status'], 'invalid_input')
        self.assertEqual(bound_registered_classifications(request_for([('00',)] * 201))['status'], 'resource_limit')
        # The exact threshold succeeds; only exceeding a cap fails.
        exact = bound_registered_classifications(request_for([PAIRS]),
                  limits={'units': 1, 'states_per_layer': 4, 'backpointers': 4, 'transitions': 4})
        self.assertEqual(exact['status'], 'identified_set')


if __name__ == '__main__':
    unittest.main()
