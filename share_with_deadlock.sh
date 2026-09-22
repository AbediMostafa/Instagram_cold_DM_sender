#!/system/bin/sh

SERVER="http://181.215.18.43"

# ==========================================================
# CONFIGURATION
# ==========================================================

MAX_RUNTIME=540
RUNS_PER_ACCOUNT=5

LOCK_DIR="/sdcard/duo_workflow.lock"
LOCK_PID="$LOCK_DIR/pid"

START_TIME=$(date +%s)
DEADLINE=$((START_TIME + MAX_RUNTIME))


# ==========================================================
# LOCK
# ==========================================================

acquire_lock()
{
    if mkdir "$LOCK_DIR" 2>/dev/null; then

        echo "$$" > "$LOCK_PID"

        echo "Lock acquired. PID=$$"

        return 0
    fi


    # Lock already exists
    if [ -f "$LOCK_PID" ]; then

        old_pid=$(cat "$LOCK_PID" 2>/dev/null)

        if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then

            echo ""
            echo "=================================================="
            echo "ANOTHER WORKFLOW IS ALREADY RUNNING"
            echo "PID: $old_pid"
            echo "Exiting this scheduled run."
            echo "=================================================="

            return 1
        fi
    fi


    # Stale lock
    echo "Removing stale lock..."

    rm -rf "$LOCK_DIR"

    if mkdir "$LOCK_DIR" 2>/dev/null; then

        echo "$$" > "$LOCK_PID"

        echo "Lock acquired after removing stale lock."

        return 0
    fi

    echo "ERROR: Could not acquire lock."

    return 1
}


release_lock()
{
    if [ -f "$LOCK_PID" ]; then

        old_pid=$(cat "$LOCK_PID" 2>/dev/null)

        if [ "$old_pid" = "$$" ]; then
            rm -rf "$LOCK_DIR"
            echo "Lock released."
        fi
    fi
}


trap release_lock EXIT
trap release_lock INT
trap release_lock TERM


# ==========================================================
# CHECK TIME
# ==========================================================

time_remaining()
{
    now=$(date +%s)

    remaining=$((DEADLINE - now))

    echo "$remaining"
}


has_time()
{
    now=$(date +%s)

    if [ "$now" -lt "$DEADLINE" ]; then
        return 0
    fi

    return 1
}


# ==========================================================
# SAFE SLEEP
# ==========================================================

safe_sleep()
{
    seconds="$1"

    if ! has_time; then
        return 1
    fi

    remaining=$(time_remaining)

    if [ "$seconds" -gt "$remaining" ]; then
        seconds="$remaining"
    fi

    if [ "$seconds" -gt 0 ]; then
        sleep "$seconds"
    fi

    has_time
}


# ==========================================================
# UI DUMP
# ==========================================================

dump_ui()
{
    uiautomator dump /sdcard/window.xml >/dev/null 2>&1
}


# ==========================================================
# GET BOUNDS CENTER
#
# Input:
#   complete XML node/line
#
# Output:
#   X Y
# ==========================================================

get_center()
{
    line="$1"

    bounds=$(echo "$line" | grep -o \
        'bounds="\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]"')

    if [ -z "$bounds" ]; then
        return 1
    fi

    coords=$(echo "$bounds" | sed \
        's/bounds="\[\([0-9]*\),\([0-9]*\)\]\[\([0-9]*\),\([0-9]*\)\]"/\1 \2 \3 \4/')

    set -- $coords

    if [ -z "$4" ]; then
        return 1
    fi

    x=$((($1 + $3) / 2))
    y=$((($2 + $4) / 2))

    echo "$x $y"
}


# ==========================================================
# FIND AND CLICK RESOURCE ID
# ==========================================================

click_resource()
{
    resource_id="$1"
    description="$2"

    dump_ui

    line=$(grep -o \
        "<node[^>]*resource-id=\"$resource_id\"[^>]*/>" \
        /sdcard/window.xml | head -1)

    if [ -z "$line" ]; then

        echo "ERROR: $description not found."

        return 1
    fi

    coords=$(get_center "$line")

    if [ -z "$coords" ]; then

        echo "ERROR: Could not determine $description coordinates."

        return 1
    fi

    set -- $coords

    x="$1"
    y="$2"

    echo "Clicking $description at X=$x Y=$y"

    input tap "$x" "$y"

    return 0
}


