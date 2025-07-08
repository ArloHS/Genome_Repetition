#!/usr/bin/env bash

build_output=$(ant clean compile jar 2>&1)
build_err_found=$?
jar_path="../application.jar"
suite_path="testsuite"
test_path="tests"
rubric_path="rubric.md"
csv_path="results.csv"

function mark() {
  case $1 in
    1)
      mode="1"
      ext="chk"
      ;;

    2)
      mode="2"
      ext="bf"
      ;;

    3)
      mode="3"
      ext="opt"
      ;;

    *)
      echo "Marking all modes"
      for mode in {1..3}; do
        mark $mode
      done
      exit 0
      ;;
  esac

  echo "Testing mode $mode"

  rm -rf ../out
  mkdir -p ../out

  cd ../out
  if [ $mode == "3" ]; then
    timeout 5 java -jar $jar_path 3 3 G 5 &> /dev/null
    rm -f ./*
  fi
  for dir in $(ls -d ../$suite_path/$test_path/mode$mode/$2* | sort -V); do
    [ -e "$dir" ] || continue # check that test directory actually exists
    test=$(basename $dir)
    echo "Running test: $test"
    if [ $build_err_found -eq 1 ]; then
      echo "Compilation error occurred: see error file for more details" > "${test}_$ext.out"
      echo "$build_output" > "${test}_$ext.err"
    else
      if [ $mode == "1" ]; then
        if [ -f "$dir/input.in" ]; then
          args=$(cat $dir/input.in)
        else
          args="$mode $dir/$test.in"
        fi
      else
        args="$mode $(cat $dir/$test.in)"
      fi
      timelimit=$(cat $dir/timeout.txt)
      timeout $timelimit java -jar $jar_path $args 1> "${test}_$ext.out" 2> "${test}_$ext.err"
      if [ $? -eq 124 ]; then
        echo "Time limit exceeded ($timelimit seconds)" >> "${test}_$ext.err"
      fi
      [ $mode != "1" ] && [ ! -f "${test}_$ext.txt" ] && touch "${test}_$ext.txt"
      if [ $mode == "2" ]; then
        cat "${test}_$ext.txt" | sort -V > "${test}_$ext.temp"
        mv "${test}_$ext.temp" "${test}_$ext.txt"
      fi
    fi
  done
  cd ../$suite_path

  python3 testscript.py $1 -p $test_path -r $rubric_path -c $csv_path > /dev/null
}

rm -f "$rubric_path"
rm -f "$csv_path"
mark "$1"
