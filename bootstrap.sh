cd vendor/source/igraph/

./bootstrap.sh
./configure
make

cd src/

SOURCES=`make echodist | head -1`
SOURCES="$SOURCES ../config.h f2c/arith.h"
headerfile=""
for file in $SOURCES ; do
    if [[ $file == *.y ]]; then
        file="${file%.y}.c"
        headerfile="${file%.c}.h"
    elif [[ $file == *.l ]]; then
        file="${file%.l}.c"
    fi
    if [[ $file == *.c ]] || [[ $file == *.cc ]] || [[ $file == *.cpp ]] || [[ $file == *.h ]] || [[ $file = *.hh ]] || [[ $file == *.pmt ]]
    then
        dir=$(dirname "$file")
        mkdir -p "../../../../src/core/src/$dir"
        cp "$file" "../../../../src/core/src/$file"
        echo "Copy $file"
        if [ -n "$headerfile" ]; then
            cp "$headerfile" "../../../../src/core/src/$headerfile"
            echo "Copy $headerfile"
        fi
    else
        echo "Ignoring $file"
    fi
    headerfile=""
done

cd ../../../../
