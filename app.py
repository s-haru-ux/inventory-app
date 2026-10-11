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
    model = genai.GenerativeModel("gemini-3-flash-preview")
except KeyError:
    st.error("AIの準備ができていません。Streamlitの設定画面(Secrets)に GEMINI_API_KEY を登録してください。")
    st.stop()


# ========== 4. 検索窓と検索機能 ==========
search_word = st.text_input("🔍 検索キーワード（例：雑巾、掃除道具、段ボール）")

if search_word:
    # 【節約術💡】まずはAIを使わずに、入力された文字が資材名にあるか普通に探す
    normal_result_df = df[df["資材名"].astype(str).str.contains(search_word, na=False)]
    
    # 普通の検索で見つかった場合は、AIを使わない（API消費ゼロ！）
    if len(normal_result_df) > 0:
        result_df = normal_result_df
    
    # 普通の検索で見つからなかった場合のみ、AIに推測してもらう
    else:
        # スプレッドシートにある資材の名前を全部集めて1つの文章にする
        item_list = df["資材名"].astype(str).tolist()
        item_list_str = "、".join(item_list)
        
        prompt = f"""
        あなたは優秀な倉庫管理者です。以下の「資材リスト」の中から、「{search_word}」という用途やキーワードに関連する資材をすべて選んでください。
        （例：「ゴキブリ対策」なら「アースレッド」などを選ぶ）
        
        選んだ資材の名前だけをカンマ（,）区切りで出力してください。それ以外の説明は絶対に書かないでください。
        もし関連する資材が1つもない場合は「なし」とだけ出力してください。
        
        【資材リスト】
        {item_list_str}
        """
        
        try:
            with st.spinner("🤖 AIが関連する資材を推測しています..."):
                response = model.generate_content(prompt)
                ai_answer = response.text.strip()
            
            if ai_answer == "なし" or ai_answer == "":
                result_df = pd.DataFrame() # 空っぽの表にする
            else:
                found_items = [item.strip() for item in ai_answer.split(",")]
                result_df = df[df["資材名"].isin(found_items)]
                
        except Exception as e:
            st.error(f"AIの検索中にエラーが発生しました。（エラー内容: {e}）")
            result_df = pd.DataFrame()

    # --- 検索結果の画面表示 ---
    if len(result_df) > 0:
        # 画面を「左:6」と「右:4」に分割
        col1, col2 = st.columns([6, 4])
        
        with col1:
            st.markdown("### 📋 検索結果")
            st.dataframe(result_df, use_container_width=True, hide_index=True)
            
        with col2:
            st.markdown("### 🗺️ マップ")
            try:
                st.image("map_image.png", caption="図面上の番号と照らし合わせてください")
            except FileNotFoundError:
                st.info("※ここに図面の画像が表示されます。")
    else:
        st.warning(f"「{search_word}」に関連する資材は見つかりませんでした。")
        
else:
    # 検索窓が空の時
    col1, col2 = st.columns([6, 4])
    
    with col1:
        st.markdown("### 📋 全データ一覧")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    with col2:
        st.markdown("### 🗺️ マップ")
        try:
            st.image("map_image.png", caption="図面上の番号と照らし合わせてください")
        except FileNotFoundError:
            st.info("※ここに図面の画像が表示されます。")
