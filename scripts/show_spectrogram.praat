# show_spectrogram.praat — Spectrogram を生成し描画する
form: "スペクトログラムを表示"
    sentence: "Sound file", ""
    positive: "Window length (s)", 0.005
    positive: "Maximum frequency (Hz)", 5000
endform

if sound_file$ = ""
    exitScript: "音声ファイルが指定されていません。"
endif

sound = Read from file: sound_file$
selectObject: sound
spec = To Spectrogram: window_length, maximum_frequency, 0.002, 20, "Gaussian"

Erase all
selectObject: spec
Paint: 0, 0, 0, 0, 100, "yes", 50, 6, 0, "yes"

selectObject: sound
View & Edit
