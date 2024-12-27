import streamlit as st
from openpyxl import Workbook
import pandas as pd
from io import BytesIO

# Secretsからパスワードを取得
PASSWORD = st.secrets["PASSWORD"]

# パスワード認証の処理
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0

def verificar_contraseña():
    contraseña_ingresada = st.text_input("Introduce la contraseña:", type="password")

    if st.button("Iniciar sesión"):
        if st.session_state.login_attempts >= 3:
            st.error("Has superado el número máximo de intentos. Acceso bloqueado.")
        elif contraseña_ingresada == PASSWORD:  # Secretsから取得したパスワードで認証
            st.session_state.authenticated = True
            st.success("¡Autenticación exitosa! Marque otra vez el botón 'Iniciar sesión'.")
        else:
            st.session_state.login_attempts += 1
            intentos_restantes = 3 - st.session_state.login_attempts
            st.error(f"Contraseña incorrecta. Te quedan {intentos_restantes} intento(s).")
        
        if st.session_state.login_attempts >= 3:
            st.error("Acceso bloqueado. Intenta más tarde.")

if st.session_state.authenticated:
    # 認証成功後に表示されるメインコンテンツ
    st.write("### :blue[Plan de pagos de deuda e interés]") 
    st.write("###### Esta herramienta calcula el monto de la cuota mensual, la proporción de intereses y capital en un préstamo de amortización constante y genera el cuadro de amortización del préstamo.")  
    
    # 入力項目
    principal = st.number_input("Monto del préstamo (GTQ):", min_value=0, value=20000, step=1000, format="%d")
    annual_rate = st.number_input("Tasa de interés anual (%):", min_value=0.0, value=26.0, step=0.1, format="%f")
    months = st.number_input("Plazo de reembolso (meses):", min_value=1, value=15, step=1, format="%d")
    
    # 計算を行うボタン
    if st.button("Calcular el cuadro de amortización"):
        # 月利の計算
        monthly_rate = annual_rate / 100 / 12
    
        # 毎月の返済額の計算
        monthly_payment = (principal * monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    
        # 初期設定
        balance = principal
        schedule = []
    
        # 各月の償還表を作成
        for month in range(1, months + 1):
            interest_payment = balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            balance -= principal_payment
            schedule.append([month, round(monthly_payment), round(principal_payment), round(interest_payment), round(balance)])
    
        # データフレームに変換し、インデックスを表示しない
        df = pd.DataFrame(schedule, columns=["Mes", "Pago mensual (GTQ)", "Pago a capital (GTQ)", "Interés (GTQ)", "Saldo restante (GTQ)"])
    
        # 結果の表示（インデックスをリセットして表示）
        st.write("#### Cuadro de Amortización en base al plan de cuotas niveladas")
        st.dataframe(df.reset_index(drop=True))
    
        # Excelファイルのダウンロードオプション
        def generate_excel(dataframe):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                dataframe.to_excel(writer, index=False, sheet_name="Amortización")
            return output.getvalue()
    
        excel_data = generate_excel(df)
        st.download_button(
            label="Descargar el cuadro en Excel",
            data=excel_data,
            file_name="cuadro_de_amortizacion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    verificar_contraseña()
    


