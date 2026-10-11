import streamlit as st
import pandas as pd

# アプリの基本設定
st.set_page_config(page_title="保管場所検索アプリ", layout="wide")
st.title("📦 資材・保管場所検索アプリ")
st.write("探したい資材の名前を入力してください。")

# データの読み込み
@st.cache_data
def load_data():
    # 同じフォルダにある inventory_data.csv を読み込む
    return pd.read_csv("inventory_data.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("エラー：'inventory_data.csv' というファイルが見つかりません。")
    st.stop()

# 検索窓
search_word = st.text_input("🔍 検索キーワード（例：雑巾、段ボール）")

if search_word:
    # 検索処理（空欄を無視して検索）
    result_df = df[df["資材名"].astype(str).str.contains(search_word, na=False)]
    st.markdown("### 📋 検索結果")

    if len(result_df) > 0:
        st.dataframe(result_df, use_container_width=True, hide_index=True)
        st.markdown("### 🗺️ マップ")
        try:
            st.image("map_image.png", caption="図面上の番号と照らし合わせてください")
        except FileNotFoundError:
            st.info("※ここに図面の画像が表示されます。（現在画像ファイルがアップロードされていません）")
    else:
        st.warning("指定されたキーワードの資材は見つかりませんでした。")
else:
    st.markdown("### 📋 全データ一覧")
    st.dataframe(df, use_container_width=True, hide_index=True)