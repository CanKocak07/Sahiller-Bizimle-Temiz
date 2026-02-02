"""
Earth Engine configuration and initialization.

Bu dosya:
- Google Earth Engine bağlantısını başlatır
- Projedeki tüm uydu servisleri bu dosyayı kullanır
- Authentication detaylarını tek bir yerde toplar
"""

import ee
import os


_DEFAULT_EE_PROJECT = "sahiller-bizimle-temiz-481410"


def initialize_earth_engine():
    """
    Google Earth Engine'i initialize eder.

    Local geliştirmede:
    - ee.Authenticate() daha önce yapılmış olmalı
    - credentials.json local makinede bulunur

    Sunucu ortamında:
    - Service Account veya ortam değişkeni kullanılabilir
    """

    project = (os.getenv("EE_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or _DEFAULT_EE_PROJECT).strip()

    try:
        # Eğer EE zaten initialize edildiyse hata vermez
        ee.Initialize(project=project)
        print(f"Earth Engine initialized successfully (project={project}).")
    except Exception as e:
        print("Earth Engine initialization failed.")
        print("Project:", project)
        print("Error:", e)
        raise
