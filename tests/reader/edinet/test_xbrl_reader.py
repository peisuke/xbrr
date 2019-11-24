import os
import re
import shutil
import unittest
from edinet.client.document_client import DocumentClient
from edinet.reader.edinet.xbrl_reader import XBRLReader


class TestXBRLReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _dir = os.path.join(os.path.dirname(__file__), "../../data")
        client = DocumentClient()
        file_path = client.get_xbrl("S100G2KL", save_dir=_dir,
                                    expand_level="dir")
        cls.reader = XBRLReader(file_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.reader.xbrl_dir.root)
        if os.path.exists(cls.reader.taxonomy.root):
            shutil.rmtree(cls.reader.taxonomy.root)

    def test_find(self):
        path = os.path.join(os.path.dirname(__file__),
                            "../../data/xbrl2019.xbrl")
        xbrl = XBRLReader(path)
        element = xbrl.find("jpdei_cor:EDINETCodeDEI")
        self.assertEqual(element.text, "E05739")

    def test_to_html(self):
        path = os.path.join(os.path.dirname(__file__),
                            "../../data/xbrl2019.xbrl")
        xbrl = XBRLReader(path)
        tag = "jpcrp_cor:InformationAboutOfficersTextBlock"
        html = xbrl.find(tag).html

        self.assertTrue(html)

    def test_taxonomy_year(self):
        self.assertEqual(self.reader.taxonomy_year, 2018)

    def test_roles(self):
        roles = self.reader.roles
        self.assertEqual(len(roles), 3)
        role_names = [r.split("/")[-1] for r in roles]
        self.assertTrue("rol_BalanceSheet" in role_names)
        self.assertTrue("NotesNumber" in role_names)
        self.assertTrue("rol_StatementOfIncome" in role_names)

    def test_namespaces(self):
        roles = self.reader.namespaces
        self.assertEqual(len(roles), 11)

    def test_read_by_link(self):
        taxonomy_element = self.reader.read_by_link("http://disclosure.edinet-fsa.go.jp/taxonomy/jpcrp/2018-03-31/jpcrp_cor_2018-03-31.xsd#jpcrp_cor_AnnexedDetailedScheduleOfProvisionsTextBlock")
        local_element = self.reader.read_by_link("jpcrp030000-asr-001_E01807-000_2019-03-31_01_2019-06-21.xsd#jpcrp030000-asr_E01807-000_ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsHeading")
        self.assertTrue(taxonomy_element)
        self.assertEqual(taxonomy_element.label(), "引当金明細表")
        self.assertTrue(local_element)
        self.assertTrue(local_element.label(), "経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析")

    def test_read_schema_by_role(self):
        bs = self.reader.read_schema_by_role("http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_BalanceSheet")
        bs.to_csv("bs.csv", index=False, encoding="shift_jis")
        self.assertGreater(len(bs), 0)

    def test_read_value_by_role(self):
        pl = self.reader.read_value_by_role("http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfIncome")
        pl.to_csv("pl.csv", index=False, encoding="shift_jis")
        self.assertGreater(len(pl), 0)

    def test_read_value_by_role_calc(self):
        pl = self.reader.read_value_by_role("http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_StatementOfIncome",
                                            kind="calculation")
        pl.to_csv("pl_cal.csv", index=False, encoding="shift_jis")
        self.assertGreater(len(pl), 0)