# ==========================================================
# CHANGE INSTAGRAM ACCOUNT
# ==========================================================

change_account()
{
    echo ""
    echo "=================================================="
    echo "              CHANGING ACCOUNT"
    echo "=================================================="


    if ! has_time; then
        echo "Time limit reached. Cannot change account."
        return 1
    fi


    # ==================================================
    # 1. Ask server for next username
    # ==================================================

    echo "Requesting next account from server..."

    response=$(curl -s \
        --connect-timeout 5 \
        --max-time 8 \
        -X POST \
        "$SERVER/duo-workflow/change-account" \
        -H "Content-Type: application/json" \
        -d "{\"phone_id\":\"${dp_cloud_phone_id}\"}")

    echo "Change account response: $response"

    username=$(echo "$response" | tr -d '\r\n')

    if [ -z "$username" ]; then

        echo "ERROR: Could not get username from server."

        return 1
    fi

    echo "Next username: $username"


    # ==================================================
    # 2. Open Instagram
    # ==================================================

    if ! has_time; then
        return 1
    fi

    echo "Opening Instagram home..."

    am force-stop com.instagram.android

    monkey -p com.instagram.android 1 >/dev/null 2>&1

    safe_sleep 3 || return 1


    # ==================================================
    # 3. Click profile/avatar
    # ==================================================

    click_resource \
        "com.instagram.android:id/tab_avatar" \
        "profile/avatar button" || return 1

    safe_sleep 1.5 || return 1


    # ==================================================
    # 4. Click account title
    # ==================================================

    click_resource \
        "com.instagram.android:id/action_bar_title" \
        "account title" || return 1

    safe_sleep 1 || return 1


    # ==================================================
    # 5. Find target username
    # ==================================================

    max_scrolls=10
    scroll_count=0
    account_found=0

    while [ "$scroll_count" -le "$max_scrolls" ]; do

        if ! has_time; then
            echo "Time limit reached while changing account."
            return 1
        fi

        echo ""
        echo "Searching for account: $username"
        echo "Scroll attempt: $scroll_count / $max_scrolls"

        dump_ui


        line=$(grep -o \
            "text=\"$username\"[^>]*bounds=\"\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]\"" \
            /sdcard/window.xml | head -1)


        if [ -n "$line" ]; then

            account_found=1

            echo "Found account: $username"

            coords=$(get_center "$line")

            if [ -z "$coords" ]; then
                echo "ERROR: Could not determine username coordinates."
                return 1
            fi

            set -- $coords

            x="$1"
            y="$2"

            echo "Clicking $username at X=$x Y=$y"

            input tap "$x" "$y"

            safe_sleep 2 || return 1

            break
        fi


        if [ "$scroll_count" -eq "$max_scrolls" ]; then
            break
        fi


        echo "Account not visible. Scrolling..."

        input swipe 540 1460 540 900 400

        safe_sleep 0.7 || return 1

        scroll_count=$((scroll_count + 1))

    done


    # ==================================================
    # Result
    # ==================================================

    if [ "$account_found" -eq 1 ]; then

        echo ""
        echo "=========================================="
        echo "Account changed successfully"
        echo "Username: $username"
        echo "=========================================="

        return 0

    fi


    echo ""
    echo "=========================================="
    echo "ERROR: Account not found"
    echo "Username: $username"
    echo "=========================================="

    return 1
}

is_invalid_post()
{
    dump_ui

    if grep -qi \
        -e 'Sorry, this page isn.t available' \
        -e 'Get the full experience' \
        -e 'Open Instagram' \
        -e 'This profile is private' \
        /sdcard/window.xml; then

        return 0
    fi

    return 1
}


