#!/bin/bash

set -x

## 1. Trap error 
status=0
trap 'status=1' ERR

## 2. Run tests
dmypy run -- --follow-imports=skip src/code_corrector
flake8 --config .flake8 src/code_corrector
vulture src/code_corrector

## 3. Throw error if any tests failed
exit $status
