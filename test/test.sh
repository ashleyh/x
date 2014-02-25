#!/bin/bash

fails=0
assert() {
  if ! eval "[[ $* ]]" ; then
    echo "FAIL: $*"
    let fails+=1
  else
    echo "PASS: $*"
  fi
}

if ! type realpath &>/dev/null ; then
  echo "Missing realpath..."
  exit 1
fi

script=$(realpath "$0")

if [[ ! "$0" -ef "$script" ]] ; then
  echo "Sanity check failed"
  exit 1
fi

home=$(dirname "$script")
x=$home/../x
tmp=$(mktemp -d -t test)

if [[ ! -d "$tmp" ]] ; then
  echo "Failed to create temporary directory"
  exit 1
fi

echo "Working in $tmp"
cd "$tmp"

cleanup() {
  echo "Cleaning up..."
  cd "$home"
  if [[ "$tmp" = /tmp/* ]] ; then
    rm -rf "$tmp"
  else
    echo "Cowardly refusing to rm -rf $tmp"
  fi
}

trap cleanup EXIT

cp "$home/rooted.tar" rooted.tar
cp "$home/unrooted.tar" unrooted.tar

"$x" rooted.tar

assert -d root
assert -f root/a
assert -f root/b
assert ! -e rooted.tar

"$x" unrooted.tar

assert -d unrooted
assert -f unrooted/a
assert -f unrooted/b

echo "$fails failures"

if [[ "$fails" -gt 0 ]] ; then exit 1 ; fi