fail_workflow()
{
    reason="$1"
    workflow_id="$2"

    echo ""
    echo "=========================================="
    echo "WORKFLOW FAILED"
    echo "Reason: $reason"
    echo "=========================================="

    # Call your server here
    response=$(curl -s \
        --connect-timeout 5 \
        --max-time 10 \
        -X POST \
        "$SERVER/duo-workflow/fail" \
        -H "Content-Type: application/json" \
        -d "{\"workflow_id\":\"$workflow_id\",\"reason\":\"$reason\"}")

    echo "Server response:"
    echo "$response"

    return 1
}


# ==========================================================
# START WORKFLOW
# ==========================================================

start_workflow()
{
    if ! has_time; then
        return 1
    fi


    echo "Requesting workflow from server..."

    response=$(curl -s \
        --connect-timeout 5 \
        --max-time 8 \
        -X POST \
        "$SERVER/duo-workflow/start" \
        -H "Content-Type: application/json" \
        -d "{\"phone_id\":\"${dp_cloud_phone_id}\"}")

    echo "Server response: $response"

     # ==================================================
        # No order available
        # ==================================================

        if [ "$response" = "-1" ]; then

            echo ""
            echo "=================================================="
            echo "NO ORDER AVAILABLE"
            echo "Waiting 60 seconds before trying again..."
            echo "=================================================="

            sleep 80

            return 2
        fi


    action_count=$(echo "$response" | sed \
        -n 's/.*"action_count":\([0-9]*\).*/\1/p')

    url=$(echo "$response" | sed \
        -n 's/.*"url":"\([^"]*\)".*/\1/p' | sed 's#\\/#/#g')

    url=$(echo "$url" | sed 's#/reel/#/p/#')

    workflow_id=$(echo "$response" | sed \
        -n 's/.*"workflow_id":\([0-9]*\).*/\1/p')


    echo "action_count=$action_count"
    echo "url=$url"
    echo "workflow_id=$workflow_id"

    if [ -z "$action_count" ] || \
       [ -z "$url" ] || \
       [ -z "$workflow_id" ]; then

        echo "ERROR: Invalid response from server."

        return 1
    fi


    # ==================================================
    # Open Instagram URL
    # ==================================================

    echo "Opening Instagram URL..."

    am start \
        -a android.intent.action.VIEW \
        -d "$url" \
        com.instagram.android

    sleep 3

     # ==================================================
      # Check if post/reel is unavailable
      # ==================================================

      echo "Checking whether Instagram post is available..."

      if is_invalid_post; then

          echo ""
          echo "=========================================="
          echo "INVALID / UNAVAILABLE POST DETECTED"
          echo "=========================================="

          dump_ui

          fail_workflow "instagram_post_not_available" "$workflow_id"

          return 1
      fi


      echo "Post appears to be available."
    # ==================================================
    # Click Share
    # Supports:
    #
    # Normal post:
    #   row_feed_button_share
    #
    # Reel:
    #   direct_share_button
    #
    # Try both buttons up to 3 times
    # ==================================================

    echo "Looking for Share button..."

    share_clicked=0

    for attempt in 1 2; do
        echo ""
        echo "=========================================="
        echo "Share button attempt $attempt / 2"
        echo "=========================================="

        # Try normal post Share button
        if click_resource \
            "com.instagram.android:id/row_feed_button_share" \
            "Normal Share button"; then

            echo "Normal post Share button clicked."
            share_clicked=1
            break
        fi

        # Try Reel Share button
        echo "Normal Share button not found."
        echo "Trying Reel Share button..."

        if click_resource \
            "com.instagram.android:id/direct_share_button" \
            "Reel Share button"; then

            echo "Reel Share button clicked."
            share_clicked=1
            break
        fi

        echo "No Share button found on attempt $attempt."

        if [ "$attempt" -lt 2 ]; then
            echo "Waiting before retry..."
            sleep 1
        fi

        input swipe 540 1296 540 1180 500
    done

    # Check result
    if [ "$share_clicked" -eq 0 ]; then
        echo ""
        echo "=========================================="
        echo "ERROR: No Share button found after 2 attempts."
        echo ""
        echo "Tried:"
        echo "  - row_feed_button_share"
        echo "  - direct_share_button"
        echo "=========================================="

        echo ""
        echo "Current UI XML:"
        dump_ui
        cat /sdcard/window.xml

        return 1
    fi

    echo ""
    echo "Share button clicked successfully."

    # ==================================================
    # Initial scrolling
    # ==================================================

    sleep 2

    input swipe 540 1643 540 1000 500
    sleep 0.5
    input swipe 540 1296 540 1140 200

    sleep 0.3

    # ==================================================
    # Click share groups
    # ==================================================

    clicked=0
    no_new_groups=0
    max_no_new_groups=5

    clicked_groups=""


    while [ "$clicked" -lt "$action_count" ]; do

        if ! has_time; then
            echo "Time limit reached during group processing."
            return 1
        fi


        echo ""
        echo "========== GROUP LOOP =========="
        echo "Clicked: $clicked / $action_count"
        echo "No new groups: $no_new_groups / $max_no_new_groups"


        dump_ui


        grep -o \
            'text="share_group[^"]*"[^>]*bounds="\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]"' \
            /sdcard/window.xml > /sdcard/share_groups.txt


        new_groups_this_screen=0


        while read -r line; do

            if [ "$clicked" -ge "$action_count" ]; then
                break
            fi

            if ! has_time; then
                return 1
            fi


            group=$(echo "$line" | sed \
                's/.*text="\(share_group_[0-9]*\)".*/\1/')


            if [ -z "$group" ]; then
                continue
            fi


            # ------------------------------------------
            # Skip already clicked
            # ------------------------------------------

            case " $clicked_groups " in

                *" $group "*)

                    echo "Already clicked: $group"

                    continue
                    ;;

            esac


            coords=$(get_center "$line")

            if [ -z "$coords" ]; then
                continue
            fi

            set -- $coords

            x="$1"
            y="$2"

            echo "Clicking $group at $x,$y"
            input tap "$x" "$y"
            sleep 0.3

            clicked_groups="$clicked_groups $group"

            clicked=$((clicked + 1))

            new_groups_this_screen=$((new_groups_this_screen + 1))


            echo "Clicked: $group"
            echo "Progress: $clicked / $action_count"

        done < /sdcard/share_groups.txt


        # ==================================================
        # Completed
        # ==================================================

        if [ "$clicked" -ge "$action_count" ]; then
            break
        fi


        # ==================================================
        # Nothing new
        # ==================================================

        if [ "$new_groups_this_screen" -eq 0 ]; then

            no_new_groups=$((no_new_groups + 1))

            echo "No new groups found."
            echo "Attempt: $no_new_groups / $max_no_new_groups"

        else

            no_new_groups=0

        fi


        # ==================================================
        # Prevent infinite scrolling
        # ==================================================

        if [ "$no_new_groups" -ge "$max_no_new_groups" ]; then

            echo ""
            echo "ERROR: No new groups found."
            echo "Clicked $clicked / $action_count"

            return 1
        fi


        echo "Scrolling for more groups..."

        input swipe 540 1460 540 350 400
        sleep 0.7

    done


    echo ""
    echo "Finished groups."
    echo "Total unique clicks: $clicked / $action_count"
    echo "Clicked groups: $clicked_groups"


    # ==================================================
    # Wait for Send
    # ==================================================

    found=0
    button_type=""


    for i in $(seq 1 5); do

        if ! has_time; then
            return 1
        fi


        dump_ui


        line=$(grep -o \
            'text="Send separately"[^>]*bounds="\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]"' \
            /sdcard/window.xml | head -1)


        if [ -n "$line" ]; then

            found=1
            button_type="Send separately"

            break
        fi


        line=$(grep -o \
            'text="Send"[^>]*bounds="\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]"' \
            /sdcard/window.xml | head -1)


        if [ -n "$line" ]; then

            found=1
            button_type="Send"

            break
        fi


        echo "Waiting for Send... $i/5"

        safe_sleep 0.2 || return 1

    done


    if [ "$found" -ne 1 ]; then

        echo "ERROR: Send button did not appear."

        return 1
    fi


    # ==================================================
    # Click Send
    # ==================================================

    coords=$(get_center "$line")

    if [ -z "$coords" ]; then

        echo "ERROR: Could not determine Send coordinates."

        return 1
    fi


    set -- $coords

    x="$1"
    y="$2"


    echo "Clicking '$button_type' at X=$x Y=$y"

    input tap "$x" "$y"


    echo "'$button_type' clicked successfully."


    # ==================================================
    # Notify server
    # ==================================================

    group_clicked=$(curl -s \
        --connect-timeout 5 \
        --max-time 8 \
        -X POST \
        "$SERVER/duo-workflow/group-click" \
        -H "Content-Type: application/json" \
        -d "{\"workflow_id\":\"$workflow_id\"}")


    echo "Group click response: $group_clicked"


    echo "Workflow completed."

    return 0
}


