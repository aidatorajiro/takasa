# OpenStreetMap 高低差を考えた最短（？）経路問題ソルバー
![takasa wo kangaeru](takasa.png)

OpenStreetMapの地図データと国土地理院の標高データを組み合わせて、高低差が出来るだけ小さくなり、かつ経路も出来るだけ短くなるような経路をかんがえます。

## 実行方法

まず国土地理院のサイト<https://fgd.gsi.go.jp/download/menu.php>にいき、探索範囲の「数値標高モデル」をダウンロードしましょう。（要会員登録）

zipファイルを全て解凍し、ダウンロードした大量のxmlファイルを実行ディレクトリの`DL`下に配置します。

次に、`config.py`を作成し、以下のように目的地などの情報を設定します。

経路の探索は指定された緯度・経度からなる矩形の範囲内で行われます。緯度・経度は小数点表記で書いてください。

```python
pathbound_small = [探索範囲の最小緯度, 探索範囲の最小経度]
pathbound_large = [探索範囲の最大緯度, 探索範囲の最大経度]

pathstart_nodeid = 出発地のOpenStreetMap上のNode ID
pathend_nodeid = 目的地のOpenStreetMap上のNode ID
```

Node IDは<https://openstreetmap.org/>などで検索しましょう。

右クリックで「地物を検索(Query Features)」すると付近のNodeが出現します。

次に、以下の順でpythonファイルを実行します。

```bash
python mapdata.py
python elevation.py
python solve.py
```

経路のノードID一覧`nodeids.results`と、

それをOverpass APIが処理できるようにした`overpass_query.results`が生成されます。<https://overpass-turbo.eu/>に入力すると、マップと照らし合わせることができます。

## 仕様

てきとうに考えました。

1. scipyのshortest_path関数を使って解きます。
1. 一方通行などの区別はないです。つまり、shortest_path関数に渡す行列は対称行列です。
1. 道の長さと高低差をスコア化し、そのスコアの合計値が最小になるような経路を選びます。長さを正規化した値L、高低差を正規化した値E、Lを正規化した値の最小値Lm、Eを正規化した値の最小値Emがある時、スコアは`L+E-Lm-Em+0.2`で表されます。
