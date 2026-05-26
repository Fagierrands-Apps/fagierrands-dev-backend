# Image Storage Configuration Status

**Date**: 2026-05-26

## ✅ Changes Committed

```
commit ff7c989
Add order status polling endpoint and unify registration flow

- Added GET /api/orders/{order_id}/status/ for status polling
- Returns rider details when order status is 'assigned'
- Removed separate rider document upload endpoint
- All users (client/rider/handler) use unified /api/accounts/register/
- Riders verified through existing assistant verification system
- No breaking changes to registration flow
```

---

## 📦 Image Storage Configuration

### Current Setup

**Order Images (Errand Placement)**:
- **Storage**: Local filesystem (`MEDIA_ROOT`)
- **Model**: `OrderImage` in `orders/models.py`
- **Upload Path**: `order_images/`
- **Endpoint**: `POST /api/orders/{order_id}/images/`
- **Status**: ✅ **Working** (uses Django's default ImageField)

**Assistant Verification Documents**:
- **Storage**: Supabase Storage
- **Bucket**: `user-uploads`
- **Client**: Configured with service role key
- **Status**: ✅ **Configured**

### Configuration Details

#### 1. Order Images (Local Storage)
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# models.py
class OrderImage(models.Model):
    image = models.ImageField(upload_to='order_images/')
```

**How it works**:
- Images uploaded via `POST /api/orders/{order_id}/images/`
- Stored in `/media/order_images/` directory
- Accessible via `/media/order_images/{filename}`
- Serializer returns full URL via `image_url` field

#### 2. Supabase Storage (Verification Docs)
```python
# .env
SUPABASE_URL=https://lmwloxheulmybtrnfobz.supabase.co
SUPABASE_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>

# supabase_client.py
VERIFICATION_BUCKET = 'user-uploads'
admin_supabase = create_client(supabase_url, service_role_key)
```

**How it works**:
- Used for assistant/rider verification documents
- Uploads via `admin_supabase.storage.from_(bucket).upload()`
- Returns public URL for stored files

---

## ⚠️ Important Notes

### Order Image Upload - Current Behavior

**✅ Working**:
- Order images upload to local filesystem
- Images accessible via Django's media serving
- Serializer returns full URLs

**⚠️ Production Consideration**:
For production deployment, you may want to:
1. Use Supabase Storage for order images (scalable, CDN)
2. Use Cloudinary (mentioned in OrderAttachment model comments)
3. Use AWS S3

**Current setup is fine for**:
- Development
- Small-scale production
- Single-server deployments

### To Switch to Supabase for Order Images

If you want order images in Supabase instead of local storage:

```python
# In OrderImageUploadView.perform_create()
from accounts.supabase_client import admin_supabase

def perform_create(self, serializer):
    order_id = self.kwargs.get('order_id')
    order = Order.objects.get(id=order_id)
    
    # Upload to Supabase
    image = self.request.FILES['image']
    filename = f"order_images/{order_id}/{image.name}"
    
    admin_supabase.storage.from_('user-uploads').upload(
        filename,
        image.read(),
        {"content-type": image.content_type}
    )
    
    url = admin_supabase.storage.from_('user-uploads').get_public_url(filename)
    
    # Save URL instead of file
    serializer.save(order=order, image_url=url)
```

---

## 🧪 Testing Order Image Upload

### Test Endpoint
```bash
# Upload order image
curl -X POST http://localhost:8000/api/orders/123/images/ \
  -H "Authorization: Bearer <token>" \
  -F "image=@photo.jpg" \
  -F "description=Delivery location" \
  -F "stage=before" \
  -F "image_type=generic"

# Get order images
curl -X GET http://localhost:8000/api/orders/123/images/ \
  -H "Authorization: Bearer <token>"
```

### Expected Response
```json
{
  "id": 1,
  "image": "/media/order_images/photo.jpg",
  "image_url": "http://localhost:8000/media/order_images/photo.jpg",
  "description": "Delivery location",
  "stage": "before",
  "uploaded_at": "2026-05-26T20:30:00Z"
}
```

---

## ✅ Summary

| Feature | Storage | Status | Notes |
|---------|---------|--------|-------|
| Order Images | Local Filesystem | ✅ Working | Fine for dev/small prod |
| Verification Docs | Supabase | ✅ Configured | Using service role key |
| Order Attachments | Cloudinary (planned) | ⏳ Not implemented | See OrderAttachment model |

**Recommendation**: Current setup works. For production scale, consider migrating order images to Supabase or S3.

---

**Built with ❤️ for FagiErrands**
