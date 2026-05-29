# 🚀 READY TO TEST ON PHONE - CHECKLIST

## ✅ What's Done
- [x] NCBA code synced from production
- [x] All endpoints configured
- [x] Swagger tested and working
- [x] Phone number handling verified

## ⚠️ What's Remaining (2 Steps)

### Step 1: Add Environment Variables (1 min)
```bash
cd /home/fagitone/Documents/GitHub/fagierrands-dev-backend

# Add NCBA credentials
export NCBA_USERNAME="Errand@123"
export NCBA_PASSWORD="9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL"
export NCBA_TILL_NO="852054"
```

### Step 2: Start Server (30 sec)
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 📱 Then Test on Phone

### Option A: Local Network
1. Get your computer's IP: `hostname -I`
2. In phone app, use: `http://YOUR_IP:8000`

### Option B: Deploy to Server
1. Push to production server
2. Use production URL in app

---

## 🧪 Quick Verification

Before testing on phone, verify locally:
```bash
python verify_ncba.py
```

Should show:
```
✅ All checks passed!
✅ NCBA Payment System is fully configured and operational!
```

---

## 🎯 What Will Work on Phone

Once server is running with env vars:
- ✅ Login/Register
- ✅ Create orders
- ✅ Initiate NCBA payment
- ✅ Receive STK push
- ✅ Complete payment
- ✅ Track order status

---

## ⏱️ Time Needed

- Add env vars: **1 minute**
- Start server: **30 seconds**
- Test on phone: **2 minutes**

**Total: ~4 minutes to be fully operational!**

---

## 🚨 If Issues

### Server won't start:
```bash
# Check if port is in use
lsof -i :8000
# Kill if needed
kill -9 <PID>
```

### Can't connect from phone:
```bash
# Check firewall
sudo ufw allow 8000
```

### NCBA not working:
```bash
# Verify env vars are set
echo $NCBA_USERNAME
echo $NCBA_TILL_NO
```

---

**Ready? Run the 2 commands above and you're live!** 🚀
