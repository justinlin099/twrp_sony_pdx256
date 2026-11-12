# Xperia 1 VII TWRP 建置指南

XQ-FS72（pdx256）／韌體 71.2.A.2.35／TWRP 3.7.1_14。

## 1. 準備環境

使用 Ubuntu 22.04 或 WSL2 Ubuntu 22.04，預留至少 150 GiB。
原始碼與輸出目錄放在 Linux 檔案系統，例如 ext4。

```bash
sudo apt-get update
sudo apt-get install -y git curl python3 gh

gh auth login
gh auth setup-git
```

登入的 GitHub 帳號需要能讀取本 repo 與 device、vendor 兩個私人倉庫。

## 2. 下載裝置與建置檔案

將 `/path/to/build` 改成你的建置位置。以下指令在同一個終端執行。

```bash
export BUILD_ROOT=/path/to/build
export PORT="$BUILD_ROOT/pdx256-port"
export SOURCE="$BUILD_ROOT/twrp-source"
export OUTPUT="$BUILD_ROOT/artifacts/recovery.img"

mkdir -p "$BUILD_ROOT"
git clone -b twrp-14.1 https://github.com/justinlin099/twrp_sony_pdx256.git "$PORT"
python3 "$PORT/tools/checkout-trees.py"
sudo bash "$PORT/tools/install-build-deps.sh"
```

`checkout-trees.py` 會下載固定版本的 device 與 vendor tree；所需原廠相依檔已包含在 vendor tree。

## 3. 安裝 repo 工具

```bash
mkdir -p "$HOME/.local/bin"
curl -fL https://storage.googleapis.com/git-repo-downloads/repo -o "$HOME/.local/bin/repo"
chmod +x "$HOME/.local/bin/repo"
export PATH="$HOME/.local/bin:$PATH"
```

## 4. 下載 TWRP 原始碼

```bash
mkdir -p "$SOURCE"
cd "$SOURCE"
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git \
  -b twrp-14.1 --depth=1 --no-clone-bundle
cp "$PORT/manifests/default.xml" .repo/manifests/pdx256-pinned.xml
repo init -m pdx256-pinned.xml --no-clone-bundle
repo sync -c -j8 --no-clone-bundle
```

## 5. 編譯

```bash
bash "$PORT/build.sh" "$SOURCE" "$OUTPUT" 8
```

最後的 `8` 是平行編譯數，可依電腦資源調整。腳本會自動套用補丁、編譯與封裝。

## 輸出

- `$BUILD_ROOT/artifacts/recovery.img`：完成封裝的 recovery 映像。
- `$BUILD_ROOT/artifacts/recovery.json`：映像 SHA-256 與封裝驗證結果。

刷入時使用上述 `artifacts/recovery.img`；`twrp-source/out` 裡的 `recovery.img` 是尚未完成封裝的中間產物。

再次編譯時指定新的輸出檔名，工具不會覆寫已存在的映像：

```bash
bash "$PORT/build.sh" "$SOURCE" "$BUILD_ROOT/artifacts/recovery-v2.img" 8
```
