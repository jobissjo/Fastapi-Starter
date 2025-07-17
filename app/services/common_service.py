import aiofiles
import base64
import uuid
from pathlib import Path
from app.core.settings import setting
from app.utils.common import CustomException


class CommonService:

    @staticmethod
    def generate_secure_filename(original_name: str) -> str:
        """
        Appends a short UUID to avoid overwriting existing files.
        """
        path = Path(original_name)
        unique_suffix = uuid.uuid4().hex[:8]
        return f"{path.stem}_{unique_suffix}{path.suffix}"
    
    
    @staticmethod
    async def save_base64_file(
        base64_str: str,
        folder: str,
        media_root: str =setting.MEDIA_ROOT
    ) -> str:
        """
        Save a base64-encoded file to the specified folder and filename.
        If file exists, generates a new unique filename.
        """

        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
            header, encoded = base64_str.split(",", 1)
            mime_type = header.split(";")[0].split(":")[1]
            extension = mime_type.split("/")[1]
            filename = f"{uuid.uuid4().hex}.{extension}"
        else:
            filename = f"{uuid.uuid4().hex}.png"


        # Ensure folder exists
        folder_path = Path(media_root) / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        

        # Create full path
        file_path = folder_path / filename

        # Secure name if file exists
        if file_path.exists():
            filename = CommonService.generate_secure_filename(filename)
            file_path = folder_path / filename

        try:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(base64.b64decode(base64_str))
            return str(file_path)
        except Exception as e:
            raise CustomException(f"Failed to save file: {e}", status_code=500)
