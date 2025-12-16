"""
Earth Engine configuration and initialization.

Bu dosya:
- Google Earth Engine bağlantısını başlatır
- Projedeki tüm uydu servisleri bu dosyayı kullanır
- Authentication detaylarını tek bir yerde toplar
"""

import ee
import os


def initialize_earth_engine():
    """
    Google Earth Engine'i initialize eder.

    Local geliştirmede:
    - ee.Authenticate() daha önce yapılmış olmalı
    - credentials.json local makinede bulunur

    Sunucu ortamında:
    - Service Account veya ortam değişkeni kullanılabilir
    """

    try:
        # Eğer EE zaten initialize edildiyse hata vermez
        ee.Initialize(project="sahiller-bizimle-temiz-481410")
        print("Earth Engine initialized successfully.")

    except Exception as e:
        print("Earth Engine initialization failed.")
        print("Error:", e)
        raise e
