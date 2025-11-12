import os
import yt_dlp
import shutil

def download_playlist(url, output_dir="1_raw_videos"):
    os.makedirs(output_dir, exist_ok=True)

    node_path = shutil.which("node")
    if not node_path:
        print("⚠️ Node.js не найден. Установи его или добавь в PATH.")
        return
    print(f"🟢 Используется Node.js: {node_path}")

    # Настройки для yt-dlp (без cookies — они будут подставляться перед каждым видео)
    base_opts = {
        "outtmpl": f"{output_dir}/%(playlist_title)s/%(title)s.%(ext)s",
        "ignoreerrors": True,
        "noplaylist": False,
        "progress_hooks": [hook],
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "extractor_args": {
            "youtube": ["player_client=web", "ejs_sandbox=nodejs"]
        },
    }

    # Создаем объект yt-dlp для получения списка видео
    with yt_dlp.YoutubeDL({"extract_flat": True, "quiet": True}) as ydl:
        playlist_info = ydl.extract_info(url, download=False)
        entries = playlist_info.get("entries", [])
        print(f"📋 Найдено видео: {len(entries)}")

        for index, entry in enumerate(entries, start=1):
            video_url = entry.get("url")
            title = sanitize_filename(entry.get("title", f"video_{index}"))

            # Путь к файлу
            video_path = os.path.join(output_dir, playlist_info.get("title", "Playlist"), f"{title}.mp4")

            # Проверка — если файл уже скачан
            if os.path.exists(video_path):
                print(f"⏩ Пропущено (уже скачано): {title}")
                continue

            print(f"\n🎬 [{index}/{len(entries)}] Скачивание: {title}")

            # Обновляем cookies из браузера перед каждым видео
            ydl_opts = base_opts.copy()
            ydl_opts["cookiesfrombrowser"] = ("chrome", None, None, None)

            # Скачиваем конкретное видео
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            except Exception as e:
                print(f"❌ Ошибка при скачивании {title}: {e}")

def sanitize_filename(name: str) -> str:
    """Удаляет недопустимые символы из имени файла"""
    return "".join(c for c in name if c.isalnum() or c in " .-_").rstrip()

def hook(d):
    if d["status"] == "downloading":
        print(f"⬇️  {d['filename']} — {d['_percent_str']} ({d['_speed_str']})", end="\r")
    elif d["status"] == "finished":
        print(f"\n✅  Скачано: {d['filename']}")

if __name__ == "__main__":
    url = input("Введите ссылку на плейлист или видео: ").strip()
    download_playlist(url)
