# PoC Dashboard — Analisis Sentimen & SNA Lintas Platform

> **Proof-of-Concept** untuk Tugas Akhir S1 Teknik Informatika.
> Dashboard ini menggunakan **data sintetis** untuk memvalidasi struktur UI, alur pencarian, dan kerangka data — sebelum integrasi data asli.

---

## 1. Cara Menjalankan

### Prasyarat
- Python ≥ 3.10
- pip (package manager Python)

### Instalasi

```bash
# Dari root project
cd dashboard/poc

# (Opsional) Buat virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Menjalankan Aplikasi

```bash
# Dari root project
streamlit run dashboard/poc/app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`.

### Penggunaan
1. Ketik kata kunci di kotak pencarian (contoh: `Sekolah Rakyat`, `MBG`, `KDMP`)
2. Tekan tombol **Cari**
3. Jelajahi 9 tab dashboard yang muncul

---

## 2. Struktur File

```
dashboard/poc/
├── app.py                    # Aplikasi utama Streamlit (orchestrator 9 tab)
├── data/
│   ├── __init__.py
│   └── mock_provider.py      # 14 fungsi mock data generator
├── components/
│   ├── __init__.py
│   └── charts.py             # Fungsi pembangun chart/visualisasi reusable
├── requirements.txt          # Dependencies Python
└── README.md                 # Dokumentasi ini
```

---

## 3. Peta Integrasi Data Asli

Tabel berikut memetakan setiap fungsi mock ke sumber data riil yang akan digunakan setelah PoC terbukti layak:

| # | Fungsi Mock | Sumber Data Asli | Catatan |
|---|---|---|---|
| 1 | `get_overview_metrics(keyword)` | **PostgreSQL** — `SELECT COUNT(*), COUNT(DISTINCT author_id), SUM(engagement), SUM(reach) FROM posts WHERE keyword_match(content, :kw)` + proporsi dari tabel `sentiment_labels` | Sentimen berasal dari inferensi IndoBERT |
| 2 | `get_mentions_trend(keyword, dimension)` | **PostgreSQL** — aggregate harian `GROUP BY DATE(created_at), {dimension_column}` dari tabel `posts JOIN sentiment_labels / emotion_labels` | Periode 30 hari, kolom dimensi sesuai parameter |
| 3 | `get_platform_sentiment(keyword, platform)` | **PostgreSQL** — `GROUP BY sentiment_label WHERE platform = :platform` | Label sentimen dari IndoBERT fine-tuned |
| 4 | `get_emotion_distribution(keyword)` | **PostgreSQL** — `GROUP BY emotion_label` dari tabel `emotion_labels` | Klasifikasi emosi Ekman via IndoBERT fine-tuned pada GoEmotions-ID / dataset custom |
| 5 | `get_top_emoji(keyword)` | **PostgreSQL** — regex extraction emoji dari kolom `content`, `GROUP BY emoji ORDER BY COUNT DESC` | Pure SQL, tanpa model ML |
| 6 | `get_sna_graph(keyword, mode)` | **NetworkX** — graf dibangun dari tabel `interactions` (reply, retweet, mention). Node attributes dari `users JOIN sentiment_labels`. Sentralitas dihitung oleh `nx.degree_centrality()` | Data interaksi dari scraping API platform |
| 7 | `get_top_issues(keyword)` | **BERTopic / LDA** — topic modeling pada korpus posts yang match keyword. Output: label topik, jumlah mention, distribusi platform | Alternatif: K-Means clustering pada embedding IndoBERT |
| 8 | `get_issue_diffusion(keyword)` | **PostgreSQL** — `GROUP BY DATE(created_at), platform, topic_label` setelah topic modeling | Menunjukkan pola penyebaran isu antar platform |
| 9 | `get_news_sites(keyword)` | **PostgreSQL** — `GROUP BY domain WHERE platform = 'Berita Online'` | Domain diekstrak dari URL berita |
| 10 | `get_top_influencers(keyword, platform)` | **PostgreSQL** — `JOIN users ON author_id`, diurutkan berdasarkan engagement rate (`AVG(engagement) / follower_count`) | Follower count dari data scraping profil |
| 11 | `get_viral_content(keyword, platform)` | **PostgreSQL** — `ORDER BY (like_count + share_count + comment_count) DESC LIMIT 10` | Langsung dari tabel posts |
| 12 | `get_wordcloud_data(keyword, scope)` | **NLP Pipeline** — tokenisasi → stopword removal → stemming (Sastrawi) → TF-IDF / raw frequency. Untuk hashtag: regex `#(\w+)` | Preprocessing Bahasa Indonesia |
| 13 | `get_popular_terms_table(keyword)` | Gabungan output #12, di-aggregate lintas platform | Menunjukkan platform mana saja term/tagar muncul |
| 14 | `get_raw_scraped_data(keyword, n_rows)` | **PostgreSQL / Scraper File** — `SELECT p.post_id, p.platform, u.display_name, p.content, s.sentiment_label, e.emotion_label, p.like_count, ... FROM posts p LEFT JOIN users u ...` atau pembacaan file CSV/JSON hasil scraper | Menampilkan tabular data mentah + file upload |

