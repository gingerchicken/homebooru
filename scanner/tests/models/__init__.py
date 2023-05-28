from booru.tests.selective import import_required, TestInstance

import_required([
    TestInstance('scanner_models_booru', 'scanner.tests.models.booru'),
    TestInstance('scanner_models_scanner', 'scanner.tests.models.scanner'),
    TestInstance('scanner_models_searchresult', 'scanner.tests.models.searchresult'),
    TestInstance('scanner_models_scannerignore', 'scanner.tests.models.scannerignore'),

], globals(), locals())