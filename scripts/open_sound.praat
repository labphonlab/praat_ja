# open_sound.praat — 引数で渡された音声ファイルを Objects ウィンドウに読み込む
form: "音声を開く"
    sentence: "Sound file", ""
endform

if sound_file$ = ""
    exitScript: "音声ファイルが指定されていません。"
endif

Read from file: sound_file$
