import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "dev"
    api_key: str = "changeme-supersecret"
    db_url: str = "sqlite:///./inventory.db"
    tz: str = os.getenv("APP_TIMEZONE", "America/Los_Angeles")
    
    use_paddle_ocr: bool = True
    staging_bins: str = "S-01,S-02,S-03,S-04"
    staging_threshold_hours: int = 12
    
    storage_backend: str = "local"
    storage_local_dir: str = "./storage"
    s3_endpoint: str = ""
    s3_bucket: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    
    class Config:
        env_file = ".env"
    
    @property
    def staging_bins_list(self) -> List[str]:
        return [bin_id.strip() for bin_id in self.staging_bins.split(",")]


settings = Settings()