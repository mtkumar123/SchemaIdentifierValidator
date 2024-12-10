class BaseException(Exception): ...


class FileTooLargeException(Exception):
    message = "File size is too large."


class InvalidFileException(Exception):
    message = "Invalid file."


class FileNotFoundException(Exception):
    message = "File not found."


class SchemaNotFoundException(Exception):
    message = "Schema not found."
