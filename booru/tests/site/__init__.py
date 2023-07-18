from ..selective import import_required, TestInstance

import_required([
    TestInstance('site_homepage', 'booru.tests.site.homepage'),
    TestInstance('site_upload', 'booru.tests.site.upload'),
    TestInstance('site_tags', 'booru.tests.site.tags'),
    TestInstance('site_users', 'booru.tests.site.users'),
    TestInstance('site_filters', 'booru.tests.site.filters'),
    TestInstance('site_posts', 'booru.tests.site.posts'),
    TestInstance('site_random', 'booru.tests.site.random'),
    TestInstance('site_pools', 'booru.tests.site.pools'),
], globals(), locals())