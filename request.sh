#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <operation> <number> <number>"
    echo "Where <operation> can be:"
    echo "- plus"
    echo "- minus"
    echo "- times"
    echo "- divide"
		exit
fi

curl \
	-X POST	\
	--header "Content-Type: application/json" \
	-d "{ \"operand1\": $2, \"operand2\": $3 }" \
	localhost:5000/$1

echo

