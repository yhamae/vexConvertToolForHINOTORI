# vex_to_device.pyの使い方
###### Made by [Yuki Hamae](mailto:github@hamae.net)@[Kagoshima Univ.](http://milkyway.sci.kagoshima-u.ac.jp/~imai/lab/)  
vexファイルを.startへ変換するプログラムは[こちら](https://github.com/TakeruKawaguchi/vex_to_start)

## 基本的な使い方
このプログラムはPython3で書かれています。したがって実際に実行する際は、コマンドライン上で、  
```
Python3 vex_concerter.py [オプション]
```
と実行する。  
オプションのところに`-h`とすると使い方を見ることが出来る。  

### オプションについて  
オプションを設定すると、特定の機能だけを実行することが出来る。例えば、.startファイルのみを作りたい場合は、`[オプション]`のところに`-s`を加えればいい。各機能とオプションで指定する際のキーワードは以下の通りである。  

|作りたいファイル|オプションで指定すべきキーワード|
|-------------|--------------------------|
|.start       | `-s`                     |
|.ndevice     | `-n`                     |
|.dat         | `-d`                     |
|.tune        | `-t`                     |

これらのキーワードは複数同時に使うこともでき、例えば.startと.deviceを同時に変換したい場合は次のようにする。  
```
Python3 vex_concerter.py -s -n
```
また、.start、.device、.dat、.tuneすべてのファイルの変換を行いたい場合は、  
```
Python3 vex_concerter.py
```
といったように、オプションに何も指定する必用がない。  
デフォルトでは`parameter.inp`というパラメータファイルを読み込むが、パラメータファイルを指定したい場合は`-f`を使う。`Python3 vex_concerter.py -f パラメータファイルの名前`といった用パラメータファイルの名前を指定して使うことが出来る。  
プログラムを実行した後、もしパラメータファイルで指定した各指示書の名前のファイルが既に存在する場合、上書きするか別の名前で保存するか聞かれる。ここで`y`を押した場合は上書きされ、`n`を押した場合は保存するファイル名を聞かれるので入力する必要がある。もしこの機能を無効化したい場合は、パラメータファイルの中に`ask_verwrite = False`と記述する。

## 各変換実行時に必用なファイル  
vexファイルから変換する際に、.start、.device、.datについては、vexファイルを元に変換を行うので、本プログラムを構成しているモジュールとvexファイル、パラメータファイルがあればいい。しかし、.tuneについては、他のものと違い、vexファイルを読み込まずに.startを読み込むので、vexファイルの代わりに.startを用意する必要がある。ただし、.start、.device、.dat、.tuneすべてのファイルの変換を行う場合は、初めに.startが作製される使用になっているので、.startを別に用意しておく必用はない。  

## パラメータファイルの書き方  
パラメータファイルの名前は拡張子も含めて何でもいいが、parameter.inp以外の名前の場合、プログラムを実行する際に指定する必要がある。  
また、パラｰメータファイルを書く際には基本的には以下の法則に従う。  
```
[指定したいパラメータの名前] = [指定したいパラメータの値]
```
***パラメータファイル内でのパラメータの指定に関する文法は、Pythonでの書き方に従っている。*** 以下にその具体的な例を挙げる。  
- 'vex_file_name'というパラメータを'sample.vex'に設定する場合  
  ```
  vex_file_name = 'sample.vex'
  ```
- 'TIME_MOVE_ANTENNA'というパラメータを1200に設定する場合  
  ```
  TIME_MOVE_ANTENNA = 1200
  ```
- 'start_time_flag'というパラメータをTrueに設定する場合  
  ```
  start_file_flag = True
  ```
なお、パラメータファイルはPythonスクリプトとして読み込まれるので、以下のような設定方法もある。
- IFFREQというパラメータを'6,6,6,6,6,6,6,6'に設定する場合
  ```
  IFFREQ = [6] * 8
  ```
  または
  ```
  for i in range(0, 8):
    IFFREQ[i] = 6
  ```

## 設定可能なパラメータ  
### 必ず設定しなくてはならないパラメータ  
|パラメータ名          |説明 |Note |
|--------------------|----|-----|
|USER_NAME           |USER_NAMEを変更する | |
|vex_file_nam        |vexファイルの名前を指定する | |
|start_time_flag     |観測開始時間を指定する |※a |
|TIME_MOVE_ANTENNA   |1SCAN目にアンテナを動かす時間 | |
|after_mmc           |MMCの一連の流れの後に何秒待つか決める | |
|before_observation  |観測を何秒前から行うかを決める | |
|time_of_second_move |2SCAN目にアンテナを動かす時間 | |
|error_flag          |エラーが起きたときの処理 | |

※a:start_time_flagについて  
    .vexファイルに従う場合は`start_time_flag = 'original_start'`。任意の時間で観測を開始する場合は`start_time_flag = 'any_start'`とし、`any_time = '2018y075d08h00m00s'`というように時間を指定する。現時刻から指定の時間後に観測する場合は、`start_time_flag = 'after_start'`とし、`after_day = 0`、`after_hour = 0`、`after_minute = 0`といったようにパラメータを設定する。

### 設定必須ではないパラメータ  
| パラメータ名      |説明 |デフォルト値 |Note |
|-----------------|-----|------------|---|
|USER_NAME        | USER_NAMEを変更する|None |  |
|station_name     |アンテナの名前を指定する |'Ny' | |
|start_file_flag  | startファイルの名前の付け方|'file_selected' | |
|start_file_name  |startファイルの名前 |vexファイルと同じ | |
|device_fname     |deviceファイルの名前 |vexファイルと同じ| |
|device_file_flag |deviceファイルを書き出すかどうか|True||
|SAM_Att          |SAM45での各アレイのAttの値|すべて5||
|dat_filename     |datファイルの名前|vexファイルと同じ||
|dat_file_flag    |datファイルを書き出すかどうか|True||
|tune_file_name   |tuneファイルの名前|vexファイルと同じ||
|tune_file_flag   |tuneファイルを書き出すかどうか|True||
**: `start_file_flag`について  
    `start_file_flag`を`file_selected`にした場合は`start_file_name`で書き出すファイル名を指定する必要がある。






