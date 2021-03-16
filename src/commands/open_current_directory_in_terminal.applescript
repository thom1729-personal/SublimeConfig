on run argv
    set thePath to item 1 of argv
    tell application "Terminal"
        activate

        delay 1
        tell application "System Events" to keystroke "t" using {command down}

        delay 1
        do script ("cd " & the quoted form of thePath) in window 1
    end tell
end run