### Langkah Integrasi
1. **Ganti isi** setiap fungsi di `data/mock_provider.py` — signature dan return type **tidak berubah**
2. **Hapus** dekorator `@st.cache_data` atau ganti TTL sesuai kebutuhan data real-time
3. **Kode UI** di `app.py` dan `components/charts.py` **tidak perlu diubah** sama sekali
4. Tambahkan koneksi database (SQLAlchemy / psycopg2) dan model loading (transformers / ONNX) di modul terpisah, dipanggil dari dalam fungsi data

### Arsitektur Target (Post-PoC)

```
project/
├── ingestion/          # Scraper per platform (X, FB, IG, YT, TikTok, Threads, News)
├── models/             # IndoBERT sentiment, emotion, topic modeling
├── sna/                # Konstruksi graf & analisis sentralitas
├── data/               # Koneksi DB, query builder, cache layer
├── dashboard/
│   ├── poc/            # ← Dashboard ini (bisa di-retire setelah integrasi)
│   └── main/           # Dashboard final dengan data asli
└── notebooks/          # Eksperimen & EDA
```

---

## 4. Catatan Teknis

### Caching
- Fungsi data menggunakan `@st.cache_data` (atau `@st.cache_resource` untuk objek non-serializable seperti Graph)
- Data di-cache berdasarkan parameter keyword → tidak di-regenerate ulang saat interaksi widget
- Untuk data asli, pertimbangkan `@st.cache_data(ttl=3600)` (cache 1 jam)

### Keyword sebagai Seed
- `hash(keyword)` digunakan sebagai random seed → output selalu konsisten untuk keyword yang sama
- Ini memungkinkan demonstrasi yang reproducible saat presentasi TA

### Graf SNA
- Pyvis menghasilkan HTML yang di-embed via `st.components.v1.html`
- Graf mendukung interaksi: zoom, drag node, hover tooltip
- Untuk data asli, graf akan jauh lebih padat — pertimbangkan filtering top-N node berdasarkan sentralitas

---

## 5. Catatan Hasil Percobaan

> **Instruksi**: Isi bagian di bawah ini setelah menjalankan dan menguji PoC.
> Bagian ini akan didokumentasikan sebagai bagian dari metodologi TA.

### 5.1. Kejelasan Struktur 8 Tab
<!-- Apakah struktur tab cukup jelas? Apakah ada tab yang membingungkan? -->
- [ ] Struktur tab jelas dan intuitif
- [ ] Ada tab yang perlu digabung/dipisah: ___
- [ ] Catatan: ___

### 5.2. Alur Pencarian Kata Kunci
<!-- Apakah alur pencarian → dashboard muncul terasa natural? -->
- [ ] Alur terasa natural dan responsif
- [ ] Ada delay yang terasa: ___
- [ ] Catatan: ___

### 5.3. Fleksibilitas Data Layer
<!-- Apakah kerangka fungsi mock_provider sudah cukup fleksibel? -->
- [ ] Signature fungsi sudah sesuai kebutuhan data asli
- [ ] Ada fungsi yang perlu ditambah/diubah: ___
- [ ] Catatan: ___

### 5.4. Performa Render
<!-- Apakah visualisasi (chart, graf SNA, word cloud) responsif? -->
- [ ] Semua visualisasi render tanpa lag signifikan
- [ ] Visualisasi yang lambat: ___
- [ ] Catatan: ___

### 5.5. Temuan & Rekomendasi Lain
<!-- Catatan tambahan yang ditemukan saat pengujian -->
-
-
-

---

## 6. Lisensi

Proyek ini adalah bagian dari Tugas Akhir dan bersifat akademis.
