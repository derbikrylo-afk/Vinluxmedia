"""
VINLUX Media Engine
Проверка наличия медиакомплекта.

Следующий этап: подключение Google Drive API и автоматическая загрузка.
"""

MAIN_COUNT = 24
COMMON_COUNT = 12


def validate_media(main_files, common_files, video_exists):
    return {
        "main": len(main_files) == MAIN_COUNT,
        "common": len(common_files) == COMMON_COUNT,
        "video": video_exists
    }

