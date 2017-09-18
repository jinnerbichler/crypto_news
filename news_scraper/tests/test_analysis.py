from django.test import TestCase

from news_scraper.scraper.pipelines.analyse import is_false_positive


class AnalysisTest(TestCase):
    def test_date_filtering(self):
        """Test detection of false positives in date extraction."""

        self.assertFalse(is_false_positive('3 days'))

        false_positives = ['at 2305', 'to mar', '330, at', '20, at', 'of 54', 'of 147,233',
                           '16th', 'of 90', 'by mar', '2017', '500, 4', '', 'may', '1,337',
                           '4,327', 'on to mon', 'of 155 sat', 'at 1,337', 'of 155', '12,33',
                           '276 on Sunday', 'may on', '08t2', '2t', '33d', '7 T', 't 2017',
                           't 12']  # '32 at', 't of 2015', '26 of t', '5000 to', 't 20 t', '10-15', 't-30', '32 at t']
        for fp in false_positives:
            self.assertTrue(is_false_positive(date_source=fp),
                            msg='"{}" is not detected as false positive'.format(fp))

        true_positives = ['on Sunday, 12:23', 'on Monday, 07:01', 'Sunday', 'of September 11th',
                          'of September 11th', 'on Aug', 'on Monday', 'on on Monday', 'September 11th',
                          '3 days', 'one month', 'next month', 'tomorrow']
        for tp in true_positives:
            self.assertFalse(is_false_positive(date_source=tp),
                             msg='"{}" is detected as false positive'.format(tp))
