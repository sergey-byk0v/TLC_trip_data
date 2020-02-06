#!/bin/bash
echo 'Instaling gitpython'
pip3 install gitpython
mv -f commit-msg ../.git/hooks/commit-msg
mv -f pre-commit ../.git/hooks/pre-commit
mv -f pre-push ../.git/hooks/pre-push