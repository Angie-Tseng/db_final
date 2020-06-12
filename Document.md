# DBMS Final Project - 借貸管理系統

###### tags: DBMS

## 1 目標
實作一個借貸管理系統，能對債權人與債務人資料、放款案件以及還款紀錄進行新增、查詢、修改或刪除，並能印出指定案件的明細以及每個月的還款明細。

## 2 Entities and Attributes
粗體字為 PR

#### CREDITOR 債權人
- **Number 編號(自動編號)**
- Name 姓名
- Tel 電話

#### DEBTOR 債務人
- **ID 身份證字號**
- Name 姓名
- CompanyName 公司名稱
- DateCreated 建檔日期
- Address 地址
    - ResidenceAddress 戶籍地址
    - MailingAddress 聯絡地址
- PhoneNumber 電話
    - Tel 市話
    - Mobile 手機
    - Company 公司

#### LOAN_PROJECT_TYPE 借貸案件類型
- **TypeNumber 案件類型編號(自動編號)**
- TypeName 類型名稱
- TotalPrinciple 放款金額
- InterestRate 月利率
- NumberOfPeriod 期數
- Remark 備註

#### LOAN_PROJECT 放款案件
- **ProjectNumber 案件編號(自動編號)**
- CreditorNumber 債權人編號
- DebterID 債務人身份證字號
- TypeNumber 方案種類編號
- StartDate 開始日
- OutstandingAmount 尚餘欠款

#### LOAN_PERIOD 還款紀錄
- **ProjectNumber 方案編號**
- **PeriodNumber 期數**
- DueDate 預計還款日期
- RepaymentDate 實際還款日期
- ExpectRepayment 預期還款
    - ExpectPrinciple 預期還款(本金)
    - ExpectInterest 實際還款(利息)
- GetRepayment 實際還款
    - GetPrinciple 實際還款(本金)
    - GetInterest 實際還款(利息)
- RepaymentMethod 還款方式
- Remark 備註

## 3 Relations
- Owe: 債務人對債權人有欠款的狀態。一位債務人可能同時向多位債權人借錢，一位債權人也可能同時借錢給多位債務人。
- ASSOCIATE_WITH: 一項貸款案件只會涉及一位債權人和一位債務人，但債權人和債務人可能涉及多項貸款案件。
- RELATE_TO: 一項貸款案件可能分好幾期，所以可能會包含多項還款紀錄。
- TYPE_OF: 一種貸款類型可能會有多項貸款案件。


## 4 ER Model
![](https://i.imgur.com/MOpn0HF.png)

## 5 Relational Schema
![](https://i.imgur.com/Ei5zMUr.png)

## 6 系統架構與環境
- Database: SQLite
- GUI: Python 3.7
    - Flask
    - numpy
- 執行
    - ```python main.py```
    - 在瀏覽器中打開```http://127.0.0.1:5000```

## 7 介面截圖與使用說明
- 管理債務人資料
    - 新增：將資料輸入到各個欄位當中，按下送出即可新增一筆資料。![](https://i.imgur.com/OJI07f9.png)


    - 修改：按下資料欄位右邊的修改按鈕，其對應的一筆資料即會顯示在對應的欄位，進行修改後按下送出即可。![](https://i.imgur.com/w1M1xCc.png)

    - 刪除：按下資料欄位右邊的刪除按鈕，即可刪除特定一筆資料。![](https://i.imgur.com/sbuasO3.png)


- 管理債權人資料
    - 新增：將資料輸入到各個欄位當中，按下送出即可新增一筆資料。![](https://i.imgur.com/o23oCUG.png)

    - 修改：按下資料欄位右邊的修改按鈕，其對應的一筆資料即會顯示在對應的欄位，進行修改後按下送出即可。![](https://i.imgur.com/ncVW1a4.png)

    - 刪除：按下資料欄位右邊的刪除按鈕，即可刪除特定一筆資料。![](https://i.imgur.com/7aYn3lX.png)

- 管理案件類型
    - 新增：將資料輸入到各個欄位當中，按下送出即可新增一筆資料。![](https://i.imgur.com/2kJZ8eH.png)

    - 修改：按下資料欄位右邊的修改按鈕，其對應的一筆資料即會顯示在對應的欄位，進行修改後按下送出即可。![](https://i.imgur.com/XzvVz1X.png)


    - 刪除：按下資料欄位右邊的刪除按鈕，即可刪除特定一筆資料。![](https://i.imgur.com/DyPvRwF.png)

- 管理放款案件
    - 新增：將資料輸入到各個欄位當中，按下送出即可新增一筆資料，同時會生成對應的還款紀錄。![](https://i.imgur.com/KY13gz3.png)

    - 刪除：按下資料欄位右邊的刪除按鈕，即可刪除特定一筆資料，同時會將對應的還款紀錄一併刪除。![](https://i.imgur.com/EasUa0M.png)

- 管理還款紀錄
    - 查詢案件編號：選擇欲查詢的案件編號，按下確認後，即可列出該案件編號的每期紀錄。![](https://i.imgur.com/TbVRvgI.png)

    - 修改：按下資料欄位右邊的修改按鈕，其對應的一筆資料即會顯示在對應的欄位，進行修改後按下送出即可。![](https://i.imgur.com/RVFWfNV.png)

- 查詢還款紀錄
    - 輸入欲查詢的債務人身分證字號，選擇「已結清」或「未結清」，按下確認後，即可列出該債務人截至今日為止的所有案件紀錄(包含已繳款總金額、剩餘繳款金額和當期已結清 (或未結清) 的詳細還款記錄)。![](https://i.imgur.com/kL9ZVvN.png)


- 查詢案件明細
    - 選擇欲查詢的案件編號，按下確認後，即可列出案件編號、開始日期、債務人的地址與電話，以及截至今日為止的繳款統計表。![](https://i.imgur.com/zWwi0n2.png)

- 使用SQL查詢
    - 輸入SQL指令，按下送出後即會顯示對應的查詢結果。![](https://i.imgur.com/bGIfrqA.png)

- 使用SQL新增、編輯、刪除資料
    - 輸入SQL指令，按下送出後即可完成新增、編輯、刪除資料。![](https://i.imgur.com/9a9E3Bj.png)
