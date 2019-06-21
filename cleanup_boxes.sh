#!/usr/bin/env bash

prefix='bunchc/'
boxes=(
    'cosmic64'
    'trusty64'
    'xenial64'
    'precise64'
    'bionic64'
    'centos5'
    'centos6'
    'centos7'
    'alpine37'
    'alpine38'
    'alpine39'
    'test'
    'stretch64'
    'jessie64'
    'cosmic64-desktop'
    'trusty64-desktop'
    'xenial64-desktop'
    'bionic64-desktop'
    'stretch64-desktop'
    'centos7-desktop'
)

faketty(){
    script -qefc "$(printf "%q " "$@")"
}

for box in ${boxes[@]}; do
    echo "${prefix}${box}"
    printf "y\n" | faketty vagrant cloud box delete ${prefix}${box}
done