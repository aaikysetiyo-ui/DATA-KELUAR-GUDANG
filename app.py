import io
from datetime import date
import pandas as pd
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Sparepart Exit Manager", page_icon="⚙️", layout="wide"
)

# Inisialisasi Database Sesi (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "sparepart_data" not in st.session_state:
    # Data contoh awal
    st.session_state.sparepart_data = pd.DataFrame(
        [
            {
                "Kode Part": "FLT-001",
                "Nama Sparepart": "Filter Oli Hino",
                "Plat Nomor": "B 9123 KFD",
                "Qty": 2,
                "Satuan": "Pcs",
                "Tanggal Keluar": str(date.today()),
                "Keterangan": "Servis Rutin",
            },
            {
                "Kode Part": "BRK-005",
                "Nama Sparepart": "Kampas Rem Depan",
                "Plat Nomor": "B 9481 TTR",
                "Qty": 1,
                "Satuan": "Set",
                "Tanggal Keluar": str(date.today()),
                "Keterangan": "Penggantian Rem Aus",
            },
        ]
    )


# ==================== HALAMAN LOGIN ====================
def login_page():
  col1, col2, col3 = st.columns([1, 1.2, 1])
  with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='text-align: center;'>⚙️ Sparepart Exit Manager</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: gray;'>Silakan login untuk"
        " masuk ke sistem</p>",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
      username = st.text_input("Username", placeholder="admin")
      password = st.text_input(
          "Password", type="password", placeholder="••••••••"
      )
      submit = st.form_submit_button("Login ke Aplikasi", use_container_width=True)

      if submit:
        if username == "admin" and password == "admin123":
          st.session_state.logged_in = True
          st.rerun()
        else:
          st.error("Username atau Password salah! (Gunakan: admin / admin123)")

    st.info("💡 **Info Login:** Username: `admin` | Password: `admin123`")


