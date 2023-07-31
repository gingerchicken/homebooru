from .selective import import_required, TestInstance

import_required([
    TestInstance('posts', 'booru.tests.models.posts'),
    TestInstance('tags', 'booru.tests.models.tags'),
    TestInstance('profile', 'booru.tests.models.profile'),
    TestInstance('comments', 'booru.tests.models.comments'),
    TestInstance('pagination', 'booru.tests.pagination'),
    TestInstance('boorutils', 'booru.tests.boorutils'),
    TestInstance('pools', 'booru.tests.models.pools'),
    TestInstance('automation', 'booru.tests.automation'),

    TestInstance('site', 'booru.tests.site')
], globals(), locals())