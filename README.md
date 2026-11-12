# Xperia 1 VII / XQ-FS72 TWRP port

裝置目錄及編譯代號為 `pdx256`，Sony 平台名稱為 `shimanto`；本移植目前驗證的
實際型號仍為 XQ-FS72，改名不表示已驗證其他地區型號。

可重現建置用的移植原始碼與封裝流程。支援基準為 **XQ-FS72、71.2.A.2.35**，
使用 TWRP Android 14.1 分支與固定 commit。這不是 TeamWin 官方支援機型聲明。

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
尚未建立遠端網址，也沒有以假的 GitHub URL 填入 manifest。`patches/` 必須套用：只拉 device/vendor 加上
未修改的官方 TWRP，無法取得這個 Sony FBE／顯示／儲存與 USB 移植。

## 建置

使用 Linux／WSL2 的 Linux 檔案系統放 Android 原始碼與輸出；建議至少保留
150 GiB，實際用量依快取／平行度增加。主機需有 Android 14 建置工具鏈所需
套件，以及 `git`、`repo`、Python 3.10+、`lz4`、`openssl`、`binutils`。
本 repo 不需放在原始碼樹內。以下 `$PORT` 是此 repo 的絕對路徑，
`$SOURCE` 是乾淨的 TWRP 原始碼目錄；請自行指定磁碟位置。

```bash
export PORT=/path/to/xperia-recovery-port
export SOURCE=/path/to/twrp-source
mkdir -p "$SOURCE"
cd "$SOURCE"
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-14.1
cp "$PORT/manifests/default.xml" .repo/manifests/pdx256-pinned.xml
repo init -m pdx256-pinned.xml
repo sync -c -j8

python3 "$PORT/tools/extract.py" \
  --recovery /path/to/stock-recovery.img \
  --system-root /path/to/extracted-factory-root

bash "$PORT/build.sh" "$SOURCE" /path/to/output/recovery.img 8
```

上游建置說明：[TWRP minimal manifest](https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp)。
本專案使用固定版本 manifest，不能任意替換成其他分支。

取得本建置整合 repo 後，必須另外將兩個 tree 的 `twrp-14.1` 分支 clone 到
`$PORT/device/sony/pdx256` 與 `$PORT/vendor/sony/pdx256`。三者缺一不可。
本機 tree 的 Git metadata 不會被 `prepare.py` 複製到 Android 原始碼目錄。
遠端尚未建立；本機可用各 repo 的絕對路徑作為 `git clone -b twrp-14.1` 的來源。

`extract.py` 只需要符合雜湊的原廠 recovery 與系統相依檔案。
不需要 boot.img、kernel Image，也不需要讀取手機私人資料或圖形鎖。
檔案擷取來源的必要路徑列於 `vendor/sony/pdx256/proprietary-files.json`。

`prepare.py` 會核對 commit、補丁雜湊與套用狀態；遇到不同的 device tree 會停止，
不覆蓋使用者修改。`build.sh` 保留目前上游使用的
`ALLOW_MISSING_DEPENDENCIES=true`，因此不能只以編譯 exit code 判斷完整性。
封裝會另驗證所有指定 ramdisk 輸入、原廠 blob、CPIO、SELinux 與 AVB。

**最後可用輸出是傳給 `build.sh` 的 OUTPUT_IMG，並非 Android out 裡的原始
recovery.img。** 原始輸出還沒有 Sony 開機所需的完整 ramdisk／AVB 封裝。
腳本不會刷機，也不會改動 boot、init_boot 或槽位。

## 封裝原理

從使用者提供的 stock recovery 解出原廠 ramdisk，依明確配方加入當次建置的
TWRP／函式庫、原廠 runtime、文字設定與圖示。SELinux 從原廠 policy 解碼，
套用可審閱的 `add.cil`／`remove.cil` 再編譯；不靠歷次測試映像疊加。

Sony AVB descriptor 排序與版面保留，改以 AOSP 公開測試金鑰簽署，適用於
已解鎖 bootloader 的測試移植。此金鑰不是 Sony 金鑰，不代表能鎖回 bootloader。
最終映像不包含 kernel；目前仍使用原廠 kernel／vendor 相依。

建置設定使用 `TARGET_NO_KERNEL := true`；此 repo 不包含 kernel tree 或核心建置流程。

## 驗證範圍

參考實機版本已確認圖形解密與卸載後重新解密、繁中與時區設定保存、
內部儲存／microSD、壓縮備份、MTP／ADB 切換及 fastbootd 往返。
整機 Data 還原尚未實測，不能以備份成功代替還原成功。

repo 整理的離線驗證見 `VALIDATION.md`。本 repo 尚未完成另一台電腦從零
下載全部原始碼的完整建置驗收；不宣稱已驗證任意新環境。

## 授權與發佈

參閱 `NOTICE.md`。不要把忽略的原廠映像、runtime、私人日誌或手機備份加入 Git。
這份 repo 不含手機憑證，也不需要分享圖形／密碼。
