#!/bin/bash

set -x

## 1. Trap error 
status=0
trap 'status=1' ERR

## 2. Run tests
dmypy run -- --follow-imports=skip src
flake8 --config .flake8 src
vulture src

## 3. Throw error if any tests failed
exit $status
