
#Request to server to get url and share count
start_time=$(date +%s%3N)

response=$(curl -s -X POST "http://209.200.252.19/duo-workflow/start" \
  -H "Content-Type: application/json" \
  -d "{\"phone_id\":\"${dp_cloud_phone_id}\"}")

end_time=$(date +%s%3N)

request_time=$((end_time - start_time))

echo "POST request time: ${request_time} ms"
echo "POST request time: $(awk "BEGIN {printf \"%.3f\", $request_time/1000}") seconds"

action_count=$(echo "$response" | sed -n 's/.*"action_count":\([0-9]*\).*/\1/p')
url=$(echo "$response" | sed -n 's/.*"url":"\([^"]*\)".*/\1/p' | sed 's#\\/#/#g')
workflow_id=$(echo "$response" | sed -n 's/.*"workflow_id":\([0-9]*\).*/\1/p')

echo "action_count=$action_count"
echo "url=$url"
echo "workflow_id=$workflow_id"

#Start Instagram with given Url
am start -a android.intent.action.VIEW \
  -d "$url" \
  com.instagram.android

sleep 3

#Clicking on Share button
uiautomator dump /sdcard/window.xml >/dev/null

xml=$(cat /sdcard/window.xml | tr '\n' ' ')
line=$(echo "$xml" | grep -o '<node[^>]*resource-id="com.instagram.android:id/row_feed_button_share"[^>]*/>')

bounds=$(echo "$line" | grep -o 'bounds="\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]"')

coords=$(echo "$bounds" | sed 's/bounds="\[\([0-9]*\),\([0-9]*\)\]\[\([0-9]*\),\([0-9]*\)\]"/\1 \2 \3 \4/')

set -- $coords

x=$((($1 + $3) / 2))
y=$((($2 + $4) / 2))

echo "Clicking Send post at X=$x Y=$y"

input tap "$x" "$y"


#Scroll 2 times
sleep 2
input swipe 540 1643 540 1000 500
sleep 0.5
input swipe 540 1296 540 1140 200

clicked=0

while [ "$clicked" -lt "$action_count" ]; do

    echo "========== LOOP =========="
    echo "Clicked: $clicked / $action_count"

    uiautomator dump /sdcard/window.xml >/dev/null

    grep -o 'text="share_group[^"]*"[^>]*bounds="\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]"' \
        /sdcard/window.xml > /sdcard/share_groups.txt

    while read line; do

        if [ "$clicked" -ge "$action_count" ]; then
            break
        fi

        bounds=$(echo "$line" | sed 's/.*bounds="\[\(.*\),\(.*\)\]\[\(.*\),\(.*\)\]".*/\1 \2 \3 \4/')
        set -- $bounds

        x=$((($1 + $3) / 2))
        y=$((($2 + $4) / 2))

        echo "Clicking share_group at $x,$y"

        input tap "$x" "$y"
        sleep 0.3

        clicked=$((clicked + 1))

        echo "Progress: $clicked / $action_count"

    done < /sdcard/share_groups.txt

    if [ "$clicked" -ge "$action_count" ]; then
        break
    fi

    echo "Need more groups. Scrolling..."

    input swipe 540 1460 540 350 400
    sleep 0.7

done

echo "Finished. Total clicks: $clicked"