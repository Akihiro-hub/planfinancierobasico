import streamlit as st
from openpyxl import Workbook
import pandas as pd
from io import BytesIO

col1, col2 = st.columns(2)
with col1:
    st.write("### :blue[Planificación de préstamos]") 
    st.write("###### El monto disponible para el préstamo dependerá de (i) cuota mensual a poder pagar, (ii) tasa de interés, y (iii) período de amortización, como se puede calcular mediante esta herramienta.")
    a = st.number_input("Cuota mensual (GTQ)", 0, 1000000000, 2000)
    b = st.number_input("Tasa anual de interés %", 0, 100, 18)
    c = st.number_input("Periodo de amortización (meses)", 0, 100, 12)
    d = (a * ((1 + b/1200)**c - 1)) / (b/1200 * (1 + b/1200)**c)

    if st.button("Calcular"):
        st.write("##### :blue[Resultado del cálculo: Monto total disponible para el préstamo (GTQ):]")
        st.text(round(d))

with col2:
    st.write("### :blue[Plan de pagos de deuda e interés]") 
    st.write("###### Esta herramienta calcula el monto de la cuota mensual, la proporción de intereses y capital en un préstamo de amortización constante y genera el cuadro de amortización del préstamo.]")  

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



