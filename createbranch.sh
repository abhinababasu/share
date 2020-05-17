#!/bin/bash

# should have one argument 
if [ -z "$1" ]; then
    echo "No branch name supplied"
    exit 1
fi

# branch name should start with abhinab
if ! [[ $1 =~ ^abhinab.+ ]]; then
    echo "$1 is not the right branch name format. Should start with abhinab"
    exit 2
fi

# no remote branch with that name
count="$(git branch -a | grep $1 | wc -l)"
if ! [ "$count" -eq 0 ]; then
    echo "Branch $1 already exists"
    exit 3
fi

if ! git checkout -b $1; then
    echo "Failed to checkout $1"
    exit 4
fi

if ! git push origin $1; then
    echo "Failed to push branch $1"
    echo 5
fi

if ! git branch --set-upstream-to=origin/$1; then
    echo "Failed to setup stream to origin/$1"
    echo 6
fi

exit 0
