#!/bin/sh
# Download all OGF Grid Forum Documents (GFD) to the current folder,
# skipping existing GFD.

# Stop after $maxgap failed download attempts.
maxgap=5

# verbose?
verbose=0

# Check which files have already been downloaded and store in an array
existing=(`ls -1 GFD.*.pdf | sed 's/[^0-9]//g' | sort -n`)
len=${#existing[*]} #Number of elements of the array

echo "Found ${#existing[*]} existing GFD."

gapcount=0
number=1
aindex=0
while true; do
    if [[ "$number" -eq "${existing[$aindex]}" ]] ; then
        if [[ "$verbose" -eq "1" ]]; then
            echo "Skip GFD.$number.pdf" # (found in index $aindex)
        fi
        let aindex++
        gapcount=0
    else
        echo -n "Downloading GFD.$number.pdf ... ";
        `wget -q http://www.ogf.org/documents/GFD.$number.pdf`
        code=$?
        if [ "$code" -eq "0" ]; then
            echo "Succeeded"
            gapcount=0
        else
            echo "Failed"
            let gapcount++
        fi
        if [ "$gapcount" -ge "$maxgap" ]; then
            if [[ "$verbose" -eq "1" ]]; then
                echo "$gapcount failed download attempts.";
            fi
            break
        fi
    fi
    let number++
done
echo "Done";
