class DuplicateDocumentError(Exception):
    def __init__(self, checksum: str) -> None:
        self.checksum = checksum
        super().__init__(f"Document with checksum {checksum} already exists")
