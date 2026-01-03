# ✨ Features Updated - Images & Social Sharing Buttons

## Changes Made

### 1. ✅ Image Support
**Files Modified**: `workers/uk/worker_uk_v2.py`, `coordinator/main.py`

- Worker now accepts `photo_url` parameter in `parse_message()`
- Images are preserved in deal data structure
- Both worker and coordinator send photos with deals
- Fallback to text-only if photo fails

### 2. ✅ Interactive Buttons
**Files Modified**: `workers/uk/worker_uk_v2.py`, `coordinator/main.py`

Added `InlineKeyboardMarkup` with 5 buttons:

#### Button Layout:
```
┌─────────────────────────────┐
│  🛒 VIEW ON AMAZON          │
├──────────────┬──────────────┤
│ 💬 WhatsApp  │ 👍 Facebook  │
├──────────────┼──────────────┤
│ 𝕏 Twitter    │ ✈️ Telegram  │
└──────────────┴──────────────┘
```

#### Button Functions:
- **VIEW ON AMAZON**: Direct link to Amazon product with affiliate tag
- **WhatsApp**: Share deal via WhatsApp with price and link
- **Facebook**: Share to Facebook with product link
- **Twitter**: Tweet the deal with price and link
- **Telegram**: Share to Telegram with full deal info

### 3. ✅ URL Encoding
**Import Added**: `from urllib.parse import quote`

- All sharing URLs are properly encoded
- Special characters handled correctly
- Works across all social platforms

### 4. ✅ Test Messages with Images
**File Modified**: `workers/uk/worker_uk_v2.py`

Test messages now include sample image URLs:
```python
{
    'text': '...',
    'photo': 'https://m.media-amazon.com/images/...'
}
```

## Message Format

### Before:
```
🔥 DEAL ALERT 🔥

📦 Product Title

💰 Prezzo: £X.XX
~~£Y.YY~~

🎯 Sconto: -50%
💾 ASIN: B0DS63GM2Z

🛒 [ACQUISTA ORA](link)
```

### After:
```
🔥 DEAL ALERT 🔥

📦 Product Title

💰 Prezzo: £X.XX
~~£Y.YY~~

🎯 Sconto: -50%
💾 ASIN: B0DS63GM2Z

[Buttons Below]
```

## Technical Details

### Worker (worker_uk_v2.py)
- `build_sharing_buttons()`: Creates inline keyboard with 5 buttons
- `post_deal()`: Sends photo with caption and buttons
- `parse_message()`: Now accepts optional photo_url parameter

### Coordinator (main.py)
- `build_sharing_buttons()`: Same button layout for consistency
- `post_deal()`: Sends photo with caption and buttons
- Handles both image and text-only fallback

## Sharing URLs

### WhatsApp
```
https://wa.me/?text=ENCODED_TEXT
```

### Facebook
```
https://www.facebook.com/sharer/sharer.php?u=ENCODED_URL
```

### Twitter
```
https://twitter.com/intent/tweet?text=ENCODED_TEXT&url=ENCODED_URL
```

### Telegram
```
https://t.me/share/url?url=ENCODED_URL&text=ENCODED_TEXT
```

## Testing

Once deployed, deals will appear with:
1. Product image (if available)
2. Deal information (price, discount, ASIN)
3. 5 interactive buttons for action and sharing

Click any button to:
- Buy on Amazon (with affiliate tag)
- Share on social media
- Share via messaging apps

## Files Modified

✅ `workers/uk/worker_uk_v2.py` - Added image support and buttons
✅ `coordinator/main.py` - Added image support and buttons
✅ `requirements.txt` - Already has python-telegram-bot with InlineKeyboardMarkup

## Next Steps

1. Push changes to GitHub:
   ```bash
   git add workers/uk/worker_uk_v2.py coordinator/main.py
   git commit -m "feat: Add image support and social sharing buttons"
   git push
   ```

2. Rebuild on Northflk
3. Test by checking @DealScoutUKBot for deals with buttons

---

**Status**: Ready for deployment ✅
