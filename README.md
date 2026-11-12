# Xperia 1 VII / XQ-FS72 TWRP port

裝置目錄及編譯代號為 `pdx256`，Sony 平台名稱為 `shimanto`；本移植目前驗證的
實際型號仍為 XQ-FS72，改名不表示已驗證其他地區型號。

可重現建置用的移植原始碼與封裝流程。支援基準為 **XQ-FS72、71.2.A.2.35**，
TWRP 原始碼主版本為 **3.7.1_14**，使用固定 commit。這不是 TeamWin 官方支援機型聲明。

## 版本與分支

- 本專案三個 repo 的分支：`twrp-14.1`。
- 上游 manifest 分支：`twrp-14.1`，用於下方 `repo init` 指令。
- 上游 recovery 原始碼分支：`android-14.1`。
- 固定 recovery commit：`426b747737e7ce9e9e17da5b4d2ba883f296aec7`；
  其 `variables.h` 定義 `TW_MAIN_VERSION_STR` 為 `3.7.1_14`。

上游分支名稱不是 TWRP 發行版本號，也不是手機目前的 Android 版本。
`3.7.1_14` 是此 commit 的主版本字串，不代表本移植是官方發行映像；
實際原始碼版本仍以 manifest 固定的 commit 為準。

## 結構

```text
device/sony/pdx256/   BoardConfig、產品設定、ramdisk overlay、SELinux 差異
vendor/sony/pdx256/   原廠相依檔案清單、版本與 SHA-256、離線擷取結果
patches/              TWRP、vold、ADB 的最終原始碼差異與固定 base commit
manifests/default.xml 所有上游專案固定版本
tools/                擷取、套用補丁、封裝與驗證工具
build.sh              編譯並輸出可刷寫的 Sony recovery
```

目前拆成建置整合、device、vendor 三個獨立 Git repo，分支皆為 `twrp-14.1`。
device/vendor repo 在上述路徑中獨立管理，由外層 repo 忽略，不是 submodule。
三個 GitHub 倉庫目前均為私人：

- 建置整合：<https://github.com/justinlin099/twrp_sony_pdx256>
- Device：<https://github.com/justinlin099/android_device_sony_pdx256>
- Vendor：<https://github.com/justinlin099/android_vendor_sony_pdx256>

`trees.lock.json` 固定兩個 companion tree 的 commit。`patches/` 必須套用：只拉 device/vendor 加上
未修改的官方 TWRP，無法取得這個 Sony FBE／顯示／儲存與 USB 移植。

## 建置

