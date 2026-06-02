class ExcelImportException(Exception):
    """Custom Exception chuyên dùng để gom và trả về cấu trúc JSON lỗi Excel"""
    def __init__(self, error_details: list):
        self.error_details = error_details
        super().__init__("Import Excel thất bại do chứa dữ liệu không hợp lệ.")