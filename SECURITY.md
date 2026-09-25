# Security policy

This is an offline game with no network access, but it reads YAML and JSON
files (settings, saves, maps) that could be shared between players. Files are
read with `yaml.safe_load` and validated maps only.

## Supported versions

Only the latest version of the `main` branch receives fixes.

## Reporting a vulnerability

Please do **not** open a public issue. Use
[GitHub private vulnerability reporting](https://github.com/naulan-chrzaszcz/SuperMarioBros.3-pygame/security/advisories/new)
(the *Security* tab of the repository), with the steps to reproduce and the
affected files. You will get an answer within two weeks; once fixed, the
issue will be credited to you if you wish.
