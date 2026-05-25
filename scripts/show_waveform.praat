# show_waveform.praat — Sound を読み込み View & Edit で波形を表示
form: "波形を表示"
    sentence: "Sound file", ""
endform

if sound_file$ = ""
    exitScript: "音声ファイルが指定されていません。"
endif

sound = Read from file: sound_file$
selectObject: sound
View & Edit
