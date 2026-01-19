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

### Altitude Calculation

高度の定義:
```
altitude_km = geocentric_distance_km - 6371.0
```

- **geocentric_distance**: 地球中心から衛星までの距離
- **6371.0 km**: 地球の平均半径
- **伝搬モデル**: SGP4 (Simplified General Perturbations)

### Data Point Limits

- 最大データポイント数: **20,000点**
- 超過時: 400エラーを返却
- 推奨: step_secondsを増やすか、期間を短縮

### CORS Configuration

開発環境では `localhost:3000` からのリクエストを許可しています。本番環境では `backend/.env` で適切なオリジンを設定してください。

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
