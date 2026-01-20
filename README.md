# 🛰️ Satellite Altitude Tracker

人工衛星の高度変動を可視化するWebアプリケーション。NORAD catalog numberと日時範囲を指定することで、TLEデータを用いた軌道計算により高度の時系列データを取得し、グラフで可視化できます。

## ✨ Features

- **リアルタイムTLE取得**: CelesTrakから最新のTLEデータを自動取得
- **高精度軌道計算**: Skyfieldライブラリを使用したSGP4伝搬モデル
- **インタラクティブなグラフ**: Plotly.jsによる高度データの可視化
- **プレミアムUI**: グラスモーフィズムとダークモードを採用したモダンなデザイン
- **統計情報表示**: 最小・最大・平均高度、変動範囲の自動計算

## 🏗️ Tech Stack

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Chart**: Plotly.js + react-plotly.js
- **Date Handling**: date-fns

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Orbit Propagation**: Skyfield
- **HTTP Client**: httpx
- **Server**: Uvicorn

## 📁 Project Structure

```
satellitealt-app/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # API endpoints and business logic
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variable template
│   └── .gitignore          # Python-specific gitignore
├── src/
│   └── app/
│       ├── page.tsx        # Main satellite tracker UI
│       ├── layout.tsx      # Root layout
│       └── globals.css     # Global styles with custom components
├── .env.local              # Frontend environment variables (not committed)
├── .env.example            # Frontend env template
├── package.json            # Node dependencies
└── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites

- **Node.js**: 18.0 or higher
- **Python**: 3.9 or higher
- **pnpm**: Package manager (or npm/yarn)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Create a `.env` file from the template:
```bash
cp .env.example .env
```

5. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The backend server will be available at `http://localhost:8000`

- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the project root directory:
```bash
cd ..  # if you're in the backend directory
```

2. Install Node dependencies:
```bash
pnpm install
# or
npm install
```

3. Create `.env.local` file (if not already created):
```bash
cp .env.example .env.local
```

The default configuration points to `http://localhost:8000` for the backend.

4. Start the Next.js development server:
```bash
pnpm dev
# or
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 Usage

1. **Backend起動**: `backend/` ディレクトリで `uvicorn main:app --reload` を実行
2. **Frontend起動**: プロジェクトルートで `pnpm dev` を実行
3. **ブラウザアクセス**: http://localhost:3000 を開く
4. **衛星選択**: NORAD IDを入力（例: 25544 = ISS）
5. **期間設定**: 開始・終了時刻とステップ秒数を指定
6. **実行**: "Calculate Altitude" をクリック
7. **結果確認**: グラフと統計情報が表示されます

### Example NORAD IDs

- **25544**: International Space Station (ISS)
- **43013**: Starlink-24
- **20580**: NOAA 15
- **42983**: Hubble Space Telescope

## 🔌 API Documentation

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok"
}
```

### Get Altitude Data

**Endpoint**: `GET /altitude`

**Query Parameters**:
- `n` (required): NORAD catalog number (integer, >= 1)
- `start` (required): Start time in ISO8601 UTC format (e.g., `2026-01-19T00:00:00Z`)
- `end` (required): End time in ISO8601 UTC format
- `step_seconds` (optional): Time step in seconds (default: 60, range: 1-3600)

**Example**:
```
GET /altitude?n=25544&start=2026-01-19T00:00:00Z&end=2026-01-19T06:00:00Z&step_seconds=60
```

**Response**:
```json
{
  "norad_id": 25544,
  "start": "2026-01-19T00:00:00Z",
  "end": "2026-01-19T06:00:00Z",
  "step_seconds": 60,
  "points": [
    {
      "t": "2026-01-19T00:00:00Z",
      "alt_km": 417.23
    },
    {
      "t": "2026-01-19T00:01:00Z",
      "alt_km": 417.45
    }
  ],
  "meta": {
    "tle_source": "celestrak",
    "tle_epoch": "24001.12345678",
    "earth_radius_km": 6371.0
  }
}
```

**Error Responses**:
- `400`: Invalid parameters or too many data points (>20,000)
- `404`: NORAD ID not found in CelesTrak database
- `502`: CelesTrak service unavailable or network error
- `500`: Internal server error

## 🔬 Technical Details

### TLE Data Source

