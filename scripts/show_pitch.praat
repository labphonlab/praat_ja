# show_pitch.praat — Pitch を抽出して描画する
form: "ピッチを表示"
    sentence: "Sound file", ""
    positive: "Time step (s)", 0.01
    positive: "Pitch floor (Hz)", 75
    positive: "Pitch ceiling (Hz)", 600
endform

if sound_file$ = ""
    exitScript: "音声ファイルが指定されていません。"
endif

sound = Read from file: sound_file$
selectObject: sound
pitch = To Pitch: time_step, pitch_floor, pitch_ceiling

Erase all
selectObject: pitch
Draw: 0, 0, pitch_floor, pitch_ceiling, "yes"

selectObject: sound
plusObject: pitch
View & Edit
