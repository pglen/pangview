#!/bin/bash

./dotime.sh $1 $2 &
$1 $2 $3 $4 $5 >/dev/null 2>&1

# EOF
