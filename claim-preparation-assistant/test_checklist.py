import unittest
from checklist import prepare_checklist

class ChecklistTests(unittest.TestCase):
    def items(self,documents,context=None):
        return {i['id']:i for i in prepare_checklist(documents,context)['items']}
    def test_bill_does_not_prove_payment(self):
        items=self.items(['Hospital bill','Discharge summary'])
        self.assertEqual(items['bill']['possession'],'reported_present')
        self.assertEqual(items['receipt']['possession'],'not_reported')
    def test_negative_names_not_mapped_as_possession(self):
        result=prepare_checklist(['No FIR','Missing payment receipt'])
        self.assertEqual(len(result['unmatched_reported']),2)
        self.assertTrue(all(i['possession']=='not_reported' for i in result['items']))
    def test_condition_unknown_no_and_yes_remain_distinct(self):
        for context,expected in [({},'context_needed'),({'accident':'no'},'not_applicable'),({'accident':'yes'},'required')]:
            self.assertEqual(self.items([],context)['accident']['applicability'],expected)
    def test_kyc_exemption_never_inferred(self):
        self.assertEqual(self.items([],{'amount_band':'unknown_or_below'})['kyc']['applicability'],'confirm_with_insurer')
        self.assertEqual(self.items([],{'amount_band':'above_100000'})['kyc']['applicability'],'required')
    def test_scope_not_silently_generalized(self):
        result=prepare_checklist([],scope='other')
        self.assertFalse(result['items']); self.assertTrue(result['questions'])
    def test_every_item_has_source_and_no_readiness_verdict(self):
        result=prepare_checklist(['Claim form'])
        self.assertEqual(result['readiness'],'not_assessed')
        self.assertTrue(all(i['source_text'] and i['url'] and i['pages'] for i in result['items']))

if __name__=='__main__': unittest.main()
