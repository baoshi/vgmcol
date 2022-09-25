#!/usr/bin/env bash

add_to_path() {
  for d; do
    d=$({ cd -- "$d" && { pwd -P || pwd; } } 2>/dev/null)  # canonicalize symbolic links
    if [ -z "$d" ]; then continue; fi  # skip nonexistent directory
    case ":$PATH:" in
      *":$d:"*) :;;
      *) PATH=$d:$PATH;;
    esac
  done
}

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SYS=`uname -s`
ARCH=`uname -m`
add_to_path ${SCRIPT_DIR}/tools/${SYS}_${ARCH} 

