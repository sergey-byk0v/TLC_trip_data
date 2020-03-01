#!/bin/bash
echo 'Instaling gitpython'
pip3 install gitpython
cp -f commit-msg ../.git/hooks/commit-msg
cp -f pre-commit ../.git/hooks/pre-commit
cp -f pre-push ../.git/hooks/pre-push