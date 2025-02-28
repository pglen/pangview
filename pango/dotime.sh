#!/bin/bash
echo "Running: $2"
sleep 5
#echo done sleep
PPP=$(ps xa | grep "$2")
#echo "ppp: '$PPP'"
IFS=$'\n'
for AA in $PPP ; do
	#echo "aa: '$AA'"
	PROCX=$(echo $AA | awk '{ print($1); } ')
	#echo "procx: '$PROCX'"
	SUMX+="$PROCX "
done
#echo  "SUMX $SUMX"
IFS=$' '
for BBB in $SUMX ; do
	#echo Kill: $BBB -- $$
	if [ "$BBB" != "$$" ] ; then
		kill $BBB >/dev/null 2>&1
	fi
done
