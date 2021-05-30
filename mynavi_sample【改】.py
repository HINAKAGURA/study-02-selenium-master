import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import datetime
import webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager


#driver自動更新
def setup_class(cls):
    cls.driver = webdriver_manager.Chrome(ChromeDriverManager().install())

# Chromeを起動する関数
def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）を設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。…ドライバーをうまく呼び出せないため、Cドライブ直下を指定
    # return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)
    return Chrome(executable_path="c:/" + driver_path, options=options)
# main処理


def main():
    try:# エラーを無視する【課題2-9】
        f = open("logfile.txt","w") # ログファイル【課題2-6】
        count = 1 # ログファイル用カウンター
        search_keyword =input("検索ワードを入力してください >>> ") # キーワード指定【課題2-4】
        f.write(datetime.datetime.now().strftime("%H:%M:%S") + " 処理開始 " + "検索ワードは「" + search_keyword +"」です\n")

        # driverを起動
        if os.name == 'nt': #Windows
            driver = set_driver("chromedriver.exe", False)
        elif os.name == 'posix': #Mac
            driver = set_driver("chromedriver", False)
        # Webサイトを開く
        driver.get("https://tenshoku.mynavi.jp/")
        time.sleep(5)
    
        try:
            # ポップアップを閉じる
            driver.execute_script('document.querySelector(".karte-close").click()')
            time.sleep(5)
            # ポップアップを閉じる
            driver.execute_script('document.querySelector(".karte-close").click()')
        except:
            pass
        
        # 検索窓に入力
        driver.find_element_by_class_name(
            "topSearch__text").send_keys(search_keyword)
        # 検索ボタンクリック
        driver.find_element_by_class_name("topSearch__button").click()
        exp_df = pd.DataFrame(index=[],columns=["社名","仕事詳細","情報更新日"])
        name_list = []
        info_list =[]
        data_list =[]
        f.write(datetime.datetime.now().strftime("%H:%M:%S") + " PandasのDataFrame作成しました\n")
        # 2ページ目以降を取得【課題2-3】
        while True:

            # ページ終了まで繰り返し取得
            _name = driver.find_elements_by_css_selector(".cassetteRecruit__name") # cssセレクタを使った指定に変更
            _info = driver.find_elements_by_css_selector(".cassetteRecruit__copy") # 項目2つ目 【課題2-2】
            _date = driver.find_elements_by_css_selector(".cassetteRecruit__updateDate") # 項目3つ目 【課題2-2】
            
            # 1ページ分繰り返し
            # print(len(_name))
            for (name , inf,d)in zip(_name,_info,_date):
                name_list.append(name.text) 
                info_list.append(inf.text)
                data_list.append(d.text.replace("情報更新日： ",""))   
                f.write(datetime.datetime.now().strftime("%H:%M:%S") + " " + str(count) +"件目出力しました\n")
                count = count + 1
            
            if len(driver.find_elements_by_class_name("iconFont--arrowLeft")) >0:# 次への矢印「>」がある限り繰り返し
                driver.find_element_by_class_name("iconFont--arrowLeft").click() 
            
            else:
                break

        exp_df["社名"] = name_list
        exp_df["仕事詳細"]=info_list
        exp_df["情報更新日"]=data_list

        #データをcsvファイルに出力 【課題2-5】
        exp_df.to_csv(f"kadai2_「{search_keyword}」.csv",encoding='utf-8-sig')
    except Exception as e:
        f.write(datetime.datetime.now().strftime("%H:%M:%S") + " " + e + "\n")
        pass
        


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