# ==========================================================
# ACQUIRE LOCK
# ==========================================================

if ! acquire_lock; then
    exit 0
fi


echo ""
echo "=================================================="
echo "       DUOPLUS WORKFLOW STARTED"
echo "=================================================="

echo "PID: $$"
echo "Maximum runtime: ${MAX_RUNTIME}s"
echo "Deadline: $DEADLINE"


# ==========================================================
# MAIN LOOP
#
# Keep processing accounts until the 9-minute deadline.
#
# Each account:
#
#   5 workflows
#        ↓
#   change account
#        ↓
#   5 workflows
#        ↓
#   change account
#        ↓
#   ...
# ==========================================================

account_cycle=0


while has_time; do

    account_cycle=$((account_cycle + 1))


    echo ""
    echo "##################################################"
    echo "ACCOUNT CYCLE: $account_cycle"
    echo "TIME REMAINING: $(time_remaining)s"
    echo "##################################################"


    completed_runs=0


    # ==================================================
    # Run 5 workflows for current account
    # ==================================================

    while [ "$completed_runs" -lt "$RUNS_PER_ACCOUNT" ]; do

        if ! has_time; then

            echo ""
            echo "Time limit reached."
            break 2
        fi


        run=$((completed_runs + 1))


        echo ""
        echo "=================================================="
        echo "STARTING RUN $run / $RUNS_PER_ACCOUNT"
        echo "ACCOUNT CYCLE: $account_cycle"
        echo "TIME REMAINING: $(time_remaining)s"
        echo "=================================================="


        if start_workflow; then

            echo "Run $run completed successfully."

        else

            echo "Run $run failed."

        fi


        completed_runs=$((completed_runs + 1))


        # Small pause before next run

        if [ "$completed_runs" -lt "$RUNS_PER_ACCOUNT" ]; then

            safe_sleep 0.5 || break 2

        fi

    done


    # ==================================================
    # DO NOT CHANGE ACCOUNT IF WE ARE NEAR DEADLINE
    # ==================================================

    remaining=$(time_remaining)

    echo ""
    echo "Finished $completed_runs / $RUNS_PER_ACCOUNT runs."
    echo "Time remaining: ${remaining}s"


    # Keep a safety margin.
    #
    # Account changing can take several seconds.
    # Do not start another account change if less
    # than 30 seconds remain.

    if [ "$remaining" -lt 30 ]; then

        echo ""
        echo "Less than 30 seconds remaining."
        echo "Stopping before account change."

        break
    fi


    # ==================================================
    # CHANGE ACCOUNT
    # ==================================================

    echo ""
    echo "Changing account..."

    if ! change_account; then

        echo "WARNING: Account change failed."

        # Don't immediately hammer the server/UI.
        # Give the current cycle a short pause.

        safe_sleep 1 || break

    fi


done


# ==========================================================
# FINISHED
# ==========================================================

echo ""
echo "=================================================="
echo "          WORKFLOW TIME LIMIT REACHED"
echo "=================================================="

echo "Total account cycles: $account_cycle"
echo "Runtime: $(( $(date +%s) - START_TIME )) seconds"
echo "Time remaining: $(time_remaining)s"

echo ""
echo "Stopping workflow."

exit 0