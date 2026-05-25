# show_formant.praat — Formant を抽出して描画する
form: "フォルマントを表示"
    sentence: "Sound file", ""
    positive: "Time step (s)", 0.01
    positive: "Max number of formants", 5
    positive: "Maximum formant (Hz)", 5500
    positive: "Window length (s)", 0.025
    real: "Pre-emphasis from (Hz)", 50
endform

if sound_file$ = ""
    exitScript: "音声ファイルが指定されていません。"
endif

sound = Read from file: sound_file$
selectObject: sound
formant = To Formant (burg): time_step, max_number_of_formants, maximum_formant, window_length, pre_emphasis_from

Erase all
selectObject: formant
Speckle: 0, 0, maximum_formant, 30, "yes"

selectObject: sound
plusObject: formant
View & Edit
