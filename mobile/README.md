# SmartWasteAI — Mobile app (design stub)

React Native companion app for informal waste pickers. **Not shipped in MVP** — API endpoints available at `/api/v1/workers`.

## Screens (design only)

- `screens/ScanScreen.md` — QR scan to log collection
- `screens/EarningsScreen.md` — daily earnings + payment history
- `screens/NearbyBinsScreen.md` — map of high-DCPI bins nearby

## API integration

```
POST /api/v1/workers/{id}/scan
Body: { "qr_code": "QR-0001", "weight_kg": 2.5 }
```

Figma mockups: add link here post-design.
