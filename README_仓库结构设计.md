# 浠撳簱缁撴瀯璁捐

## 鐩爣

杩欎釜椤圭洰鏇撮€傚悎閲囩敤锛?
- 鏂囨湰鏁版嵁浣滀负鐪熸簮
- 鑴氭湰璐熻矗璁＄畻涓庡鍑?- Excel 鍙綔涓烘煡鐪嬪眰鍜屼汉宸ユ牎楠屽眰

## 鎺ㄨ崘鐩綍

```text
GCG/
鈹溾攢 data/
鈹? 鈹溾攢 cards/
鈹? 鈹? 鈹斺攢 cards.yaml
鈹? 鈹溾攢 value_tables/
鈹? 鈹? 鈹斺攢 value_table.yaml
鈹? 鈹溾攢 decks/
鈹? 鈹? 鈹溾攢 blue_purple_sample_50.txt
鈹? 鈹? 鈹斺攢 deck_meta.yaml
鈹? 鈹斺攢 scenarios/
鈹?    鈹斺攢 p22_blue_purple_sample.yaml
鈹溾攢 docs/
鈹? 鈹斺攢 鏁版嵁瀛楁璇存槑.md
鈹溾攢 schemas/
鈹? 鈹溾攢 cards.schema.yaml
鈹? 鈹溾攢 value_table.schema.yaml
鈹? 鈹溾攢 deck.schema.yaml
鈹? 鈹斺攢 p22_scenario.schema.yaml
鈹溾攢 output/
鈹溾攢 archive/
鈹溾攢 run_p22_greedy.py
鈹溾攢 export_cards_yaml.py
鈹斺攢 export_value_table_yaml.py
```

## 涓轰粈涔堜笉鐢?xlsx 浣滀负鐪熸簮

- `xlsx` 涓嶉€傚悎 git diff
- 瑙勫垯淇敼涓嶅鏄撳仛 review
- 鍐茬獊闅捐В鍐?- 瀹规槗鎶婃暟鎹€佸叕寮忋€佹牱寮忔贩鍦ㄤ竴璧?
## 鎺ㄨ崘鐨勭淮鎶ゆ柟寮?
### cards.yaml

瀛樺熀纭€鍗＄墝淇℃伅锛?
- 缂栧彿
- 鍗″悕
- 绫诲瀷
- LV / COST
- AP / HP
- traits
- resonance
- 鍘熷鏁堟灉鏂囨湰

### value_table.yaml

瀛樹环鍊艰〃瑙勫垯锛?
- 鏁堟灉鍚嶇О
- 鍙傛暟1 / 鍙傛暟2
- 鍚勮緭鍑虹淮搴?- 澶囨敞

### decks/*.txt

缁х画淇濈暀鐜╁瑙嗚鍙嬪ソ鐨?decklist 鏍煎紡锛?
```text
// Main Deck
4x ST01-005
4x ST05-004
```

### scenarios/*.yaml

瀛?P2-2 鐨勮繍琛屽弬鏁帮細

- 浣跨敤鍝鐗?- 璺戝灏戝洖鍚?- 鏉′欢榛樿姒傜巼
- 鏄惁绮剧‘澶勭悊鍏遍福

## 杈撳嚭灞?
鑴氭湰杈撳嚭缁熶竴鏀惧埌锛?
- `output/`

鏃?Excel 鍜屼腑闂村浠藉缓璁斁锛?
- `archive/`

骞堕€氳繃 `.gitignore` 蹇界暐銆?
## 褰撳墠寤鸿

褰撳墠鏈€鍚堢悊鐨勪富绾挎槸锛?
1. 缁х画鎶?Excel 閲岀殑瑙勫垯杩佺Щ鍒版枃鏈枃浠?2. 璁╄剼鏈紭鍏堣鍙栨枃鏈湡婧?3. Excel 鍙繚鐣欎负瀵煎嚭鍜屼汉宸ユ鏌ョ粨鏋?

