# 機場接送預約單：LINE MINI App 上線步驟

客人在 LINE 裡打開預約單，填完按「送出預約給客服」，預約內容會直接傳到你的官方帳號聊天室，不用複製貼上。
在一般瀏覽器打開時，會自動改回「複製預約內容」的方式。

## 資料夾內容

| 檔案 | 用途 |
|---|---|
| `index.html` | 預約單頁面（LIFF ID 填在檔案最上方） |
| `flights.json` | 桃園機場班表，供頁面查航班 |
| `update_flights.py` | 更新班表的程式 |
| `.github/workflows/update-flights.yml` | 每天自動執行更新（台灣時間 02:00、10:00、18:00） |

## 步驟一：放上網路（GitHub Pages，免費）

LINE 規定 MINI App 必須是 `https://` 網址，GitHub Pages 免費提供，也能每天自動更新班表。

1. 到 <https://github.com> 註冊帳號（已有可略過）。
2. 右上角 **＋ → New repository**，名稱例如 `airport-booking`，選 **Public**，按 **Create repository**。
3. 在新 repo 頁面點 **uploading an existing file**，把這個資料夾裡的所有檔案拖進去，按 **Commit changes**。
   - `.github` 是隱藏資料夾，Mac 在 Finder 按 `⌘ + Shift + .` 才看得到，記得一起拖進去。
4. **Settings → Pages**：Source 選 **Deploy from a branch**，Branch 選 `main`、`/ (root)`，按 **Save**。
5. 約 1 分鐘後，網址會是 `https://你的帳號.github.io/airport-booking/`，先用手機打開確認頁面正常。
6. **Settings → Actions → General**：最下面 Workflow permissions 選 **Read and write permissions**，按 **Save**（讓每日更新可以存檔）。
7. **Actions** 分頁 → 左邊 **Update flights** → **Run workflow**，手動跑一次確認沒有錯誤。

## 步驟二：在 LINE Developers 建立 MINI App

以下依 LINE Developers 後台的名稱說明，實際畫面若有調整，以後台為準。

1. 到 <https://developers.line.biz/console/> 用你的 LINE 帳號登入。
2. 選擇（或建立）你的 **Provider**。官方帳號所在的 Provider 最好用同一個。
3. **Create a new channel → LINE MINI App**，填寫名稱「機場接送預約」、說明、圖示等資料後建立。
4. 進入該 channel 的 **Web app settings**（或 **LIFF** 分頁）：
   - **Endpoint URL**：填步驟一第 5 點的網址。
   - **Scopes**：勾選 `profile` 和 `chat_message.write`（送出訊息需要這個）。
5. 複製頁面上的 **LIFF ID**（格式像 `2001234567-AbCdEfGh`）。
6. 回到 GitHub，打開 `index.html` → 右上鉛筆圖示編輯，找到這一行：
   ```js
   window.LIFF_ID = '';
   ```
   把 LIFF ID 貼進引號裡，按 **Commit changes**。

> 還沒送審的 MINI App 一樣可以用連結打開，只是不會出現在 LINE 的搜尋結果中。若想要「認證 MINI App」標章，再依後台指示送審即可。

## 步驟三：放進官方帳號

MINI App 的網址是 `https://miniapp.line.me/你的LIFF ID`。

到 **LINE Official Account Manager**：
- **圖文選單**：新增一格「線上預約」，動作選「連結」，貼上網址。
- **自動回應**：關鍵字「預約」時回覆這個網址。

客人從官方帳號聊天室打開時，按「送出預約給客服」，訊息會以客人的名義傳進聊天室，客服在後台直接看到。

## 常見問題

- **按送出後沒反應，改成複製？** 代表不是從聊天室打開（例如從瀏覽器或其他聊天室），或 `chat_message.write` 沒勾。這時頁面會自動改用複製，客人仍可貼上傳送。
- **聯絡人自動帶入了 LINE 暱稱？** 這是為了方便，客人可以直接改成真實姓名。
- **查不到航班？** 目前只支援桃園機場。松山、高雄的航班請客人手動填寫。
- **班表要多久才完整？** 機場一次只公開三天的資料，每日更新累積約一週後，七天的班表都會有。
