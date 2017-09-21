from django.test import TestCase

from news_scraper.scraper.pipelines.reddit import is_title_ignored


class RedditPipelineTest(TestCase):
    def test_ignored_titles(self):
        """Test detection of ignored titles."""

        self.assertTrue(is_title_ignored(title='Daily discussion - September 22nd, 2017',
                                         ignored_regexes=[r'^(Daily discussion)']))
        self.assertFalse(is_title_ignored(title='PSA: Please update Neon Wallet to 0.0.5.',
                                          ignored_regexes=[r'^(Daily discussion)']))
