  SERVER="http://181.215.18.43"


  dump_ui()
  {
      uiautomator dump /sdcard/window.xml >/dev/null 2>&1
  }

  # ==================================================
  # Change Instagram account
  # ==================================================

  change_account()
  {
      echo ""
      echo "=================================================="
      echo "              CHANGING ACCOUNT"
      echo "=================================================="


      # ==================================================
      # 1. Ask server for next username
      # ==================================================

      echo "Requesting next account from server..."

      response=$(curl -s \
          --connect-timeout 30 \
          --max-time 10 \
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
      # 2. Go to Instagram Home
      # ==================================================

      echo "Opening Instagram home..."

      am force-stop com.instagram.android
      monkey -p com.instagram.android 1

      sleep 4


      # ==================================================
      # 3. Click profile/avatar tab
      # ==================================================

      dump_ui

      line=$(grep -o \
          '<node[^>]*resource-id="com.instagram.android:id/tab_avatar"[^>]*/>' \
          /sdcard/window.xml | head -1)

      if [ -z "$line" ]; then
          echo "ERROR: Profile/avatar button not found."
          return 1
      fi

      bounds=$(echo "$line" | grep -o \
          'bounds="\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]"')

      coords=$(echo "$bounds" | sed \
          's/bounds="\[\([0-9]*\),\([0-9]*\)\]\[\([0-9]*\),\([0-9]*\)\]"/\1 \2 \3 \4/')

      set -- $coords

      x=$((($1 + $3) / 2))
      y=$((($2 + $4) / 2))

      echo "Clicking profile/avatar at X=$x Y=$y"

      input tap "$x" "$y"

      sleep 1.5


      # ==================================================
      # 4. Click account username/title
      # ==================================================

      dump_ui

      line=$(grep -o \
          '<node[^>]*resource-id="com.instagram.android:id/action_bar_title"[^>]*/>' \
          /sdcard/window.xml | head -1)

      if [ -z "$line" ]; then
          echo "ERROR: Account title not found."
          return 1
      fi

      bounds=$(echo "$line" | grep -o \
          'bounds="\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]"')

      coords=$(echo "$bounds" | sed \
          's/bounds="\[\([0-9]*\),\([0-9]*\)\]\[\([0-9]*\),\([0-9]*\)\]"/\1 \2 \3 \4/')

      set -- $coords

      x=$((($1 + $3) / 2))
      y=$((($2 + $4) / 2))

      echo "Clicking account title at X=$x Y=$y"

      input tap "$x" "$y"

      sleep 1


      # ==================================================
      # 5. Find target username
      # ==================================================

      max_scrolls=10
      scroll_count=0
      account_found=0

      while [ "$scroll_count" -le "$max_scrolls" ]; do

          echo ""
          echo "Searching for account: $username"
          echo "Scroll attempt: $scroll_count / $max_scrolls"

          dump_ui


          # ------------------------------------------
          # Search exact username in UI
          # ------------------------------------------

          line=$(grep -o \
              "text=\"$username\"[^>]*bounds=\"\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]\"" \
              /sdcard/window.xml | head -1)


          if [ -n "$line" ]; then

              account_found=1

              echo "Found account: $username"

              bounds=$(echo "$line" | sed \
                  's/.*bounds="\[\(.*\),\(.*\)\]\[\(.*\),\(.*\)\]".*/\1 \2 \3 \4/')

              set -- $bounds

              x=$((($1 + $3) / 2))
              y=$((($2 + $4) / 2))

              echo "Clicking $username at X=$x Y=$y"

              input tap "$x" "$y"

              sleep 2

              break
          fi


          # ------------------------------------------
          # Not found -> scroll
          # ------------------------------------------

          if [ "$scroll_count" -eq "$max_scrolls" ]; then
              break
          fi

          echo "Account not visible. Scrolling..."

          input swipe 540 1460 540 900 400

          sleep 0.7

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

      else

          echo ""
          echo "=========================================="
          echo "ERROR: Account not found"
          echo "Username: $username"
          echo "=========================================="

          return 1
      fi
  }

#  change_account

dump_ui
change_account
