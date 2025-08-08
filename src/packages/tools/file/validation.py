import os


class FileValidator:
    """Validation for file and directory existence and permissions."""

    @staticmethod
    def file_exists(filepath: str) -> bool:
        """Check if file exists."""
        return os.path.isfile(filepath)

    @staticmethod
    def dir_exists(directory: str) -> bool:
        """Check if directory exists."""
        return os.path.isdir(directory)

    @staticmethod
    def has_read_permission(filepath: str) -> bool:
        """Check if file is readable."""
        return os.access(filepath, os.R_OK)

    @staticmethod
    def has_write_permission(filepath: str) -> bool:
        """Check if file is writable."""
        return os.access(filepath, os.W_OK)
