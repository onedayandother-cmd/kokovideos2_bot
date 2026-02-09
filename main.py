import os
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# --- بياناتك الشخصية المكتملة ---
API_ID = 20209272
API_HASH = "08361988c289fcbb31a417c32701edf8"
BOT_TOKEN = "8281075910:AAEQB35hgCaSBWSz949AdTJXT4EtjehIqsU"
# ----------------------------

app = Client("kokovideos2_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "✅ أهلاً بك في بوت kokovideos2_bot!\n\n"
        "أرسل لي الآن رابط فيديو أو بلاي لست كاملة من:\n"
        "(YouTube, Facebook, Instagram, TikTok)\n\n"
        "🚀 سأقوم بالتحميل والرفع لك حتى حجم 2 جيجا."
    )

@app.on_message(filters.text & ~filters.command("start"))
async def downloader(client, message):
    url = message.text
    if not url.startswith("http"):
        return await message.reply_text("❌ من فضلك أرسل رابطاً صحيحاً يبدأ بـ http")

    status_msg = await message.reply_text("⏳ جاري سحب البيانات وفحص الحجم... انتظر قليلاً")
    
    try:
        # إعدادات التحميل لضمان أعلى جودة وأفضل صيغة mp4
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': False,  # لدعم تحميل البلاي لست كاملة
            'quiet': True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # التحقق إذا كان الرابط بلاي لست أم فيديو واحد
            if 'entries' in info:
                videos = info['entries']
            else:
                videos = [info]
            
            for video in videos:
                if video is None: continue
                file_path = ydl.prepare_filename(video)
                
                if os.path.exists(file_path):
                    await status_msg.edit(f"📤 جاري رفع: {video.get('title', 'Video')}")
                    
                    # رفع الفيديو باستخدام بروتوكول تليجرام السريع
                    await client.send_video(
                        chat_id=message.chat.id,
                        video=file_path,
                        caption=f"✅ تم التحميل: {video.get('title', 'Video')}",
                        supports_streaming=True
                    )
                    
                    # حذف الملف من السيرفر بعد الرفع لتوفير المساحة
                    os.remove(file_path)

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit(f"❌ حدث خطأ: {str(e)}")
        # تنظيف أي ملفات متبقية في حال حدوث خطأ
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

app.run()