使用 Linux／WSL2 的 Linux 檔案系統放 Android 原始碼與輸出；建議至少保留
150 GiB，實際用量依快取／平行度增加。建議使用獨立 Ubuntu 22.04 環境；
在該環境內以 root 執行 `bash tools/install-build-deps.sh` 安裝相依套件，
並安裝 [Google repo launcher](https://gerrit.googlesource.com/git-repo/+/refs/heads/main/README.md)。
主機需有 Android 14 建置工具鏈所需
套件，以及 `git`、`repo`、Python 3.10+、`lz4`、`openssl`、`binutils`。
本 repo 不需放在原始碼樹內。以下 `$PORT` 是此 repo 的絕對路徑，
`$SOURCE` 是乾淨的 TWRP 原始碼目錄；請自行指定磁碟位置。

```bash
export PORT=/path/to/xperia-recovery-port
export SOURCE=/path/to/twrp-source
git clone -b twrp-14.1 https://github.com/justinlin099/twrp_sony_pdx256.git "$PORT"
python3 "$PORT/tools/checkout-trees.py"
mkdir -p "$SOURCE"
cd "$SOURCE"
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-14.1
cp "$PORT/manifests/default.xml" .repo/manifests/pdx256-pinned.xml
repo init -m pdx256-pinned.xml
repo sync -c -j8

bash "$PORT/build.sh" "$SOURCE" /path/to/output/recovery.img 8
```

上游建置說明：[TWRP minimal manifest](https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp)。
本專案使用固定版本 manifest，不能任意替換成其他分支。

私人倉庫需先設定 GitHub Git 認證，例如 `gh auth login`、`gh auth setup-git`；
不要把 token 寫進 URL、腳本或 manifest。`checkout-trees.py` 會將兩個 tree
下載到 `$PORT/device/sony/pdx256` 與 `$PORT/vendor/sony/pdx256`，並 checkout
鎖定的 commit。三者缺一不可；現有 checkout 若版本不符或有修改，腳本會停止。
本機 tree 的 Git metadata 不會被 `prepare.py` 複製到 Android 原始碼目錄。

私人 vendor repo 已收錄 7 個原廠 runtime，以及逐檔拆出的 recovery 相依檔。
`build.sh` 自動呼叫 `prepare-factory.py` 核對所有 SHA-256；不必另行
從手機或韌體匯入檔案，也不需要完整或壓縮的原廠 recovery 映像。
不需要 boot.img、kernel Image，也不需要讀取手機私人資料或圖形鎖。
`extract.py` 保留給維護者匯入同版本的原廠檔案；來源路徑與雜湊列於
`vendor/sony/pdx256/proprietary-files.json`。

`prepare.py` 會核對 commit、補丁雜湊與套用狀態；遇到不同的 device tree 會停止，
不覆蓋使用者修改。`build.sh` 保留目前上游使用的
`ALLOW_MISSING_DEPENDENCIES=true`，因此不能只以編譯 exit code 判斷完整性。
封裝會另驗證所有指定 ramdisk 輸入、原廠 blob、CPIO、SELinux 與 AVB。

**最後可用輸出是傳給 `build.sh` 的 OUTPUT_IMG，並非 Android out 裡的原始
recovery.img。** 原始輸出還沒有 Sony 開機所需的完整 ramdisk／AVB 封裝。
腳本不會刷機，也不會改動 boot、init_boot 或槽位。

## 封裝原理

依明確配方組合 vendor tree 內逐檔保存的相依內容、當次建置的
TWRP／函式庫、文字設定與圖示。SELinux 從 vendor tree 的原廠 policy 解碼，
套用可審閱的 `add.cil`／`remove.cil` 再編譯；不靠歷次測試映像疊加。

映像由上游 `mkbootimg` 產生，AVB 由未修改的上游 `avbtool` 依
`device/sony/pdx256/image-config.json` 設定產生，不再自行重寫 AVB 二進位欄位。
使用 AOSP 公開測試金鑰簽署，適用於
已解鎖 bootloader 的測試移植。此金鑰不是 Sony 金鑰，不代表能鎖回 bootloader。
最終映像不包含 kernel；目前仍使用原廠 kernel／vendor 相依。

建置設定使用 `TARGET_NO_KERNEL := true`；此 repo 不包含 kernel tree 或核心建置流程。
精簡檢查、已移除的重複流程與仍需保留的移植部分見 `ARCHITECTURE.md`。

## 驗證範圍

參考實機版本已確認圖形解密與卸載後重新解密、繁中與時區設定保存、
內部儲存／microSD、壓縮備份、MTP／ADB 切換及 fastbootd 往返。
整機 Data 還原尚未實測，不能以備份成功代替還原成功。

repo 整理的離線驗證見 `VALIDATION.md`。本 repo 尚未完成另一台電腦從零
下載全部原始碼的完整建置驗收；不宣稱已驗證任意新環境。

## 授權與發佈

參閱 `NOTICE.md`。vendor repo 僅收錄版本清單指定的原廠相依檔；不要加入
私人日誌、手機備份或無關韌體。原廠檔案維持各自原有授權，並未重新授權。
這份 repo 不含手機憑證，也不需要分享圖形／密碼。
目前圖示使用向量機身、第三方 SONY／XPERIA 字標及實機 TWRP 首頁截圖。
16／24／32／48 px 顯示背面上半部，64／96／128／256 px 顯示正背面。
舊 commit 仍有照片圖示；私人上傳不等於已完成公開發佈的素材授權整理。
