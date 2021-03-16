on run argv
    set thePath to item 1 of argv
    tell application "Terminal"
        activate
        -- tell application "System Events"
        --     repeat while not (name of (first process where it is frontmost)) is equal to "Terminal"
        --         log "delay A"
        --         delay 0.1
        --     end repeat
        -- end tell
        -- log "delay B"

        delay 1
        tell application "System Events" to keystroke "t" using {command down}

        delay 1
        
        -- repeat while contents of selected tab of window 1 starts with linefeed
        --     delay 0.01
        -- end repeat
        do script ("cd " & the quoted form of thePath) in window 1
    end tell
end run
