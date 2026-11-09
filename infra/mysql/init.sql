
CREATE DATABASE IF NOT EXISTS video_upload_db;
CREATE DATABASE IF NOT EXISTS video_metadata_db;
CREATE DATABASE IF NOT EXISTS video_jobs_db;
CREATE DATABASE IF NOT EXISTS video_worker_db;
CREATE DATABASE IF NOT EXISTS video_thumbnail_db;

GRANT ALL PRIVILEGES ON video_upload_db.* TO 'video_user'@'%';
GRANT ALL PRIVILEGES ON video_metadata_db.* TO 'video_user'@'%';
GRANT ALL PRIVILEGES ON video_jobs_db.* TO 'video_user'@'%';
GRANT ALL PRIVILEGES ON video_worker_db.* TO 'video_user'@'%';
GRANT ALL PRIVILEGES ON video_thumbnail_db.* TO 'video_user'@'%';

FLUSH PRIVILEGES;
