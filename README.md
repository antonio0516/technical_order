## 初始化專案

- 下面流程只有第一次起專案要跑，如果有設定好開機自動開啟 Docker desktop，那之後不用再跑這流程

1. 先取得給 MongoDB replica set 使用的 keyfile
    - 這裡權限設置非常重要，一定要確認專案的這個檔案權限是不是符合下面的設置
        - 使用者和群組是 999，而且是 rw-------
    -   ```bash
        cd Technical-Order-Editor
        openssl rand -base64 128 > mongodb-keyfile
        sudo chmod 600 mongodb-keyfile
        sudo chown 999:999 mongodb-keyfile
        ```
    - wsl 的使用者要先去 /etc/wsl.conf 裡面加入
        ```bash
        [automount]
        options = "metadata"
        ```
    - 然後需要在 cmd 裡面執行
        ```bash
        wsl --shutdown
        ```

1. 開啟專案
    ```bash
    docker compose up -d
    ```

2. 注意，以下步驟只有在專案沒有 `mongo_db` 這個資料夾的情況下才要跑
    - 這個資料夾裝著 MongoDB 的資料，這些設定也包括在內

2. 進去 MongoDB 的 container
    ```bash
    docker exec -it <id> bash
    ```
    - `docker ps` 可以查不同 container 的 id
    - 也可以用 docker desktop 開 container 的 terminal

3. 登入帳號
    ```bash
    mongo -u account -p password --authenticationDatabase admin
    ```

3. 設置成 replica set
    ```bash
    rs.initiate(
        {
            _id: "rs0",
            members: [
                { _id: 0, host: "localhost:27017" }
            ]
        }
    )
    ```

### 設置 MongoDB host
1. 注意，以下步驟只有在專案沒有 `mongo_db` 這個資料夾的情況下才要跑
    - 這個資料夾裝著 MongoDB 的資料，這些設定也包括在內
1. 進入 MongoDB container
    ```bash
    docker exec -it <id> bash
    ```

2. 進入 MongoDB
    ```bash
    mongo -u account -p password --authenticationDatabase admin
    ```

3. 設置 MongoDB host
    ```bash
    var cfg = rs.conf();
    cfg.members[0].host = "10.5.0.4:27017";
    rs.reconfig(cfg, {force: true});
    ```
    - 設置成 docker network 的 ip 才可以讓其他 container 連到，但會讓 host 連不到

## 前端開發
1. 安裝套件
    ```bash
    cd frontend
    npm install
    ```
3. 開發
    ```bash
    npm run dev
    ```

## 前端 build
1. 安裝依賴套件
    ```bash
    cd frontend
    npm install
    ```
1. 執行 build 指令
    -   ```bash
        npm run build
        ```
        - 要用管理員模式執行 cmd
2. 去 release 資料夾會有 build 好的專案檔，執行裡面的 exe 檔即可安裝應用程式