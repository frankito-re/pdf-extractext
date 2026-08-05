# Única responsabilidad: transportar el checksum duplicado hacia quien la capture
# (SOLID: SRP). presentation/main.py la traduce a HTTP 409 sin que checksum.py
# conozca nada de HTTP.
class DuplicateDocumentError(Exception):
    def __init__(self, checksum: str) -> None:
        self.checksum = checksum
        super().__init__(f"Document with checksum {checksum} already exists")
