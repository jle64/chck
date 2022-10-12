NAME
----

`chck.py`

SYNOPSIS
--------

```shell
chck.py [-h|--help] [-g|--globbing PATTERN] [-m|--mtime] [-v|--verbose] DIRECTORY HISTORY_FILE
```

DESCRIPTION
-----------

Periodically check a directory for changes in files with distinction between actually modified files and files to which data got appended to.

This is done by performing a checksum of all files in a directory (optionally filtered by a glob pattern) and saving it to an history file, along with the file size, then looking for changes on the next run. If a file is bigger than it was, both a checksum of the whole file and a checksum limited to the file former size are done, so we can distinguish between the cases of modified data or appended data. After every run, the history file is rotated.

This can be useful for example to check the integrity of files that can still be written to but should not be modified (log files for example).

FILES STATUSES
--------------

Files can have the following statuses:

* changed (modified)
* changed (appended to)
* ignored (not a file)
* ignored (mtime unchanged)
* new
* removed
* unchanged

EXAMPLES
--------

A simple check needs only the path of a directory on which to perform the check on, and a json file that will store the files informations history:

```shell
./chck.py --verbose my_directory my_history_file.json
```

You can get the output on stdout in verbose (`-v|--verbose`) mode:

```shell
./chck.py --verbose /var/log /var/log/log.history.json
```
outputs:

```
STATUS                    SIZE      CHECKSUM                                                         NAME
new                       4         17e682f060b5f8e47ea04c5c4855908b0a5ad612022260fe50e11ecb0cc0ab76 /var/log/mail.log
unchanged                 0         e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 /var/log/auth.log
changed (appended to)     8         d892da858d1ffbb89c0a392933a9f2a19342e8da2e81be44f78dadfba9f6fe83 /var/log/system.log
changed (modified)        4         17e682f060b5f8e47ea04c5c4855908b0a5ad612022260fe50e11ecb0cc0ab76 /var/log/dmesg.log
```

By default, globbing is done on `*`. This can be changed using the `-g|--glob` option, for example to `**/*` to perform a recursive check, or `*.ext` to check only for a specific extension:

```shell
./chck.py --glob '*/**.log' /var/log /var/log.history.json
```

It's also possible to pass the `-m|--mtime` option to avoid performing checks on files whose mtime hasn't changed:

```shell
./chck.py --mtime /var/log /var/log.history.json
```

FILES
-----

The history file is in `json` format, and is rotated at every run, with the previous file being kept with `-bak-(CURRENT DATE)` appended to its name.
