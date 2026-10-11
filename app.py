import streamlit as st
import pandas as pd
import google.generativeai as genai

# ========== 1. アプリの基本設定 ==========
st.set_page_config(page_title="保管場所検索アプリ", layout="wide")
st.title("📦 資材・保管場所検索アプリ (AI搭載✨)")
st.write("資材の名前や、使用用途（例：掃除道具、ゴキブリ対策）を入力してください。AIが推測して探します！")

# ========== 2. データの読み込み ==========
@st.cache_data
def load_data():
    # 同じフォルダにある inventory_data.csv を読み込む
    return pd.read_csv("inventory_data.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("エラー：'inventory_data.csv' というファイルが見つかりません。")
    st.stop()

# ========== 3. AI（Gemini）の準備 ==========
try:
    # 金庫(Secrets)からAPIキーを取り出して設定する
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # ★ここを修正しました！最新のモデル「gemini-3-flash-preview」を使います
    model = genai.GenerativeModel("gemini-3-flash-preview")
except KeyError:
    st.error("AIの準備ができていません。Streamlitの設定画面(Secrets)に GEMINI_API_KEY を登録してください。")
    st.stop()

# ========== 4. 検索窓と検索機能 ==========
search_word = st.text_input("🔍 検索キーワード（例：雑巾、掃除道具、段ボール）")

if search_word:
    st.markdown("### 🤖 AIが資材を探しています...")
    
    # スプレッドシートにある資材の名前を全部集めて1つの文章にする
    item_list = df["資材名"].astype(str).tolist()
    item_list_str = "、".join(item_list)
    
    # AIへのお願い（プロンプト）を作る
    prompt = f"""
    あなたは優秀な倉庫管理者です。以下の「資材リスト」の中から、「{search_word}」という用途やキーワードに関連する資材をすべて選んでください。
    （例：「ゴキブリ対策」なら「アースレッド」などを選ぶ）
    
    選んだ資材の名前だけをカンマ（,）区切りで出力してください。それ以外の説明は絶対に書かないでください。
    もし関連する資材が1つもない場合は「なし」とだけ出力してください。
    
    【資材リスト】
    {item_list_str}
    """
    
    # AIに考えてもらう
    try:
        response = model.generate_content(prompt)
        ai_answer = response.text.strip()
        
        if ai_answer == "なし" or ai_answer == "":
             st.warning(f"「{search_word}」に関連する資材は見つかりませんでした。")
        else:
             # AIが見つけた資材名のリストを作る
             found_items = [item.strip() for item in ai_answer.split(",")]
             
             # 見つかった資材だけを表に残す
             result_df = df[df["資材名"].isin(found_items)]
             
             if len(result_df) > 0:
                 st.success(f"AIが見つけた関連資材: {ai_answer}")
                 st.markdown("### 📋 検索結果")
                 st.dataframe(result_df, use_container_width=True, hide_index=True)
                 
                 st.markdown("### 🗺️ マップ")
                 try:
                     st.image("map_image.png", caption="図面上の番号と照らし合わせてください")
                 except FileNotFoundError:
                     st.info("※ここに図面の画像が表示されます。")
             else:
                 st.warning(f"「{search_word}」に関連する資材は見つかりませんでした。")
                 
    except Exception as e:
        st.error(f"AIの検索中にエラーが発生しました。設定を確認してください。（エラー内容: {e}）")
        
else:
    st.markdown("### 📋 全データ一覧")
    st.dataframe(df, use_container_width=True, hide_index=True)
