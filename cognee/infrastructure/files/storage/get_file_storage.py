import os

from cognee.base_config import get_base_config

from .StorageManager import StorageManager


def get_file_storage(storage_path: str) -> StorageManager:
    # Cache StorageManager instances per storage_path to avoid redundant creation
    manager = _storage_managers.get(storage_path)
    if manager is not None:
        return manager

    base_config = get_base_config()
    is_s3_path = storage_path.startswith("s3://")
    env_storage_backend = os.getenv("STORAGE_BACKEND")
    config_has_s3 = (
        "s3://" in base_config.system_root_directory and "s3://" in base_config.data_root_directory
    )
    use_s3 = is_s3_path or (env_storage_backend == "s3" and config_has_s3)

    if use_s3:
        # Import only once for S3 backend
        from cognee.infrastructure.files.storage.S3FileStorage import S3FileStorage

        backend = S3FileStorage(storage_path)
    else:
        # Import only once for Local backend
        from cognee.infrastructure.files.storage.LocalFileStorage import LocalFileStorage

        backend = LocalFileStorage(storage_path)

    manager = StorageManager(backend)
    _storage_managers[storage_path] = manager
    return manager
