import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import datetime
import webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager

LOG_FILE_PATH = "./log/log_{datetime}.log"
EXP_CSV_PATH = "./exp_list_{search_keyword}_{datetime}.csv"
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

# Chromeを起動する関数
def set_driver(headless_flg):
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

    # ChromeのWebDriverオブジェクトを作成する。DriverManagerでバージョンチェックをし、古ければ更新をし、さらにそのパスを返す
    return Chrome(ChromeDriverManager().install(), options=options)

# ログを出力する関数
def log(txt):
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logstr = '[%s: %s] %s' %('log', now, txt)
    with open (log_file_path, 'a' , encoding = 'utf-8_sig') as f:
        f.write(logstr + "\n")
    print(logstr)

# Table全体をリストとして取り込んだあと、必要な情報を取り出す関数
def find_table_target_word(th_elms, td_elms, target:str):
    for th_elm, td_elm in zip(th_elms,td_elms):
        if th_elm.text == target:
            return td_elm.text

# main処理
def main():
    search_keyword =input("検索ワードを入力してください >>> ") 

    log("処理開始")
    log("検索ワードは「{}」です".format(search_keyword))

    # driverを起動
    driver = set_driver(True)
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
    driver.find_element_by_class_name("topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()
    exp_name_list = []
    exp_info_list =[]
    exp_startingsalary_list =[]
    exp_data_list =[]
 
    count = 1 # ログファイル用カウンター
    success = 0 # 同上（成功件数）
    fail = 0 # 同上（失敗件数）

    while True:

        # ページ終了まで繰り返し取得
        name_list = driver.find_elements_by_css_selector(".cassetteRecruit__heading .cassetteRecruit__name")
        info_list = driver.find_elements_by_css_selector(".cassetteRecruit__heading .cassetteRecruit__copy") 
        startingsalary_list = driver.find_elements_by_css_selector(".cassetteRecruit .tableCondition") # 一旦、テーブルをまるごと取得・格納する
        data_list = driver.find_elements_by_css_selector(".cassetteRecruit__updateDate") 
        
        # 1ページ分繰り返し
        for (name , inf , salary , d)in zip(name_list, info_list, startingsalary_list,data_list):
            try:
                exp_name_list.append(name.text) 
                exp_info_list.append(inf.text)
                ss = find_table_target_word(salary.find_elements_by_tag_name("th"),salary.find_elements_by_tag_name("td"),"初年度年収")
                exp_startingsalary_list.append(ss)
                exp_data_list.append(d.text.replace("情報更新日： ",""))   
                log(f"{count}件目成功：{name.text}")
                success+=1
            except Exception as e:
                log(f"{count}件目失敗：{name.text}")
                log(e)
                fail+=1
            finally:
                count+=1
        # 次への矢印「>」がある限り繰り返し
        next_page = driver.find_elements_by_class_name("iconFont--arrowLeft")
        if len(next_page) >0:
            next_page_link = next_page[0].get_attribute("href")
            driver.get(next_page_link)        
        else:
            log("最終ページです。終了します。")
            break



    #データをcsvファイルに出力 
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    exp_df = pd.DataFrame({"企業名":exp_name_list,"情報":exp_info_list,"初任給":exp_startingsalary_list,"情報更新日":exp_data_list})
    exp_df.to_csv(EXP_CSV_PATH.format(search_keyword=search_keyword,datetime=now),encoding='utf-8-sig',index = False)
    log(f"処理完了　成功件数：{success}件、失敗件数{fail}件")

      


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