TLEデータは [CelesTrak](https://celestrak.org/) から取得しています:
- URL: `https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE`
- リアルタイム取得（データベース保存なし）
- 開始時刻に最も近いepochのTLEを使用

### TLE (Two-Line Element Set) とは

TLE は衛星の軌道要素を表す標準フォーマットです。3行で構成されます：

```
ISS (ZARYA)             
1 25544U 98067A   26019.20762778  .00012345  00000-0  12345-3 0  9999
2 25544  51.6420 123.4567 0001234  12.3456 347.7890 15.12345678123456
```

**Line 0**: 衛星名  
**Line 1**: カタログ番号、epoch（元期）、平均運動の1次微分など  
**Line 2**: 軌道傾斜角、昇交点赤経、離心率、近地点引数、平均近点角、平均運動など

### SGP4 伝搬モデル

**SGP4 (Simplified General Perturbations 4)** は地球周回衛星の位置と速度を予測する数学モデルです。

**考慮する摂動項**:
- 地球の扁平率 (J2, J3, J4)
- 大気抵抗（低軌道衛星の場合）
- 太陽・月の重力の影響（簡略化）

**入力**:
- TLE（軌道要素）
- 予測したい時刻（UTC）

**出力**:
- 衛星の位置ベクトル (x, y, z) [km]（TEME座標系）
- 衛星の速度ベクトル (vx, vy, vz) [km/s]

### 高度計算の実装

本アプリケーションでは **Skyfield** ライブラリを使用してSGP4計算を実行します。

#### ステップ1: TLE読み込み

```python
from skyfield.api import EarthSatellite, load

ts = load.timescale()
satellite = EarthSatellite(tle_line1, tle_line2, "Satellite", ts)
```

#### ステップ2: 時刻配列の生成

```python
# ユーザー指定の開始・終了時刻とステップ秒数から時刻配列を生成
current_time = start_time
while current_time <= end_time:
    t = ts.utc(current_time.year, current_time.month, current_time.day,
               current_time.hour, current_time.minute, current_time.second)
    # 計算処理
    current_time += timedelta(seconds=step_seconds)
```

#### ステップ3: 地心位置の計算

```python
# 衛星の地心位置を取得
geocentric = satellite.at(t)
position = geocentric.position.km  # [x, y, z] in km (TEME座標系)
```

#### ステップ4: 地心距離の計算

```python
# 3次元ベクトルのノルム（ユークリッド距離）
geocentric_distance = sqrt(x^2 + y^2 + z^2)

# Pythonコードでの実装:
geocentric_distance = (position[0]**2 + position[1]**2 + position[2]**2) ** 0.5
```

#### ステップ5: 高度の算出

```python
# 高度 = 地心距離 - 地球の平均半径
altitude_km = geocentric_distance - 6371.0
```

### 高度定義の詳細

**地心距離 (Geocentric Distance)**:
- 地球の中心から衛星までの直線距離
- TEME (True Equator Mean Equinox) 座標系で計算
- 単位: キロメートル [km]

**地球の平均半径**:
- 本アプリでは **6371.0 km** を使用
- これは地球を完全な球体と仮定した場合の平均値
- 実際の地球は回転楕円体ですが、MVPとして球体近似を採用

**高度 (Altitude)**:
```
altitude = geocentric_distance - 6371.0 [km]
```

この定義により：
- ISSの高度 ≈ 400-420 km
- 静止衛星の高度 ≈ 35,786 km

### 座標系: TEME

**TEME (True Equator Mean Equinox)**:
- SGP4モデルが出力する標準座標系
- 地球の真の赤道面と平均春分点を基準とする慣性座標系
- 地球の自転とは独立（恒星に対して固定）

**特徴**:
- X軸: 平均春分点方向
- Z軸: 地球の真の回転軸（北極）方向
- Y軸: 右手系を構成する方向

### 計算精度と制限事項

**精度**:
- SGP4モデルは一般的に **数km程度の誤差**
- TLEの鮮度に依存（古いTLEほど誤差が増加）
- 予測期間が長いほど誤差が累積

**制限事項**:
1. **球体近似**: 地球を完全な球体として扱う
2. **TLE単一使用**: 計算期間中、1つのTLEのみを使用（実際は定期的に更新が必要）
3. **大気密度**: 実際の大気密度変動を完全には考慮していない
4. **長期予測**: 数日～数週間の予測が限界（それ以上は誤差が大きい）

### 数式まとめ

1. **地心距離**:
   ```
   r = √(x² + y² + z²)
   ```

2. **高度**:
   ```
   h = r - R_earth
   where R_earth = 6371.0 km
   ```

3. **データポイント数**:
   ```
   N = ⌊(t_end - t_start) / Δt⌋ + 1
   where Δt = step_seconds
   ```

### ライブラリ

- **Skyfield** (v1.49): 天文計算ライブラリ
  - SGP4実装を内包
  - 高精度な時刻処理
  - 座標変換機能
  - NASA JPLの DE421 惑星暦をサポート

- **sgp4** (組み込み): Skyfieldが内部で使用
  - SGP4/SDP4アルゴリズムの実装
  - TLE解析機能

## 🛠️ Development Notes

### Backend Development

FastAPIの自動ドキュメント:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Development

- Hot Reload対応（ファイル保存時に自動反映）
- TypeScript型チェック: `pnpm tsc --noEmit`
- Lint: `pnpm lint`

### Environment Variables

**Backend** (`backend/.env`):
```env
PORT=8000
HOST=0.0.0.0
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## 🚧 Known Limitations

- TLE切替なし: 計算期間中はひとつのTLEを使用（将来的には期間中のTLE切替を実装予定）
- 大気抵抗未考慮: SGP4モデルの制約により、長期予測の精度には限界があります
- キャッシュなし: 毎回CelesTrakからTLEを取得（同一衛星の連続リクエストで最適化の余地あり）

## 📝 Future Enhancements

- [ ] TLE履歴管理とデータベース保存
- [ ] 複数衛星の同時表示・比較機能
- [ ] 3D軌道可視化
- [ ] 地上軌跡（Ground Track）表示
- [ ] エクスポート機能（CSV/JSON）
- [ ] レート制限とキャッシング
- [ ] ユーザー認証

## 📄 License

This project is created for educational and demonstration purposes.

## 🙏 Acknowledgments

- [CelesTrak](https://celestrak.org/) - TLE data provider
- [Skyfield](https://rhodesmill.org/skyfield/) - Satellite position calculation library
- [Plotly](https://plotly.com/) - Data visualization library
