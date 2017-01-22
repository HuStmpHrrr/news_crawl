#!/bin/bash

# set -x

SCRIPT=${BASH_SOURCE[0]}
DIR=`readlink -f $(dirname $SCRIPT)`

export PYTHONPATH=$DIR # try to unify the data representation

print_help() {
	cat <<EOF
$SCRIPT -p port -o output_folder -t target

options:
-p		the port to open the http server.
-o		output folder.		
-t		target to crawl. CNN for example.
-h		display rhis help.

EOF
}


PORT=
OUTPUT=
TARGET=

while getopts :p:o:t:h opt; do
	case $opt in
		p) PORT=$OPTARG;;
		o) OUTPUT=$OPTARG;;
		t) TARGET=$OPTARG;;
		h) print_help; exit 0;;
		\?)
			echo "Invalid option: -$OPTARG" >&2
			print_help
			exit 1;;
		:)  
			echo "Option -$OPTARG requires an argument." >&2
			print_help
			exit 1;;
	esac
done

echo "${PORT:?port must be specified.}" > /dev/null
echo "${TARGET:?target must be specified.}" >/dev/null
mkdir -p "${OUTPUT:?output folder must be specified.}"

cp -r "$DIR"/templates/* "$OUTPUT"

twistd -n web -p 8000 --path "$OUTPUT`[ -f "$OUTPUT/index.html" ] && echo /index.html`" &
HTTP_SERVER=$!

cd "$DIR/crawler"
scrapy crawl "$TARGET" --logfile "$OUTPUT/crawler.log" -s OUTPUT_FOLDER="$OUTPUT" -s JOBDIR="$OUTPUT"

python "$DIR/"template.py "$OUTPUT" "$TARGET"

ctrlc() {
	echo "Ctrl+C detected. kill http server before exits..." >&2
	kill -9 $HTTP_SERVER
}

trap ctrlc INT

wait $HTTP_SERVER
