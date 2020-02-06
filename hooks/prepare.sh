#!/bin/bash
echo 'Instaling gitpython'
pip3 install gitpython
echo 'Making hooks executable'
chmod +x commit-msg
chmod +x pre-commit
chmod +x pre-push