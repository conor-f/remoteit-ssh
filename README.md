# remoteit-ssh

A simple tool to let you automatically SSH into remote.it devices based on
their names.


## Config

Set up your config as an `ini` file as follows:

```
[default]
R3_ACCESS_KEY_ID = abcdefg
R3_SECRET_ACCESS_KEY = abcdefg

[test]
R3_ACCESS_KEY_ID = abcdefg
R3_SECRET_ACCESS_KEY = abcdefg

[prod]
R3_ACCESS_KEY_ID = abcdefg
R3_SECRET_ACCESS_KEY = abcdefg
```


## Usage

```
$ # Normal usage:
$ remoteit-ssh <device name or partial>

$ # Using specific profile:
$ remoteit-ssh --profile test <device name or partial>

$ # Help:
$ remoteit-ssh --help
```