# ==================== APLIKASI UTAMA ====================
def main_app():
  # Sidebar Menu & Import Excel
  with st.sidebar:
    st.markdown("### ⚙️ Sparepart Manager")
    st.markdown("---")
    st.markdown("#### 📥 Import Data Excel")

    uploaded_file = st.file_uploader(
        "Upload file Excel (.xlsx / .csv)", type=["xlsx", "xls", "csv"]
    )

    if uploaded_file is not None:
      try:
        if uploaded_file.name.endswith(".csv"):
          df_import = pd.read_csv(uploaded_file)
        else:
          df_import = pd.read_excel(uploaded_file)

        if st.button("Proses Import Data", use_container_width=True):
          new_count = 0
          agg_count = 0

          # Normalisasi kolom
          df_import.columns = [str(c).strip().title() for c in df_import.columns]

          for _, row in df_import.iterrows():
            kode = str(row.get("Kode Part", row.get("Kode", ""))).strip().upper()
            nama = str(
                row.get(
                    "Nama Sparepart", row.get("Nama", row.get("Sparepart", ""))
                )
            ).strip()
            plat = (
                str(
                    row.get(
                        "Plat Nomor",
                        row.get("No Polisi", row.get("Plat", "-")),
                    )
                )
                .strip()
                .upper()
            )
            try:
              qty = int(row.get("Qty", row.get("Jumlah", 1)))
            except:
              qty = 1
            satuan = str(row.get("Satuan", row.get("Unit", "Pcs"))).strip()
            tgl = str(row.get("Tanggal Keluar", row.get("Tanggal", date.today())))
            ket = str(
                row.get("Keterangan", row.get("Penerima", "-"))
            ).strip()

            if not kode or not nama:
              continue

            # Logika Agregasi (Kode Part + Plat Nomor sama)
            existing_idx = st.session_state.sparepart_data[
                (
                    st.session_state.sparepart_data["Kode Part"].str.upper()
                    == kode
                )
                & (
                    st.session_state.sparepart_data["Plat Nomor"].str.upper()
                    == plat
                )
            ].index

            if not existing_idx.empty:
              idx = existing_idx[0]
              st.session_state.sparepart_data.loc[idx, "Qty"] += qty
              if ket and ket != "-" and ket not in str(st.session_state.sparepart_data.loc[idx, "Keterangan"]):
                st.session_state.sparepart_data.loc[idx, "Keterangan"] += (
                    f", {ket}"
                )
              agg_count += 1
            else:
              new_row = pd.DataFrame(
                  [{
                      "Kode Part": kode,
                      "Nama Sparepart": nama,
                      "Plat Nomor": plat if plat else "-",
                      "Qty": qty,
                      "Satuan": satuan if satuan else "Pcs",
                      "Tanggal Keluar": str(tgl),
                      "Keterangan": ket if ket else "-",
                  }]
              )
              st.session_state.sparepart_data = pd.concat(
                  [st.session_state.sparepart_data, new_row], ignore_index=True
              )
              new_count += 1

          st.success(
              f"Import Berhasil!\n- Data Baru: {new_count}\n- Teragregasi (Kode+"
              f" Plat Sama): {agg_count}"
          )
          st.rerun()
      except Exception as e:
        st.error(f"Gagal membaca file: {e}")

    # Tombol Download Template Excel
    template_df = pd.DataFrame([
        {
            "Kode Part": "FLT-001",
            "Nama Sparepart": "Filter Oli Hino",
            "Plat Nomor": "B 9123 KFD",
            "Qty": 2,
            "Satuan": "Pcs",
            "Tanggal Keluar": str(date.today()),
            "Keterangan": "Servis Rutin",
        },
        {
            "Kode Part": "BRK-005",
            "Nama Sparepart": "Kampas Rem Depan",
            "Plat Nomor": "B 9481 TTR",
            "Qty": 1,
            "Satuan": "Set",
            "Tanggal Keluar": str(date.today()),
            "Keterangan": "Penggantian Rem Aus",
        },
    ])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
      template_df.to_excel(writer, index=False, sheet_name="Template")
    st.download_button(
        label="📥 Download Template Excel",
        data=output.getvalue(),
        file_name="Template_Import_Sparepart.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("#### 📊 Statistik Ringkasan")
    total_parts = (
        st.session_state.sparepart_data["Kode Part"].nunique()
        if not st.session_state.sparepart_data.empty
        else 0
    )
    total_qty = (
        st.session_state.sparepart_data["Qty"].sum()
        if not st.session_state.sparepart_data.empty
        else 0
    )
    total_plats = (
        st.session_state.sparepart_data["Plat Nomor"].nunique()
        if not st.session_state.sparepart_data.empty
        else 0
    )
    total_records = len(st.session_state.sparepart_data)

    st.metric("Total Item Part", total_parts)
    st.metric("Total Qty Keluar", total_qty)
    st.metric("Plat Terdaftar", total_plats)
    st.metric("Total Baris Transaksi", total_records)

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
      st.session_state.logged_in = False
      st.rerun()

  # Main Dashboard Area
  st.title("🛠️ Sistem Manajemen Sparepart Keluar")
  st.markdown(
      "Kelola data sparepart keluar, import excel otomatis dengan agregasi"
      " kode & plat nomor."
  )

  if st.session_state.sparepart_data.empty:
    st.info(
        "Belum ada data transaksi. Silakan upload file Excel melalui sidebar"
        " di sebelah kiri."
    )
    return

  # Filter Kontrol
  col1, col2, col3 = st.columns([2, 1.5, 1.5])
  with col1:
    search_query = st.text_input(
        "🔍 Cari (Kode Part, Nama, Plat, Keterangan)", ""
    )
  with col2:
    plats_list = ["Semua"] + list(
        st.session_state.sparepart_data["Plat Nomor"].unique()
    )
    selected_plat = st.selectbox("Filter Plat Nomor", plats_list)
  with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Reset Filter"):
      search_query = ""
      selected_plat = "Semua"

  # Terapkan Filter
  filtered_df = st.session_state.sparepart_data.copy()
  if search_query:
    query = search_query.lower()
    filtered_df = filtered_df[
        filtered_df["Kode Part"].str.lower().str.contains(query)
        | filtered_df["Nama Sparepart"].str.lower().str.contains(query)
        | filtered_df["Plat Nomor"].str.lower().str.contains(query)
        | filtered_df["Keterangan"].str.lower().str.contains(query)
    ]

  if selected_plat != "Semua":
    filtered_df = filtered_df[filtered_df["Plat Nomor"] == selected_plat]

  # Tampilkan Tabel Data
  st.markdown("### 📋 Daftar Transaksi Sparepart Keluar")
  st.dataframe(
      filtered_df.reset_index(drop=True), use_container_width=True, height=350
  )

  # Tombol Export Excel
  col_ex1, col_ex2 = st.columns([2, 8])
  with col_ex1:
    excel_out = io.BytesIO()
    with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
      filtered_df.to_excel(writer, index=False, sheet_name="Rekapan_Sparepart")
    st.download_button(
        label="📥 Export ke Excel",
        data=excel_out.getvalue(),
        file_name=f"Rekapan_Sparepart_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

  st.markdown("---")
  st.markdown("### ✏️ Edit atau Hapus Data Satuan")

  if not filtered_df.empty:
    selected_row_idx = st.selectbox(
        "Pilih baris transaksi untuk diedit/dihapus:",
        options=filtered_df.index,
        format_func=lambda x: (
            f"[{filtered_df.loc[x, 'Kode Part']}]"
            f" {filtered_df.loc[x, 'Nama Sparepart']} - Plat:"
            f" {filtered_df.loc[x, 'Plat Nomor']} (Qty:"
            f" {filtered_df.loc[x, 'Qty']})"
        ),
    )

    with st.form("edit_delete_form"):
      c1, c2, c3 = st.columns(3)
      with c1:
        new_kode = st.text_input(
            "Kode Part",
            value=st.session_state.sparepart_data.loc[
                selected_row_idx, "Kode Part"
            ],
        )
        new_nama = st.text_input(
            "Nama Sparepart",
            value=st.session_state.sparepart_data.loc[
                selected_row_idx, "Nama Sparepart"
            ],
        )
      with c2:
        new_plat = st.text_input(
            "Plat Nomor",
            value=st.session_state.sparepart_data.loc[
                selected_row_idx, "Plat Nomor"
            ],
        )
        new_qty = st.number_input(
            "Qty",
            min_value=1,
            value=int(
                st.session_state.sparepart_data.loc[selected_row_idx, "Qty"]
            ),
        )
      with c3:
        new_satuan = st.selectbox(
            "Satuan",
            ["Pcs", "Set", "Unit", "Box", "Liter", "Meter", "Roll"],
            index=0,
        )
        new_ket = st.text_input(
            "Keterangan",
            value=st.session_state.sparepart_data.loc[
                selected_row_idx, "Keterangan"
            ],
        )

      col_btn1, col_btn2 = st.columns(2)
      with col_btn1:
        submit_update = st.form_submit_button(
            "💾 Simpan Perubahan", use_container_width=True
        )
      with col_btn2:
        submit_delete = st.form_submit_button(
            "🗑️ Hapus Baris Ini", use_container_width=True
        )

      if submit_update:
        st.session_state.sparepart_data.loc[selected_row_idx, "Kode Part"] = (
            new_kode.upper()
        )
        st.session_state.sparepart_data.loc[selected_row_idx, "Nama Sparepart"] = (
            new_nama
        )
        st.session_state.sparepart_data.loc[selected_row_idx, "Plat Nomor"] = (
            new_plat.upper()
        )
        st.session_state.sparepart_data.loc[selected_row_idx, "Qty"] = new_qty
        st.session_state.sparepart_data.loc[selected_row_idx, "Satuan"] = (
            new_satuan
        )
        st.session_state.sparepart_data.loc[selected_row_idx, "Keterangan"] = (
            new_ket
        )
        st.success("Data berhasil diperbarui!")
        st.rerun()

      if submit_delete:
        st.session_state.sparepart_data = (
            st.session_state.sparepart_data.drop(selected_row_idx)
            .reset_index(drop=True)
        )
        st.success("Data berhasil dihapus!")
        st.rerun()


# Kontrol Alur Sesi
if not st.session_state.logged_in:
  login_page()
else:
  main_app()
