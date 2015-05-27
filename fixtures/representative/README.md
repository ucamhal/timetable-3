This directory contains a small dataset intended to be representative of all
of the types of data encountered in Timetable.

The ``django-fixture.json`` file was created using:

    $ dj dumpdata --indent=4 --format=json -e timetables.ThingLock timetables

``gh-data.csv`` was created by loading ``django-fixture.json`` into a clean Timetable install, then running:

    $ dj grasshopper_export_data

``gh-tree.json`` was created by running [``etc/scripts/timetable/old-stack-import/generate-tree.js``](https://github.com/fronteerio/grasshopper/blob/bd5741355509af84d2b374172579b17d83e72ac5/etc/scripts/timetable/old-stack-import/generate-tree.js) from the [grasshopper](https://github.com/fronteerio/grasshopper) repo on ``gh-data.csv``.

The data in all 3 files has been manually verified to be mutually consistent.
