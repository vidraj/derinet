# What to do when releasing a new version (especially a major one)

## Building

1. Prepare the build and commit everything.
2. Build locally.
3. Make a clean checkout (preferably on a clean computer).
4. Build from the clean checkout.
5. Verify that the builds match each other and your expectations.
6. Try a load-save roundtrip of the new version and verify that the
   roundtripped version works.


## Publishing

1. Commit the built DB into `data/releases/`.
2. Tag using `git tag v2.X.Y -m 'Snapshot as of version 2.X.Y'`.
3. `git push && git push --tags`
4. Update the list of authors in the README for DeriSearch.
5. Upload the new version to DeriSearch2.
6. Update the website at <https://ufal.mff.cuni.cz/derinet>.
