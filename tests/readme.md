## Configuration

### Required Environmental vars

* `SESSION` String session of the user
* `PEER` Username/id of the user
* `API_ID` ...
* `API_HASH` ...

### Test Coverage

Running test creates `.coverage`, `coverage.xml` (in `reports/` dir)

> If you are using Jetbrains IDE, you can load `coverage.xml`, `Run > Show Coverage Data > select the coverage.xml`


### Notes

This is integration tests, requires user account to interact with Sophie. During tests sophie runs on `TESTMODE`, loads special module `_tests` which contains corresponding tests functions to interact with utilities!
