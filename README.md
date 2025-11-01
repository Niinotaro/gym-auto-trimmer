# Gym Auto Trimmer (Non-AI PoC)

学習済みAIモデルを使わず、ROI内のフレーム差分ヒューリスティックで「活動区間（演技）」を抽出するPoCです。  
この段階では **実行確認・依存インストールは行いません**（ローカルでの確認は利用者が実施）。

## 仕組み（概要）
1. ROI でトリミングしたフレームの差分を二値化し、非ゼロ画素率をスコア化
2. スコアの移動平均 → しきい値でアクティブ/非アクティブを2値化
3. 近接区間の結合（gap≤0.8s）、短尺の抑制、前後余白（0.1s）付与
4. 必要に応じて FFmpeg で30fps CFRにて切り出し

## 想定依存（pyprojectに定義）
- opencv-python
- numpy
- pyyaml
- rich
- typer

## 使い方の例（**ここでは実行しない**）
```bash
# 依存導入と実行はローカルでユーザが行う
trim-gym --input path/to/video.mp4 --roi 200,120,140,120 --config configs/default_hbar.yaml --dry-run
trim-gym --input path/to/video.mp4 --roi 200,120,140,120 --write-clips --out-dir runs/demo
```

## 制限

* 照度変化・手ぶれに弱い場合があります（将来スタビライズ等で補強）
* このリポジトリはPoCの土台です。精度KPI・GUIは後続作業で追加

