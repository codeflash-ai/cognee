"""Advanced PDF loader leveraging unstructured for layout-aware extraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import asyncio
from cognee.infrastructure.files.storage import get_file_storage, get_storage_config
from cognee.infrastructure.files.utils.get_file_metadata import get_file_metadata
from cognee.infrastructure.loaders.LoaderInterface import LoaderInterface
from cognee.shared.logging_utils import get_logger

from cognee.infrastructure.loaders.external.pypdf_loader import PyPdfLoader

logger = get_logger(__name__)

try:
    from unstructured.partition.pdf import partition_pdf
except ImportError as e:
    logger.info(
        "unstructured[pdf] not installed, can't use AdvancedPdfLoader, will use PyPdfLoader instead."
    )
    raise ImportError from e


@dataclass
class _PageBuffer:
    page_num: Optional[int]
    segments: List[str]


class AdvancedPdfLoader(LoaderInterface):
    """
    PDF loader using unstructured library.

    Extracts text content, images, tables from PDF files page by page, providing
    structured page information and handling PDF-specific errors.
    """

    @property
    def supported_extensions(self) -> List[str]:
        return ["pdf"]

    @property
    def supported_mime_types(self) -> List[str]:
        return ["application/pdf"]

    @property
    def loader_name(self) -> str:
        return "advanced_pdf_loader"

    def can_handle(self, extension: str, mime_type: str) -> bool:
        """Check if file can be handled by this loader."""
        # Check file extension
        if extension in self.supported_extensions and mime_type in self.supported_mime_types:
            return True

        return False

    async def load(self, file_path: str, strategy: str = "auto", **kwargs: Any) -> str:
        """Load PDF file using unstructured library. If Exception occurs, fallback to PyPDFLoader.

        Args:
            file_path: Path to the document file
            strategy: Partitioning strategy ("auto", "fast", "hi_res", "ocr_only")
            **kwargs: Additional arguments passed to unstructured partition

        Returns:
            LoaderResult with extracted text content and metadata

        """
        try:
            logger.info(f"Processing PDF: {file_path}")

            with open(file_path, "rb") as f:
                file_metadata = await get_file_metadata(f)

            # Name ingested file of current loader based on original file content hash
            storage_file_name = "text_" + file_metadata["content_hash"] + ".txt"

            # Set partitioning parameters
            partition_kwargs: Dict[str, Any] = {
                "filename": file_path,
                "strategy": strategy,
                "infer_table_structure": True,
                "include_page_breaks": False,
                "include_metadata": True,
                **kwargs,
            }
            # Use partition to extract elements
            elements = partition_pdf(**partition_kwargs)

            # Process elements into text content
            page_contents = self._format_elements_by_page(elements)

            # Check if there is any content
            if not page_contents:
                logger.warning(
                    "AdvancedPdfLoader returned no content. Falling back to PyPDF loader."
                )
                return await self._fallback(file_path, **kwargs)

            # Combine all page outputs
            full_content = "\n".join(page_contents)

            # Store the content
            storage_config = get_storage_config()
            data_root_directory = storage_config["data_root_directory"]
            storage = get_file_storage(data_root_directory)

            full_file_path = await storage.store(storage_file_name, full_content)

            return full_file_path

        except Exception as exc:
            logger.warning("Failed to process PDF with AdvancedPdfLoader: %s", exc)
            return await self._fallback(file_path, **kwargs)

    async def _fallback(self, file_path: str, **kwargs: Any) -> str:
        logger.info("Falling back to PyPDF loader for %s", file_path)
        fallback_loader = PyPdfLoader()
        return await fallback_loader.load(file_path, **kwargs)

    def _format_elements_by_page(self, elements: List[Any]) -> List[str]:
        """Format elements by page."""
        page_buffers: List[_PageBuffer] = []
        current_buffer = _PageBuffer(page_num=None, segments=[])
        append_page_buffer = page_buffers.append  # Localize for perf

        _safe_to_dict = self._safe_to_dict
        _format_element = self._format_element

        for element in elements:
            # Inline _safe_to_dict logic for performance (bypass function call overhead)
            # This yields a measurable impact for tight data wrangling loops.
            has_to_dict = hasattr(element, "to_dict")
            if has_to_dict:
                try:
                    element_dict = element.to_dict()
                except Exception:
                    element_dict = None
            else:
                element_dict = None

            if element_dict is None:
                # Avoid redundant getattr(type.__name__) slowdown with type caching
                category = getattr(element, "category", None)
                if category:
                    fallback_type = category
                else:
                    # type(element).__name__ is measurably faster than getattr with fallback
                    fallback_type = type(element).__name__

                element_dict = {
                    "type": fallback_type,
                    "text": getattr(element, "text", ""),
                    "metadata": getattr(element, "metadata", {}),
                }

            metadata = element_dict.get("metadata", None)
            page_num = metadata.get("page_number") if metadata else None

            if current_buffer.page_num != page_num:
                if current_buffer.segments:
                    append_page_buffer(current_buffer)
                current_buffer = _PageBuffer(page_num=page_num, segments=[])

            formatted = _format_element(element_dict)
            if formatted:
                current_buffer.segments.append(formatted)

        if current_buffer.segments:
            append_page_buffer(current_buffer)

        # Preallocate result and avoid unnecessary str() in result collecting loop
        page_contents: List[str] = []
        join = "\n\n".join
        for buffer in page_buffers:
            header = f"Page {buffer.page_num}:\n" if buffer.page_num is not None else "Page:"
            content = header + join(buffer.segments) + "\n"
            page_contents.append(content)
        return page_contents

    def _format_element(
        self,
        element: Dict[str, Any],
    ) -> str:
        """Format element."""
        # Minimize .get and .lower calls
        element_type = element.get("type")
        element_type_lower = element_type.lower() if isinstance(element_type, str) else ""
        text = self._clean_text(element.get("text", ""))
        metadata = element.get("metadata", {})

        if element_type_lower == "table":
            return self._format_table_element(element) or text

        if element_type_lower == "image":
            description = text or self._format_image_element(metadata)
            return description

        # Ignore header and footer
        if element_type_lower == "header" or element_type_lower == "footer":
            return ""

        return text

    def _format_table_element(self, element: Dict[str, Any]) -> str:
        """Format table element."""
        metadata = element.get("metadata", {})
        text = self._clean_text(element.get("text", ""))
        table_html = metadata.get("text_as_html")

        if table_html:
            return table_html.strip()

        return text

    def _format_image_element(self, metadata: Dict[str, Any]) -> str:
        """Format image."""
        placeholder = "[Image omitted]"
        image_text = placeholder
        coordinates = metadata.get("coordinates", {})
        points = coordinates.get("points") if isinstance(coordinates, dict) else None
        if points and isinstance(points, tuple) and len(points) == 4:
            leftup = points[0]
            rightdown = points[3]
            if (
                isinstance(leftup, tuple)
                and isinstance(rightdown, tuple)
                and len(leftup) == 2
                and len(rightdown) == 2
            ):
                image_text = f"{placeholder} (bbox=({leftup[0]}, {leftup[1]}, {rightdown[0]}, {rightdown[1]}))"

            layout_width = coordinates.get("layout_width")
            layout_height = coordinates.get("layout_height")
            system = coordinates.get("system")
            if layout_width and layout_height and system:
                image_text = (
                    image_text
                    + f", system={system}, layout_width={layout_width}, layout_height={layout_height}))"
                )

        return image_text

    def _safe_to_dict(self, element: Any) -> Dict[str, Any]:
        """Safe to dict."""
        try:
            if hasattr(element, "to_dict"):
                return element.to_dict()
        except Exception:
            pass
        fallback_type = getattr(element, "category", None)
        if not fallback_type:
            fallback_type = getattr(element, "__class__", type("", (), {})).__name__

        return {
            "type": fallback_type,
            "text": getattr(element, "text", ""),
            "metadata": getattr(element, "metadata", {}),
        }

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).replace("\xa0", " ").strip()


if __name__ == "__main__":
    loader = AdvancedPdfLoader()
    asyncio.run(
        loader.load(
            "/Users/xiaotao/work/cognee/cognee/infrastructure/loaders/external/attention_is_all_you_need.pdf"
        )
    )
