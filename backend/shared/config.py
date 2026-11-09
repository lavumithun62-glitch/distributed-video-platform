from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Distributed Video Processing Platform"
    environment: str = "development"
    secret_key: str = "development-secret"

    # MySQL settings
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "video_user"
    mysql_password: str = "video_password"

    # Separate service databases
    upload_database: str = "video_upload_db"
    metadata_database: str = "video_metadata_db"
    orchestrator_database: str = "video_jobs_db"
    worker_database: str = "video_worker_db"
    thumbnail_database: str = "video_thumbnail_db"

    # RabbitMQ settings
    rabbitmq_url: str = (
        "amqp://video_user:video_password@localhost:5672/"
    )

    # Redis settings
    redis_url: str = "redis://localhost:6379/0"

    # Storage directories
    upload_dir: str = "storage/uploads"
    processed_dir: str = "storage/processed"
    thumbnail_dir: str = "storage/thumbnails"

    # Upload validation
    max_upload_size_mb: int = 500
    allowed_video_extensions: str = ".mp4,.mov,.avi,.mkv,.webm"

    # Transcoding settings
    video_resolutions: str = "360p,720p,1080p"
    max_retries: int = 3

    # Microservice ports
    gateway_port: int = 8000
    upload_service_port: int = 8001
    metadata_service_port: int = 8002
    orchestrator_service_port: int = 8003
    thumbnail_service_port: int = 8004
    delivery_service_port: int = 8005

    # Environment configuration
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_extensions(self) -> set[str]:
        return {
            extension.strip().lower()
            for extension in self.allowed_video_extensions.split(",")
        }

    @property
    def upload_path(self) -> Path:
        return ROOT_DIR / self.upload_dir

    @property
    def processed_path(self) -> Path:
        return ROOT_DIR / self.processed_dir

    @property
    def thumbnail_path(self) -> Path:
        return ROOT_DIR / self.thumbnail_dir


settings = Settings()