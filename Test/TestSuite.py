from unittest import TestLoader, TestSuite
from HtmlTestRunner import HTMLTestRunner
from TestLoadFile import *
from TestGrasp import *

if __name__ == '__main__':
    tests_loadfile = TestLoader().loadTestsFromTestCase(TestLoadFile)
    tests_grasp = TestLoader().loadTestsFromTestCase(TestGrasp)

    suite = TestSuite([tests_loadfile, tests_grasp])

    runner = HTMLTestRunner(combine_reports=True, report_name="TestReport", add_timestamp=True)

    runner.run(suite)
