from booru.tests.selective import import_required, TestInstance

import_required([
    TestInstance('scanner_models', 'scanner.tests.models'),
    TestInstance('scanner_views', 'scanner.tests.views'),
], globals(), locals())