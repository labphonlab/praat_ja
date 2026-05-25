# create_textgrid.praat — Sound と同名の TextGrid を作成し View & Edit で開く
form: "TextGrid を作成"
    sentence: "Sound file", ""
    sentence: "Tier names", "phones words"
    sentence: "Point tier names", ""
endform

if sound_file$ = ""
    exitScript: "音声ファイルが指定されていません。"
endif

sound = Read from file: sound_file$
selectObject: sound
tg = To TextGrid: tier_names$, point_tier_names$

selectObject: sound
plusObject: tg
View & Edit

# 同名で TextGrid を保存
path$ = sound_file$
# 拡張子を ".TextGrid" に置換
if endsWith(path$, ".wav") or endsWith(path$, ".WAV")
    out$ = left$(path$, length(path$) - 4) + ".TextGrid"
elif endsWith(path$, ".mp3") or endsWith(path$, ".MP3")
    out$ = left$(path$, length(path$) - 4) + ".TextGrid"
elif endsWith(path$, ".flac") or endsWith(path$, ".FLAC")
    out$ = left$(path$, length(path$) - 5) + ".TextGrid"
else
    out$ = path$ + ".TextGrid"
endif

selectObject: tg
Save as text file: out$
