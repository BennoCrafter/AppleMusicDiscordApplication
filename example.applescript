tell application "Music"
    if player state is playing then
        set currentTrack to the current track
        set currentArtist to the artist of currentTrack
        set currentName to the name of currentTrack
        set currentDuration to the duration of currentTrack
        set currentPosition to the player position

        set minutesElapsed to (currentPosition div 60) as integer
        set secondsElapsed to (currentPosition mod 60) as integer

        set minutesTotal to (currentDuration div 60) as integer
        set secondsTotal to (currentDuration mod 60) as integer

        return currentName & " - " & currentArtist & "\\n" & "Time: " & minutesElapsed & ":" & text -2 thru -1 of ("0" & secondsElapsed) & " / " & minutesTotal & ":" & text -2 thru -1 of ("0" & secondsTotal)
    else
        return "No music is currently playing."
    end if
end tell
