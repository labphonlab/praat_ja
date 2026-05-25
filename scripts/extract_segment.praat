# extract_segment.praat — 指定区間（秒）の Sound を切り出して保存する
form: "区間を抽出"
    sentence: "Sound file", ""
    real: "Start time (s)", 0.0
    real: "End time (s)", 1.0
    sentence: "Output file", ""
endform

if sound_file$ = ""
    exitScript: "音声ファイルが指定されていません。"
endif

if end_time <= start_time
    exitScript: "終了時刻は開始時刻より大きい値を指定してください。"
endif

sound = Read from file: sound_file$
selectObject: sound
part = Extract part: start_time, end_time, "rectangular", 1.0, "no"

if output_file$ = ""
    # 入力ファイル名に "_segment.wav" を付加して保存
    if endsWith(sound_file$, ".wav") or endsWith(sound_file$, ".WAV")
        out$ = left$(sound_file$, length(sound_file$) - 4) + "_segment.wav"
    else
        out$ = sound_file$ + "_segment.wav"
    endif
else
    out$ = output_file$
endif

selectObject: part
Save as WAV file: out$
View & Edit
